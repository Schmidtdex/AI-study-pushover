from src.agents.analyst import Insight
from src.agents.llm_clients import gemini_generate_text
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um assistente de estudos pessoal.
Seu trabalho: transformar um insight estruturado em uma push
notification curta, direta e humana.

REGRAS:
1. Máximo 2 frases. Idealmente 1. Total entre 50 e 180 caracteres.
2. Nunca comece com "Olá" ou "Oi" — push notification não tem espaço.
3. Use números concretos quando o insight tiver (dias, minutos).
4. Tom: amigo direto, não professor cobrador. Não use "você precisa".
5. Português do Brasil, informal mas não infantil.
6. NUNCA invente fatos — use só o que está no insight.
7. Se o insight é positivo (well_done), reforce sem exagerar.
8. Se for urgente, soa urgente. Se for revisão calma, soa calmo.
9. Sempre termine com pontuação final (ponto, exclamação ou interrogação).

EXEMPLOS BONS:
- "Integrais sumiu há 6 dias e era difícil. Vale 15min hoje pra não perder."
- "Prova de Cálculo em 2 dias e quase nada estudado. Hora de focar."
- "3 dias seguidos estudando. Tá no ritmo, segue."

EXEMPLOS RUINS (não faça):
- "Olá! Tudo bem? Notei que você precisa estudar..." (longo demais, formal)
- "Você deveria revisar integrais." (genérico, sem números)
- "Estude mais hoje!" (vazio)
- "Faz 7 dias que" (frase incompleta, sem pontuação)

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
    """Remove aspas, espaços e prefixos comuns que o modelo às vezes adiciona."""
    msg = message.strip()
    if (msg.startswith('"') and msg.endswith('"')) or \
       (msg.startswith("'") and msg.endswith("'")):
        msg = msg[1:-1].strip()
    
    msg = _detect_and_fix_truncation(msg)
    return msg


def _detect_and_fix_truncation(message: str) -> str:
    if not message:
        return message
    
    msg = message.rstrip()
    
    valid_endings = (".", "!", "?", "…")
    
    if msg.endswith(valid_endings):
        return msg
    
    last_period = max(
        msg.rfind("."),
        msg.rfind("!"),
        msg.rfind("?"),
    )
    
    if last_period == -1:
        logger.warning(
            "Mensagem do Gemini sem pontuação alguma, truncamento severo: %r",
            message,
        )
        return msg + "…"
    
    fixed = msg[:last_period + 1].strip()
    
    if fixed != msg:
        logger.warning(
            "Mensagem do Gemini truncada, corrigida. "
            "Original (%d chars): %r | Corrigida (%d chars): %r",
            len(msg), msg, len(fixed), fixed,
        )
    
    return fixed