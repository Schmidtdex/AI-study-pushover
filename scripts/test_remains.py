"""
Testa deadlines, learning_tracks e daily_logs.
Roda com: python -m scripts.test_remaining_repos
"""

from datetime import datetime, date, timedelta
from src.repositories import subjects, deadlines, tracks, daily_logs
from src.db import close_pool


def main() -> None:
    print("=== Testando deadlines / tracks / daily_logs ===\n")

    # Pega ou cria as matérias que vamos usar
    calc = subjects.get_or_create("Cálculo I", category="faculdade")
    react = subjects.get_or_create("React", category="pessoal")

    # ---- DEADLINES ----
    print("📅 DEADLINES\n")

    # 1. Cria 3 deadlines com proximidades diferentes
    print("1. Criando deadlines...")
    in_2_days = datetime.now() + timedelta(days=2, hours=10)
    in_5_days = datetime.now() + timedelta(days=5)
    in_10_days = datetime.now() + timedelta(days=10)

    d1 = deadlines.create(calc["id"], "Prova P1", "prova", in_2_days)
    print(f"   {d1['title']} em {d1['due_at']:%d/%m %H:%M}")

    d2 = deadlines.create(calc["id"], "Lista 3", "entrega", in_5_days)
    print(f"   {d2['title']} em {d2['due_at']:%d/%m %H:%M}")

    d3 = deadlines.create(calc["id"], "Trabalho final", "trabalho", in_10_days)
    print(f"   {d3['title']} em {d3['due_at']:%d/%m %H:%M}")

    # 2. Próximos 7 dias — note que o de 10 dias NÃO aparece
    print("\n2. Deadlines nos próximos 7 dias:")
    for d in deadlines.get_upcoming(days=7):
        print(
            f"   [{d['subject_category']}] {d['subject_name']} - {d['title']} "
            f"em {d['days_until']:.1f} dias ({d['kind']})"
        )

    # 3. Marca a prova como concluída
    print(f"\n3. Marcando '{d1['title']}' como concluído...")
    deadlines.mark_completed(d1["id"])

    # 4. Lista de novo — agora a prova sumiu
    print("   Próximos 7 dias depois de marcar:")
    for d in deadlines.get_upcoming(days=7):
        print(f"   - {d['title']} em {d['days_until']:.1f} dias")

    # ---- LEARNING TRACKS ----
    print("\n\n🎯 LEARNING TRACKS\n")

    # 5. Cria trilha pra React
    print("5. Criando trilha pra React...")
    track = tracks.create(
        subject_id=react["id"],
        course_name="The Complete React Course",
        course_url="https://example.com/curso",
        goal="dominar hooks e context pra construir SPA",
    )
    print(f"   {track['course_name']}")
    print(f"   Objetivo: {track['goal']}")

    # 6. Lista trilhas ativas
    print("\n6. Trilhas ativas:")
    for t in tracks.list_active():
        print(f"   - {t['subject_name']}: {t['course_name']} (desde {t['started_at']})")

    # 7. Desativa
    print(f"\n7. Desativando trilha de React...")
    tracks.deactivate(track["id"])
    print(f"   Trilhas ativas agora: {len(tracks.list_active())}")

    # 8. Reativa
    tracks.reactivate(track["id"])
    print(f"   Reativada. Ativas: {len(tracks.list_active())}")

    # ---- DAILY LOGS ----
    print("\n\n📓 DAILY LOGS\n")

    # 9. Primeiro upsert do dia (cria)
    print("9. Registrando log de hoje (primeiro upsert)...")
    log = daily_logs.upsert(energy=4, mood="focado", note="manhã produtiva")
    print(f"   {log}")

    # 10. Segundo upsert (atualiza só mood, mantém o resto)
    print("\n10. Atualizando só o mood...")
    log = daily_logs.upsert(mood="cansado à tarde")
    print(f"   energy={log['energy']} (preservado), mood='{log['mood']}' (atualizado)")
    print(f"   note='{log['note']}' (preservado)")

    # 11. Cria logs de dias passados pra testar agregação
    print("\n11. Criando logs dos 3 dias anteriores...")
    for i in range(1, 4):
        d = date.today() - timedelta(days=i)
        daily_logs.upsert(log_date=d, energy=3, mood="ok")
    
    # 12. Logs recentes
    print("\n12. Logs dos últimos 7 dias:")
    for l in daily_logs.get_recent(days=7):
        print(f"   {l['log_date']}: energia={l['energy']}, mood='{l['mood']}'")

    # 13. Energia média
    avg = daily_logs.average_energy(days=7)
    print(f"\n13. Energia média (7d): {avg:.2f}" if avg else "   sem dados")

    close_pool()
    print("\n✅ Todos os repositórios funcionando!")


if __name__ == "__main__":
    main()