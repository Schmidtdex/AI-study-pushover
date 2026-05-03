"""
Testa o ciclo completo, de coleta a push.
Roda com: python -m scripts.test_full_cycle
"""

import json
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from src.orchestrator import run_cycle
from src.db import close_pool


def main() -> None:
    print("=== Testando ciclo completo (DRY RUN) ===\n")

    # Primeiro em dry_run pra ver o que aconteceria sem enviar push
    print("📋 Modo dry_run (sem envio real):\n")
    result = run_cycle(dry_run=True)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("message"):
        print("\n" + "─" * 60)
        print(f"📱 Mensagem que seria enviada:")
        print(f"   \"{result['message']}\"")
        print("─" * 60)

        confirm = input("\n🚀 Enviar de verdade? (sim/não): ").strip().lower()
        if confirm == "sim":
            print("\nEnviando...")
            real_result = run_cycle(dry_run=False)
            print(json.dumps(real_result, indent=2, ensure_ascii=False))
            if real_result["pushed"]:
                print("\n✅ Push enviado! Confere o celular.")
        else:
            print("Ok, não enviei.")
    else:
        reason = result.get("reason", "?")
        print(f"\n💤 Nenhum push seria enviado. Motivo: {reason}")

    close_pool()


if __name__ == "__main__":
    main()