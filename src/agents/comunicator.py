from src.agents.analyst import Insight
from src.agents.llm_clients import gemini_generate_text


SYSTEM_PROMPT = """Você é um assistente de estudos pessoal.
Seu trabalho: transformar um insight estruturado em uma push
notification curta, direta e humana.

REGRAS:
1. Máximo 2 frases. Idealmente 1.
2. Nunca comece com "Olá" ou "Oi" — push notification não tem espaço.
3. Use números concretos quando o insight tiver (dias, minutos).
4. Tom: amigo direto, não professor cobrador. Não use "você precisa".
5. Português do Brasil, informal mas não infantil.
6. NUNCA invente fatos — use só o que está no insight.
7. Se o insight é positivo (well_done), reforce sem exagerar.
8. Se for urgente, soa urgente. Se for revisão calma, soa calmo.

EXEMPLOS BONS:
- "Integrais sumiu há 6 dias e era difícil. Vale 15min hoje pra não perder."
- "Prova de Cálculo em 2 dias e quase nada estudado. Hora de focar."
- "3 dias seguidos estudando. Tá no ritmo, segue."

EXEMPLOS RUINS (não faça):
- "Olá! Tudo bem? Notei que você precisa estudar..." (longo demais, formal)
- "Você deveria revisar integrais." (genérico, sem números)
- "Estude mais hoje!" (vazio)

Responda APENAS com a mensagem final. Sem aspas, sem prefixo, sem explicação."""


def compose_message(insight: Insight) -> str:
    user_prompt = _build_user_prompt(insight)
    message = gemini_generate_text(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )
    return _clean(message)


def _build_user_prompt(insight: Insight) -> str:
    parts = [
        f"Tipo: {insight.kind}",
        f"Severidade: {insight.severity}/5",
        f"Título do insight: {insight.title}",
        f"Justificativa: {insight.rationale}",
    ]
    if insight.subject:
        parts.append(f"Matéria: {insight.subject}")
    if insight.topic:
        parts.append(f"Tópico: {insight.topic}")

    parts.append("\nGere a mensagem do push:")
    return "\n".join(parts)


def _clean(message: str) -> str:
    msg = message.strip()
    if (msg.startswith('"') and msg.endswith('"')) or \
       (msg.startswith("'") and msg.endswith("'")):
        msg = msg[1:-1].strip()
    return msg