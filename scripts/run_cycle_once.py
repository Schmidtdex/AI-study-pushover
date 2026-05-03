import logging
import sys
from src.orchestrator import run_cycle
from src.db import close_pool


# Configura logging com timestamp — vai aparecer bonito nos logs do Actions
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("🚀 Iniciando ciclo de análise...")

    try:
        result = run_cycle(dry_run=False)

        # Loga o resultado em formato estruturado
        logger.info("Resultado: %s", result)

        if result.get("pushed"):
            logger.info(
                "✅ Push enviado | kind=%s severity=%s",
                result.get("chosen_kind"),
                result.get("chosen_severity"),
            )
        else:
            logger.info(
                "💤 Nenhum push | motivo: %s",
                result.get("reason", "?"),
            )

        return 0

    except Exception:
        # Loga stack trace completo e retorna falha
        logger.exception("❌ Erro no ciclo")
        return 1

    finally:
        close_pool()


if __name__ == "__main__":
    sys.exit(main())