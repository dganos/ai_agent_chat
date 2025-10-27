import os
import sys
import tempfile
import textwrap
from typing import Any, List, Tuple

import gradio as gr
from dotenv import load_dotenv
from agent import GrokAgent, AgentResponse

# Ensure local imports work when executing generated code in a temp dir
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")


# --- Execution ---

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
                    exec_btn = gr.Button("Execute", variant="primary")
                output_box = gr.Textbox(label="Output / Logs", lines=16)

        state_history = gr.State([])  # list of (user, assistant)
        state_code = gr.State("")

        agent = GrokAgent(api_key=XAI_API_KEY)

        def on_send(user_msg: str, chat_hist: List[Tuple[str, str]]):
            resp: AgentResponse = agent.chat(user_msg, chat_hist)
            chat_hist = chat_hist + [(user_msg, resp.message)]
            return chat_hist, resp.code, chat_hist, resp.code

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

        def on_execute(code: str, dry: bool):
            return execute_code(code, dry_run=dry)

        exec_btn.click(on_execute, inputs=[state_code, dry_toggle], outputs=[output_box])

        def on_clear():
            return [], "", [], ""

        clear_btn.click(on_clear, inputs=None, outputs=[chatbot, code_view, state_history, state_code])

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", 7860)))
