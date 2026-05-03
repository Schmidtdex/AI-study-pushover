from datetime import datetime, timedelta

import gradio as gr

from src.repositories import subjects as subjects_repo
from src.repositories import deadlines as deadlines_repo


def _load_deadlines_table() -> list[list]:
    rows = deadlines_repo.list_all(include_completed=False)
    return [
        [
            d["id"],
            d["subject_name"],
            d["title"],
            d["kind"],
            d["due_at"].strftime("%d/%m/%Y %H:%M"),
        ]
        for d in rows
    ]


def _load_subject_choices() -> list[str]:
    return [s["name"] for s in subjects_repo.list_all()]


def _create_deadline(
    subject_name: str,
    title: str,
    kind: str,
    due_date: str,
    due_time: str,
) -> tuple[str, list[list]]:
    if not subject_name:
        return "Selecione uma matéria.", _load_deadlines_table()
    if not title or not title.strip():
        return "Informe o título.", _load_deadlines_table()

    subject = subjects_repo.get_by_name(subject_name)
    if subject is None:
        return f"Matéria '{subject_name}' não encontrada.", _load_deadlines_table()

    try:
        due_str = f"{due_date} {due_time}"
        due_at = datetime.strptime(due_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return (
            "Data ou hora inválida. Use AAAA-MM-DD e HH:MM.",
            _load_deadlines_table(),
        )

    if due_at < datetime.now():
        return (
            "Data no passado. Cadastre só prazos futuros.",
            _load_deadlines_table(),
        )

    try:
        deadlines_repo.create(
            subject_id=subject["id"],
            title=title.strip(),
            kind=kind,
            due_at=due_at,
        )
    except Exception as e:
        return f"Erro: {e}", _load_deadlines_table()

    return (
        f"Deadline '{title}' cadastrado pra {due_at:%d/%m %H:%M}.",
        _load_deadlines_table(),
    )


def _complete_deadline(deadline_id: str) -> tuple[str, list[list]]:
    if not deadline_id or not deadline_id.strip():
        return "Informe o ID do deadline.", _load_deadlines_table()

    try:
        did = int(deadline_id.strip())
    except ValueError:
        return "ID precisa ser um número.", _load_deadlines_table()

    success = deadlines_repo.mark_completed(did)
    if not success:
        return f"Deadline com ID {did} não encontrado.", _load_deadlines_table()

    return f"Deadline {did} marcado como concluído.", _load_deadlines_table()


def _default_due_date() -> str:
    return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")


def build_deadlines_tab() -> None:

    gr.Markdown("### Deadlines pendentes")

    table = gr.Dataframe(
        headers=["ID", "Matéria", "Título", "Tipo", "Prazo"],
        datatype=["number", "str", "str", "str", "str"],
        value=_load_deadlines_table(),
        interactive=False,
        wrap=True,
    )

    refresh_btn = gr.Button("Atualizar lista", size="sm")

    gr.Markdown("---")
    gr.Markdown("### Cadastrar novo deadline")

    with gr.Row():
        d_subject = gr.Dropdown(
            label="Matéria",
            choices=_load_subject_choices(),
            scale=2,
        )
        d_kind = gr.Radio(
            label="Tipo",
            choices=["prova", "entrega", "trabalho", "outro"],
            value="prova",
            scale=1,
        )

    d_title = gr.Textbox(
        label="Título",
        placeholder="ex: Prova P1, Lista 3, Trabalho final",
    )

    with gr.Row():
        d_date = gr.Textbox(
            label="Data (AAAA-MM-DD)",
            value=_default_due_date(),
            placeholder="2026-05-15",
        )
        d_time = gr.Textbox(
            label="Hora (HH:MM)",
            value="23:59",
            placeholder="14:30",
        )

    create_btn = gr.Button("Cadastrar deadline", variant="primary")
    create_status = gr.Markdown()

    gr.Markdown("---")
    gr.Markdown("### Marcar como concluído")

    with gr.Row():
        complete_id = gr.Textbox(
            label="ID do deadline",
            placeholder="ex: 3",
            scale=1,
        )
        complete_btn = gr.Button("Marcar concluído", scale=1)

    complete_status = gr.Markdown()

    create_btn.click(
        fn=_create_deadline,
        inputs=[d_subject, d_title, d_kind, d_date, d_time],
        outputs=[create_status, table],
    )

    complete_btn.click(
        fn=_complete_deadline,
        inputs=complete_id,
        outputs=[complete_status, table],
    )

    refresh_btn.click(
        fn=lambda: gr.update(value=_load_deadlines_table()),
        inputs=None,
        outputs=table,
    ).then(
        fn=lambda: gr.update(choices=_load_subject_choices()),
        inputs=None,
        outputs=d_subject,
    )