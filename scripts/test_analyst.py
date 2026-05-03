"""
Testa o Analista de ponta a ponta.
Roda com: python -m scripts.test_analyst
"""

from src.agents.collector import collect
from src.agents.analyst import analyze
from src.agents.serializer import bundle_to_llm_json
from src.db import close_pool


def _print_section(title: str) -> None:
    print(f"\n{'─' * 60}\n  {title}\n{'─' * 60}")


def main() -> None:
    print("1. Coletando snapshot...")
    bundle = collect()

    print("\n2. JSON enviado ao LLM (preview):")
    json_str = bundle_to_llm_json(bundle)
    # imprime só primeiros 800 chars pra não poluir
    print(json_str[:800] + ("\n..." if len(json_str) > 800 else ""))

    print("\n3. Chamando o Groq...")
    insights = analyze(bundle)

    _print_section(f"💡 INSIGHTS ({len(insights)})")

    if not insights:
        print("Nenhum insight gerado. (Pode ser sinal de pouco dado.)")
    
    # Ordena por severidade desc pra ver os mais críticos primeiro
    insights_sorted = sorted(insights, key=lambda i: i.severity, reverse=True)

    for i, insight in enumerate(insights_sorted, 1):
        sev_marker = "🚨" if insight.severity >= 4 else "⚡" if insight.severity >= 3 else "💡"
        print(f"\n{i}. {sev_marker} [{insight.kind}] sev={insight.severity}")
        print(f"   Título: {insight.title}")
        print(f"   Razão:  {insight.rationale}")
        if insight.subject:
            print(f"   Matéria: {insight.subject}", end="")
            if insight.topic:
                print(f" → {insight.topic}", end="")
            print()
        if insight.deadline_id:
            print(f"   Deadline ID: {insight.deadline_id}")

    close_pool()
    print("\n✅ Analista funcionando!")


if __name__ == "__main__":
    main()