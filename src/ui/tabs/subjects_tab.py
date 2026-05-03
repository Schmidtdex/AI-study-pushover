import gradio as gr

from src.repositories import subjects as subjects_repo


def _load_subjects_table() -> list[list]:
    rows = subjects_repo.list_all()
    return [
        [s["id"], s["name"], s["category"], s["created_at"].strftime("%d/%m/%Y")]
        for s in rows
    ]


def _create_subject(name: str, category: str) -> tuple[str, list[list]]:
    if not name or not name.strip():
        return "Informe o nome da matéria.", _load_subjects_table()

    if category not in ("faculdade", "pessoal"):
        return "Selecione uma categoria.", _load_subjects_table()
    
    existing = subjects_repo.get_by_name(name.strip())
    if existing:
        return (
            f"Já existe matéria com esse nome ({existing['category']}).",
            _load_subjects_table(),
        )

    try:
        new_subject = subjects_repo.create(name=name.strip(), category=category)
    except Exception as e:
        return f"Erro: {e}", _load_subjects_table()

    return (
        f"Matéria '{new_subject['name']}' ({new_subject['category']}) criada.",
        _load_subjects_table(),
    )


def build_subjects_tab() -> None:

    gr.Markdown("### Matérias")
    gr.Markdown(
        "*Lista todas as matérias cadastradas. Você pode criar pela aba de "
        "sessões também — ali a criação é detectada automaticamente.*"
    )

    table = gr.Dataframe(
        headers=["ID", "Nome", "Categoria", "Criada em"],
        datatype=["number", "str", "str", "str"],
        value=_load_subjects_table(),
        interactive=False,
        wrap=True,
        label="Matérias cadastradas",
    )

    refresh_btn = gr.Button("Atualizar lista", size="sm")

    gr.Markdown("---")
    gr.Markdown("### Criar nova matéria")

    with gr.Row():
        name_input = gr.Textbox(
            label="Nome",
            placeholder="ex: Cálculo I, React, Cibersegurança",
            scale=2,
        )
        category_input = gr.Radio(
            label="Categoria",
            choices=["faculdade", "pessoal"],
            value="faculdade",
            scale=1,
        )

    create_btn = gr.Button("Criar matéria", variant="primary")
    status = gr.Markdown()

    # Eventos
    create_btn.click(
        fn=_create_subject,
        inputs=[name_input, category_input],
        outputs=[status, table],
    )

    refresh_btn.click(
        fn=lambda: _load_subjects_table(),
        inputs=None,
        outputs=table,
    )