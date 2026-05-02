"""
Testa o repository de sessions.
Roda com: python -m scripts.test_sessions

Pré-requisito: já ter rodado test_subjects ao menos uma vez
(precisa existir 'Cálculo I' e 'React' no banco).
"""

from datetime import datetime, timedelta
from src.repositories import subjects, sessions
from src.db import close_pool


def main() -> None:
    print("=== Testando repository de sessions ===\n")

    # Pega (ou cria) as matérias que vamos usar
    calc = subjects.get_or_create("Cálculo I", category="faculdade")
    react = subjects.get_or_create("React", category="pessoal")
    algo = subjects.get_or_create("Algoritmos", category="faculdade")

    # 1. Registra algumas sessões — algumas hoje, algumas no passado
    print("1. Registrando sessões...")

    # Hoje: estudou cálculo
    s1 = sessions.create(
        subject_id=calc["id"],
        topic="derivadas",
        duration_min=45,
        difficulty=4,
        notes="travei na regra da cadeia",
    )
    print(f"   Sessão hoje: {s1['topic']} ({s1['duration_min']}min)")

    # Hoje: estudou react
    s2 = sessions.create(
        subject_id=react["id"],
        topic="hooks (useState, useEffect)",
        duration_min=60,
        difficulty=2,
    )
    print(f"   Sessão hoje: {s2['topic']} ({s2['duration_min']}min)")

    # 4 dias atrás: cálculo de novo, mesmo tópico
    four_days_ago = datetime.now() - timedelta(days=4)
    s3 = sessions.create(
        subject_id=calc["id"],
        topic="derivadas",
        duration_min=30,
        difficulty=3,
        studied_at=four_days_ago,
    )
    print(f"   Sessão 4 dias atrás: {s3['topic']}")

    # 6 dias atrás: integrais (vai ser o "tópico esquecido")
    six_days_ago = datetime.now() - timedelta(days=6)
    s4 = sessions.create(
        subject_id=calc["id"],
        topic="integrais",
        duration_min=50,
        difficulty=5,
        studied_at=six_days_ago,
    )
    print(f"   Sessão 6 dias atrás: {s4['topic']}")

    # 2. Sessões dos últimos 7 dias
    print("\n2. Sessões dos últimos 7 dias:")
    for s in sessions.get_recent(days=7):
        when = s["studied_at"].strftime("%d/%m %H:%M")
        print(f"   [{when}] {s['subject_name']}: {s['topic']} ({s['duration_min']}min)")

    # 3. Tópicos vistos por último (chave do spaced repetition)
    print("\n3. Tópicos por 'última vez visto' (mais antigo primeiro):")
    for t in sessions.get_topics_last_seen(days_back=30):
        days_ago = (datetime.now(t["last_seen"].tzinfo) - t["last_seen"]).days
        print(
            f"   {t['subject_name']} → {t['topic']}: "
            f"visto há {days_ago}d, {t['times_studied']}x, "
            f"dificuldade média {t['avg_difficulty']:.1f}"
        )

    # 4. Total por matéria — note que 'Algoritmos' aparece com 0
    print("\n4. Total estudado por matéria (últimos 7 dias):")
    for t in sessions.total_minutes_by_subject(days=7):
        marker = "⚠️ " if t["total_min"] == 0 else "   "
        print(
            f"   {marker}[{t['subject_category']}] {t['subject_name']}: "
            f"{t['total_min']}min ({t['session_count']} sessões)"
        )

    # 5. Sessões de uma matéria específica
    print(f"\n5. Histórico de '{calc['name']}':")
    for s in sessions.list_by_subject(calc["id"]):
        when = s["studied_at"].strftime("%d/%m")
        print(f"   [{when}] {s['topic']} ({s['duration_min']}min, dif={s['difficulty']})")

    close_pool()
    print("\n✅ Repository de sessions funcionando!")


if __name__ == "__main__":
    main()