import os
import re
import sys
import tempfile
import textwrap
import threading
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import requests
from dotenv import load_dotenv

# Ensure local imports work when executing generated code in a temp dir
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_API_URL = "https://api.x.ai/v1/chat/completions"

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert Polymarket trading bot generator. Output clean Python code ONLY when appropriate, wrapped in a single fenced code block like:
    ```python
    # code
    ```

    Constraints and safety rules:
    - Use only safe libraries available: requests, time, json, os, dotenv, websocket-client (if needed), web3 (placeholder), pandas (optional).
    - Import helpers from local api_helpers: fetch_markets, place_order.
    - Respect a DRY_RUN boolean from env or caller to avoid real trades.
    - Never use dangerous calls: eval, exec, compile, __import__, subprocess, os.system, shutil.rmtree, fork/daemonize, file writes outside CWD.
    - Do not read environment variables other than explicitly needed (e.g., DRY_RUN).
    - Add basic error handling and clear prints for logs.

    Polymarket APIs quick reference:
    - Gamma REST: https://gamma-api.polymarket.com (markets, prices, volumes)
    - CLOB Orders: https://clob.polymarket.com (REST/WebSocket). In MVP, do NOT place real orders; call place_order(..., dry_run=True).
    """
)

# --- Agent integration ---

def extract_code_from_markdown(text: str) -> Tuple[str, str]:
    """Extract first python fenced block and return (code, remainder_message)."""
    code_block_re = re.compile(r"```python\n([\s\S]*?)\n```", re.IGNORECASE)
    match = code_block_re.search(text)
    if not match:
        return "", text
    code = match.group(1).strip()
    # Remove the code block from message
    remainder = text[: match.start()] + text[match.end() :]
    return code, remainder.strip()


def agent_response(user_input: str, history: List[Tuple[str, str]]) -> Tuple[str, str]:
    """Call xAI Grok API and return (assistant_message, code_str)."""
    headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for human, assistant in history:
        if human:
            messages.append({"role": "user", "content": human})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": "grok-3",  # or grok-4 if available
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2000,
    }

    try:
        resp = requests.post(XAI_API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"xAI API error {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        # Expected shape similar to OpenAI
        content = data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        fallback = (
            "I could not reach the AI service. Here's a safe example that lists markets."
        )
        code = textwrap.dedent(
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
        return fallback, code

    code, remainder = extract_code_from_markdown(content)
    if not code:
        # No code block found; provide minimal stub
        code = textwrap.dedent(
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
    assistant_message = remainder if remainder else "Generated code ready to review and execute."
    return assistant_message, code


# --- Execution ---

def audit_generated_code(code: str) -> List[str]:
    """Scan generated code for obviously dangerous patterns.

    Returns a list of issues; empty list means acceptable.
    """
    issues: List[str] = []
    forbidden_patterns = [
        r"\beval\b",
        r"\bexec\b",
        r"\bcompile\b",
        r"\b__import__\b",
        r"subprocess\.",
        r"os\.system\(",
        r"shutil\.rmtree",
        r"rm -rf",
        r"open\(.*?/etc/",
        r"\/dev\/",
    ]
    for pat in forbidden_patterns:
        if re.search(pat, code):
            issues.append(f"Forbidden pattern detected: {pat}")

    # Allowlist imports; warn on unknown imports
    allowed_imports = {
        "requests",
        "time",
        "json",
        "os",
        "dotenv",
        "websocket",
        "websocket_client",
        "web3",
        "pandas",
        "api_helpers",
    }
    for match in re.finditer(r"^\s*import\s+([a-zA-Z0-9_\.]+)", code, flags=re.MULTILINE):
        module = match.group(1).split(".")[0]
        if module not in allowed_imports:
            issues.append(f"Unexpected import: {module}")
    for match in re.finditer(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+", code, flags=re.MULTILINE):
        module = match.group(1).split(".")[0]
        if module not in allowed_imports:
            issues.append(f"Unexpected import: {module}")

    return issues


def execute_code(code: str, dry_run: bool = True, timeout_s: int = 30) -> str:
    os.environ["DRY_RUN"] = "1" if dry_run else "0"
    # Ensure local imports work
    env = os.environ.copy()
    python_executable = sys.executable

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "generated_bot.py")
        # Write code
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        # Execute in subprocess
        try:
            proc = __import__("subprocess").run(
                [python_executable, script_path],
                cwd=CURRENT_DIR,  # so relative imports find api_helpers
                capture_output=True,
                text=True,
                timeout=timeout_s,
                env=env,
            )
            stdout = proc.stdout
            stderr = proc.stderr
            if proc.returncode != 0:
                return f"[EXIT {proc.returncode}]\nSTDERR:\n{stderr}\n\nSTDOUT:\n{stdout}"
            return stdout or "(no output)"
        except __import__("subprocess").TimeoutExpired:
            return f"Execution timed out after {timeout_s}s"


# Streaming execution support (single-run at a time for simplicity)
CURRENT_PROCESS_LOCK = threading.Lock()
CURRENT_PROCESS: Optional[Any] = None


def execute_code_streaming(code: str, dry_run: bool = True, timeout_s: int = 300):
    """Yield incremental logs while executing code in a subprocess."""
    import subprocess  # local import to avoid at module import time

    # Audit code first
    issues = audit_generated_code(code)
    if issues:
        yield "\n".join(["Execution blocked due to code audit issues:"] + [f"- {i}" for i in issues])
        return

    os.environ["DRY_RUN"] = "1" if dry_run else "0"
    env = os.environ.copy()
    python_executable = sys.executable

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "generated_bot.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        buf: List[str] = []
        try:
            with CURRENT_PROCESS_LOCK:
                global CURRENT_PROCESS
                if CURRENT_PROCESS is not None:
                    yield "Another execution is in progress. Please stop it first."
                    return
                CURRENT_PROCESS = subprocess.Popen(
                    [python_executable, script_path],
                    cwd=CURRENT_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env,
                )

            assert CURRENT_PROCESS is not None
            for line in CURRENT_PROCESS.stdout:  # type: ignore[union-attr]
                buf.append(line.rstrip("\n"))
                yield "\n".join(buf)

            ret = CURRENT_PROCESS.wait(timeout=timeout_s)
            if ret != 0:
                buf.append(f"[EXIT {ret}]")
            yield "\n".join(buf) if buf else "(no output)"
        except subprocess.TimeoutExpired:
            try:
                if CURRENT_PROCESS:
                    CURRENT_PROCESS.kill()
            finally:
                with CURRENT_PROCESS_LOCK:
                    CURRENT_PROCESS = None
            buf.append(f"Execution timed out after {timeout_s}s")
            yield "\n".join(buf)
        finally:
            with CURRENT_PROCESS_LOCK:
                CURRENT_PROCESS = None


# --- UI Wiring ---

def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Polymarket Auto Flows - MVP") as demo:
        gr.Markdown("# Polymarket Auto Flows — MVP\nChat → Code → Execute")
        with gr.Row():
            with gr.Column(scale=5):
                chatbot = gr.Chatbot(height=520, label="Agent")
                user_box = gr.Textbox(placeholder="Describe your bot...", label="Your message")
                with gr.Row():
                    send_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear")
            with gr.Column(scale=5):
                code_view = gr.Code(label="Generated Python Code", language="python", interactive=True)
                with gr.Row():
                    dry_toggle = gr.Checkbox(value=True, label="Dry-run (no live trades)")
                    live_confirm = gr.Checkbox(value=False, label="I understand live trades spend real funds")
                with gr.Row():
                    exec_btn = gr.Button("Execute (stream)", variant="primary")
                    stop_btn = gr.Button("Stop", variant="stop")
                output_box = gr.Textbox(label="Output / Logs", lines=16)

        state_history = gr.State([])  # list of (user, assistant)
        state_code = gr.State("")
        state_running = gr.State(False)

        def on_send(user_msg: str, chat_hist: List[Tuple[str, str]]):
            assistant_msg, code = agent_response(user_msg, chat_hist)
            chat_hist = chat_hist + [(user_msg, assistant_msg)]
            return chat_hist, code, chat_hist, code

        send_btn.click(
            on_send,
            inputs=[user_box, state_history],
            outputs=[chatbot, code_view, state_history, state_code],
        )

        user_box.submit(
            on_send,
            inputs=[user_box, state_history],
            outputs=[chatbot, code_view, state_history, state_code],
        )

        def on_execute_stream(code: str, dry: bool, confirm_live: bool):
            if not code.strip():
                yield "No code to execute. Generate code first."
                return
            if not dry and not confirm_live:
                yield "Live trades require confirmation. Please check the confirmation box or enable Dry-run."
                return
            # Audit here as well for immediate feedback
            issues = audit_generated_code(code)
            if issues:
                yield "\n".join(["Execution blocked due to code audit issues:"] + [f"- {i}" for i in issues])
                return
            # Stream execution
            yield from execute_code_streaming(code, dry_run=dry)

        exec_btn.click(
            on_execute_stream,
            inputs=[state_code, dry_toggle, live_confirm],
            outputs=[output_box],
        )

        def on_stop():
            with CURRENT_PROCESS_LOCK:
                global CURRENT_PROCESS
                if CURRENT_PROCESS is not None:
                    try:
                        CURRENT_PROCESS.kill()
                        return "Execution stopped by user."
                    finally:
                        CURRENT_PROCESS = None
            return "No execution in progress."

        stop_btn.click(on_stop, inputs=None, outputs=[output_box])

        def on_clear():
            return [], "", [], ""

        clear_btn.click(on_clear, inputs=None, outputs=[chatbot, code_view, state_history, state_code])

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", 7860)))
