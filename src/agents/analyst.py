import typing_extensions
import json
from dataclasses import dataclass
from typing import Literal, Optional
from src.agents.context_types import ContextBundle
from src.agents.serializer import bundle_to_llm_json
from src.agents.llm_clients import groq_chat_json

InsightKind = Literal[
    "urgent_deadline",      # prazo apertado + estudo insuficiente
    "forgotten_topic",      # tópico não revisado há tempo (spaced rep)
    "neglected_subject",    # matéria sem estudo nenhum
    "low_energy_pattern",   # vários dias com energia baixa
    "well_done",            # padrão positivo digno de reforço
]

@dataclass
class Insight:
    kind: InsightKind
    severity: int
    title: str
    rationale: str
    subject: Optional[str]
    topic: Optional[str]
    deadline_id: Optional[str]


SYSTEM_PROMPT = """Você é um analista de hábitos de estudo.
Recebe um snapshot estruturado dos dados de estudo do usuário e
devolve uma lista de insights ACIONÁVEIS, em ordem de prioridade.

REGRAS DURAS:
1. Nunca invente fatos. Cite apenas o que está no snapshot.
2. Não dê conselhos genéricos ("estude mais"). Seja específico.
3. Priorize matérias da faculdade sobre trilhas pessoais (categoria 'faculdade' > 'pessoal').
4. Se o usuário está com baixa energia ou registrou contexto difícil ('tava cansado',
   'tive evento'), seja gentil — não jogue mais cobrança em cima.
5. Se houver padrão positivo (estudou todos os dias, completou deadline), gere
   ao menos um insight 'well_done' pra reforçar.
6. Severidade 5 só pra coisas realmente urgentes (prova em <2 dias sem estudo).
   Severidade 1 é "vale lembrar mas não é urgente".
7. Máximo 5 insights por análise. Menos é melhor que mais.

FORMATO DA RESPOSTA: JSON com a chave "insights" sendo uma lista de objetos.
Cada objeto deve ter:
  - kind: um de "urgent_deadline" | "forgotten_topic" | "neglected_subject" |
          "low_energy_pattern" | "well_done"
  - severity: integer 1-5
  - title: string curta (até 80 caracteres)
  - rationale: string explicando POR QUE esse insight (1-2 frases, cita números)
  - subject: nome da matéria (ou null se não aplicável)
  - topic: tópico específico (ou null)
  - deadline_id: integer id do deadline relacionado (ou null)

Exemplo de resposta válida:
{
  "insights": [
    {
      "kind": "urgent_deadline",
      "severity": 5,
      "title": "Prova de Cálculo em 2 dias e só 30min estudados",
      "rationale": "A prova P1 acontece em 2.4 dias e nos últimos 7 dias houve apenas 30 minutos de estudo de Cálculo. Risco alto de despreparo.",
      "subject": "Cálculo I",
      "topic": null,
      "deadline_id": 7
    }
  ]
}"""

def analyze(bundle: ContextBundle) -> list[Insight]:
    user_prompt = (
        "Aqui está o snapshot dos dados de estudo:\n\n"
        + bundle_to_llm_json(bundle)
    )

    raw_response = groq_chat_json(
        system=SYSTEM_PROMPT,
        user=user_prompt
    )

    return _parse_insights(raw_response)


_VALID_KINDS = {
    "urgent_deadline", "forgotten_topic", "neglected_subject",
    "low_energy_pattern", "well_done",
}

def _parse_insights(raw_json: str) -> list[Insight]:
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido do analista: {e}") from e

    if not isinstance(data, dict) or "insights" not in data:
        raise ValueError("Chave 'insights' ausente na resposta do analista: " + str(data)[:200])

    raw_list = data["insights"]
    if not isinstance(raw_list, list):
        raise ValueError("Chave 'insights' deve ser uma lista")
    insights: list[Insight] = []
    for i, item in enumerate(raw_list):
        try:
            insights.append(_validate_one(item))
        except ValueError as e:
            raise ValueError(f"  Insight #{i} descartado: {e}")
        return insights

def _validate_one(item: dict) -> Insight:
    if not isinstance(item, dict):
        raise ValueError("não é um objeto")

    kind = item.get("kind")
    if kind not in _VALID_KINDS:
        raise ValueError(f"kind inválido: {kind}")

    severity = item.get("severity")
    if not isinstance(severity, int) or not (1 <= severity <= 5):
        raise ValueError(f"severity inválida: {severity}")

    title = item.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title vazio ou inválido")

    rationale = item.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("rationale vazio ou inválido")

    return Insight(
        kind=kind,
        severity=severity,
        title=title.strip(),
        rationale=rationale.strip(),
        subject=item.get("subject"),
        topic=item.get("topic"),
        deadline_id=item.get("deadline_id"),
    )