from __future__ import annotations

import os
import re
import textwrap
from dataclasses import dataclass
from typing import List, Protocol, Tuple, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

XAI_API_URL = "https://api.x.ai/v1/chat/completions"


@dataclass
class AgentResponse:
    message: str
    code: str


class ChatAgent(Protocol):
    def chat(self, user_input: str, history: List[Tuple[str, str]]) -> AgentResponse:  # pragma: no cover - protocol
        ...


def extract_code_from_markdown(text: str) -> Tuple[str, str]:
    """Extract first python fenced block and return (code, remainder_message)."""
    code_block_re = re.compile(r"```python\n([\s\S]*?)\n```", re.IGNORECASE)
    match = code_block_re.search(text)
    if not match:
        return "", text
    code = match.group(1).strip()
    remainder = text[: match.start()] + text[match.end() :]
    return code, remainder.strip()


DEFAULT_SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert Polymarket trading bot generator. Output clean Python code ONLY when appropriate, wrapped in a single fenced code block like:
    ```python
    # code
    ```

    Constraints:
    - Use only safe libraries available: requests, time, json, os, dotenv, websocket-client (if needed), web3 (placeholder), pandas (optional).
    - Import helpers from local api_helpers: fetch_markets, place_order.
    - Respect a DRY_RUN boolean from env or caller to avoid real trades.
    - Add basic error handling and clear prints for logs.

    Polymarket APIs quick reference:
    - Gamma REST: https://gamma-api.polymarket.com (markets, prices, volumes)
    - CLOB Orders: https://clob.polymarket.com (REST/WebSocket). In MVP, do NOT place real orders; call place_order(..., dry_run=True).
    """
)


class GrokAgent:
    def __init__(self, api_key: str | None = None, model: str = "grok-3", system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.api_key = api_key or os.getenv("XAI_API_KEY", "")
        self.model = model
        self.system_prompt = system_prompt

    def chat(self, user_input: str, history: List[Tuple[str, str]]) -> AgentResponse:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        for human, assistant in history:
            if human:
                messages.append({"role": "user", "content": human})
            if assistant:
                messages.append({"role": "assistant", "content": assistant})
        messages.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2000,
        }

        try:
            resp = requests.post(XAI_API_URL, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            code, remainder = extract_code_from_markdown(content)
            if not code:
                code = self._fallback_code()
            msg = remainder if remainder else "Generated code ready to review and execute."
            return AgentResponse(message=msg, code=code)
        except Exception:
            return AgentResponse(
                message=(
                    "I could not reach the AI service. Here's a safe example that lists markets."
                ),
                code=self._fallback_code(),
            )

    @staticmethod
    def _fallback_code() -> str:
        return textwrap.dedent(
            """
            import os
            from api_helpers import fetch_markets, place_order

            DRY_RUN = os.getenv("DRY_RUN", "1") == "1"

            def main():
                data = fetch_markets(limit=5)
                markets = data.get("markets") or data
                print(f"Fetched {len(markets)} markets (showing up to 5):")
                for m in markets[:5]:
                    print(f"- {m.get('question') or m.get('slug')}")

            if __name__ == "__main__":
                main()
            """
        ).strip()
