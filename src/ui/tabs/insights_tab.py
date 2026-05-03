
import gradio as gr

from src.orchestrator import run_cycle


def _format_result(result: dict) -> str:
    """Formata o dict de resultado em markdown bonito."""
    lines = ["### Resultado da análise\n"]

    lines.append(f"- **Coletor rodou:** {'✅' if result['collected'] else '❌'}")
    lines.append(f"- **Insights gerados:** {result['insights_count']}")

    if result.get("decided"):
        lines.append("")
        lines.append("### Insight escolhido pra notificar")
        lines.append(f"- **Tipo:** `{result['chosen_kind']}`")
        lines.append(f"- **Severidade:** {result['chosen_severity']}/5")
    else:
        lines.append("")
        lines.append("### Nenhum insight passaria pelas regras")
        lines.append(f"**Motivo:** {result.get('reason', '?')}")

    if result.get("message"):
        lines.append("")
        lines.append("### Mensagem que seria enviada")
        lines.append(f"> {result['message']}")

    if result.get("pushed"):
        lines.append("")
        lines.append(" *Push real foi enviado — você desativou o dry-run.*")
    else:
        lines.append("")
        lines.append("*(Nada foi enviado — modo dry-run.)*")

    return "\n".join(lines)


def _run_analysis(send_real: bool) -> str:
    """Roda um ciclo. Retorna markdown formatado."""
    try:
        result = run_cycle(dry_run=not send_real)
        return _format_result(result)
    except Exception as e:
        return f" Erro durante análise:\n\n```\n{e}\n```"


def build_insights_tab() -> None:
    """Constrói a aba de insights."""

    gr.Markdown("### Ver o que o sistema acharia agora")
    gr.Markdown(
        "*Roda o ciclo completo (Coletor → Analista → Decisor → Comunicador) "
        "e mostra o resultado. Por padrão **não envia push** — só mostra.*"
    )

    send_real = gr.Checkbox(
        label="Enviar push de verdade",
        value=False,
        info="Marca pra disparar a notificação real no Pushover.",
    )

    run_btn = gr.Button(" Analisar agora", variant="primary", size="lg")
    output = gr.Markdown()

    run_btn.click(
        fn=_run_analysis,
        inputs=send_real,
        outputs=output,
    )