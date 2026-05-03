
import gradio as gr

from src.repositories import subjects as subjects_repo
from src.repositories import sessions as sessions_repo
from src.ui.helpers import find_existing_subject



def _on_subject_change(typed: str) -> tuple:
    if not typed or not typed.strip():
        return (
            "",
            gr.update(visible=False),
            False,
        )

    existing = find_existing_subject(typed)

    if existing is not None:
        msg = (
            f"✓ Vai usar matéria existente: "
            f"**{existing['name']}** ({existing['category']})"
        )
        return (
            msg,
            gr.update(visible=False),
            False,
        )
    else:
        msg = (
            f" Matéria nova: **{typed.strip()}**. "
            f"Selecione a categoria abaixo."
        )
        return (
            msg,
            gr.update(visible=True),
            True,
        )


def _on_register(
    typed_subject: str,
    is_new: bool,
    category: str,
    topic: str,
    duration: int,
    difficulty: int,
    notes: str,
) -> tuple[str, gr.Dropdown]:
    # Validações
    if not typed_subject or not typed_subject.strip():
        return "Informe a matéria.", gr.update()

    if not topic or not topic.strip():
        return "Informe o tópico estudado.", gr.update()

    if duration <= 0:
        return "Duração precisa ser maior que zero.", gr.update()

    if is_new:
        if category not in ("faculdade", "pessoal"):
            return "Selecione a categoria da matéria nova.", gr.update()
        try:
            subject = subjects_repo.create(
                name=typed_subject.strip(),
                category=category,
            )
        except Exception as e:
            return f"Erro ao criar matéria: {e}", gr.update()
    else:
        subject = find_existing_subject(typed_subject)
        if subject is None:
            return "Matéria não encontrada. Tente de novo.", gr.update()

    # Cria a sessão
    try:
        session = sessions_repo.create(
            subject_id=subject["id"],
            topic=topic.strip(),
            duration_min=duration,
            difficulty=difficulty if difficulty > 0 else None,
            notes=notes.strip() if notes else None,
        )
    except Exception as e:
        return f"Erro ao salvar sessão: {e}", gr.update()

    # Recarrega lista de matérias pro dropdown atualizar
    new_choices = _load_subject_choices()

    msg = (
        f"Sessão registrada!\n\n"
        f"- **Matéria:** {subject['name']} ({subject['category']})"
        f"{' *(nova!)*' if is_new else ''}\n"
        f"- **Tópico:** {session['topic']}\n"
        f"- **Duração:** {session['duration_min']} min\n"
        f"- **Dificuldade:** {session['difficulty'] or '—'}"
    )

    return msg, gr.update(choices=new_choices)


# ---------- Helpers ----------

def _load_subject_choices() -> list[str]:
    """Lista de matérias formatadas para o dropdown."""
    return [s["name"] for s in subjects_repo.list_all()]


# ---------- Build ----------

def build_session_tab() -> None:

    gr.Markdown("### Registrar uma sessão de estudo")
    gr.Markdown(
        "*Digite a matéria livremente. Se já existe, será reaproveitada. "
        "Se for nova, escolha a categoria.*"
    )

    is_new_state = gr.State(value=False)

    with gr.Row():
        with gr.Column(scale=2):
            subject = gr.Dropdown(
                label="Matéria",
                choices=_load_subject_choices(),
                allow_custom_value=True,
                interactive=True,
                info="Digite ou selecione. Detecta duplicatas automaticamente.",
            )
            subject_status = gr.Markdown("")
            category = gr.Radio(
                label="Categoria (matéria nova)",
                choices=["faculdade", "pessoal"],
                value="faculdade",
                visible=False,
                interactive=True,
            )
            topic = gr.Textbox(
                label="Tópico",
                placeholder="ex: derivadas, useState, criptografia simétrica",
                max_lines=1,
            )

        with gr.Column(scale=1):
            duration = gr.Slider(
                label="Duração (min)",
                minimum=5,
                maximum=240,
                step=5,
                value=30,
            )
            difficulty = gr.Slider(
                label="Dificuldade (1-5)",
                minimum=1,
                maximum=5,
                step=1,
                value=3,
            )

    notes = gr.Textbox(
        label="Notas (opcional)",
        placeholder="ex: travei na regra da cadeia, revisar com o vídeo do canal X",
        lines=2,
    )

    submit_btn = gr.Button("✓ Registrar sessão", variant="primary")
    status = gr.Markdown()

    subject.change(
        fn=_on_subject_change,
        inputs=subject,
        outputs=[subject_status, category, is_new_state],
    )

    submit_btn.click(
        fn=_on_register,
        inputs=[
            subject, is_new_state, category,
            topic, duration, difficulty, notes,
        ],
        outputs=[status, subject],
    )