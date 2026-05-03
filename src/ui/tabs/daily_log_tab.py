from datetime import date

import gradio as gr

from src.repositories import daily_logs as logs_repo


def _load_today_log() -> str:
    """Retorna o log de hoje formatado em markdown, ou aviso se não existe."""
    log = logs_repo.get_by_date(date.today())
    if log is None:
        return "*Sem log de hoje ainda.*"

    energy = log["energy"] if log["energy"] is not None else "—"
    mood = log["mood"] if log["mood"] else "—"
    note = log["note"] if log["note"] else "—"

    return (
        f"**Log de hoje ({log['log_date']}):**\n\n"
        f"- Energia: {energy}/5\n"
        f"- Mood: {mood}\n"
        f"- Nota: {note}"
    )


def _save_log(energy: int, mood: str, note: str) -> tuple[str, str]:

    try:
        logs_repo.upsert(
            energy=energy if energy > 0 else None,
            mood=mood.strip() if mood else None,
            note=note.strip() if note else None,
        )
    except Exception as e:
        return f"Erro: {e}", _load_today_log()

    return "Log salvo!", _load_today_log()


def build_daily_log_tab() -> None:
    gr.Markdown("### Como foi o dia?")
    gr.Markdown(
        "Registre uma vez por dia (ou atualize ao longo dele). "
        "Campos vazios não sobrescrevem o que já tem salvo."
    )

    today_display = gr.Markdown(value=_load_today_log())

    with gr.Row():
        energy = gr.Slider(
            label="Energia (1-5)",
            minimum=0,           
            maximum=5,
            step=1,
            value=0,
            info="0 = pular este campo",
        )
        mood = gr.Textbox(
            label="Mood",
            placeholder="ex: focado, ansioso, cansado",
            max_lines=1,
        )

    note = gr.Textbox(
        label="Observação do dia",
        placeholder=(
            "ex: tive evento à tarde, fiquei no projeto, dormi mal, "
            "produtividade alta de manhã"
        ),
        lines=3,
    )

    submit_btn = gr.Button(" Salvar log do dia", variant="primary")
    status = gr.Markdown()

    submit_btn.click(
        fn=_save_log,
        inputs=[energy, mood, note],
        outputs=[status, today_display],
    )