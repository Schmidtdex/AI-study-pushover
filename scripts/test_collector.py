"""
Testa o Agente Coletor.
Roda com: python -m scripts.test_collector

Pré-requisitos: já ter dados no banco vindo dos test_* anteriores.
"""

from src.agents.collector import collect
from src.db import close_pool


def _print_section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


def main() -> None:
    print("Coletando snapshot do estudo...\n")
    bundle = collect()

    print(f"📸 Snapshot gerado em: {bundle.generated_at:%d/%m/%Y %H:%M}")

    # ----- Daily -----
    _print_section("📓 DAILY")
    if bundle.daily.today_log:
        log = bundle.daily.today_log
        print(f"Log de hoje: energia={log['energy']}, mood='{log['mood']}'")
        print(f"             note='{log['note']}'")
    else:
        print("Sem log de hoje ainda.")
    print(f"Logs últimos 7 dias: {len(bundle.daily.recent_logs)}")
    if bundle.daily.avg_energy_7d is not None:
        print(f"Energia média 7d: {bundle.daily.avg_energy_7d:.2f}")

    # ----- Deadlines -----
    _print_section("📅 DEADLINES")
    print(f"Pendentes (próximos 14d): {len(bundle.deadlines.upcoming)}")
    for d in bundle.deadlines.upcoming:
        print(
            f"  - [{d['subject_category']}] {d['subject_name']} - "
            f"{d['title']} ({d['kind']}) em {d['days_until']:.1f}d"
        )
    if bundle.deadlines.overdue:
        print(f"\nVencidos não concluídos: {len(bundle.deadlines.overdue)}")
        for d in bundle.deadlines.overdue:
            print(f"  ⚠️ {d['subject_name']} - {d['title']}")

    # ----- Sessions -----
    _print_section("📚 SESSIONS")
    print(f"Sessões últimos 7d: {len(bundle.sessions.recent)}")
    print(f"\nMinutos por matéria (7d):")
    for t in bundle.sessions.total_by_subject_7d:
        print(
            f"  [{t['subject_category']}] {t['subject_name']}: "
            f"{t['total_min']}min ({t['session_count']} sessões)"
        )

    # ----- Tracks -----
    _print_section("🎯 TRACKS ATIVAS")
    for t in bundle.tracks.active:
        print(f"  - {t['subject_name']}: {t['course_name']}")
        if t['goal']:
            print(f"    objetivo: {t['goal']}")

    # ----- Derived (a parte mais importante) -----
    _print_section("🧠 DERIVED (insights brutos)")

    print(f"\n• Dias estudou nos últimos 7: {bundle.derived.days_studied_in_last_7}/7")

    print(f"\n• Matérias negligenciadas (0min em 7d):")
    if bundle.derived.neglected_subjects:
        for n in bundle.derived.neglected_subjects:
            print(f"    - [{n['subject_category']}] {n['subject_name']}")
    else:
        print("    (nenhuma)")

    print(f"\n• Tópicos esquecidos (>= 5 dias sem revisar):")
    if bundle.derived.forgotten_topics:
        for f in bundle.derived.forgotten_topics:
            print(
                f"    - {f['subject_name']} → {f['topic']} "
                f"(há {f['days_since_last_seen']}d, dif={f['avg_difficulty']:.1f})"
            )
    else:
        print("    (nenhum)")

    print(f"\n• Deadlines URGENTES (<=3d e pouco estudo):")
    if bundle.derived.urgent_deadlines:
        for u in bundle.derived.urgent_deadlines:
            print(
                f"    🚨 {u['subject_name']} - {u['title']} "
                f"em {u['days_until']:.1f}d (estudou {u['studied_min_7d']}min)"
            )
    else:
        print("    (nenhum)")

    close_pool()
    print("\n✅ Coletor funcionando!")


if __name__ == "__main__":
    main()