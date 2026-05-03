"""
Interface Gradio do Study Companion.

Roda com: python -m src.ui.app
Abre em: http://localhost:7860
"""

import gradio as gr

from src.ui.tabs.session_tab import build_session_tab
from src.ui.tabs.daily_log_tab import build_daily_log_tab
from src.ui.tabs.subjects_tab import build_subjects_tab        
from src.ui.tabs.deadlines_tab import build_deadlines_tab      
from src.ui.tabs.insights_tab import build_insights_tab  


def build_app() -> gr.Blocks:
    """Monta o app completo combinando as abas."""
    with gr.Blocks(
        title="Study Companion",
        theme=gr.themes.Soft(),
    ) as app:
        gr.Markdown("# Study Companion")
        gr.Markdown("Registre seus estudos. O sistema analisa e te avisa.")

        with gr.Tabs():
            with gr.Tab("Sessão de estudo"):
                build_session_tab()
            with gr.Tab("Log diário"):
                build_daily_log_tab()
            with gr.Tab("Matérias"):
                build_subjects_tab()
            with gr.Tab("Prazos"):
                build_deadlines_tab()
            with gr.Tab("Insights"):
                build_insights_tab()

    return app


if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True,
    )