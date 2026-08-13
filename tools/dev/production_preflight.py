from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text

from app.core.config import settings
from app.infrastructure.database.engine import engine


def check(name: str, ok: bool, detail: str) -> bool:
    print(
        f"[{'PASS' if ok else 'FAIL'}] "
        f"{name}: {detail}"
    )
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Non-destructive production preflight checks "
            "for the current single-process architecture."
        )
    )
    parser.add_argument(
        "--allow-debug",
        action="store_true",
        help="Do not fail when DEBUG=true.",
    )
    args = parser.parse_args()

    results = []

    results.append(
        check(
            "debug",
            args.allow_debug or not settings.debug,
            f"DEBUG={settings.debug}",
        )
    )

    env_path = PROJECT_ROOT / ".env"
    results.append(
        check(
            "env-file",
            env_path.exists(),
            str(env_path),
        )
    )

    private_key = Path(
        settings.default_ssh_private_key_path
    ).expanduser()

    results.append(
        check(
            "ssh-private-key",
            private_key.is_file(),
            str(private_key),
        )
    )

    known_hosts = Path(
        settings.ssh_known_hosts_path
    ).expanduser()

    results.append(
        check(
            "ssh-known-hosts",
            known_hosts.is_file(),
            str(known_hosts),
        )
    )

    provider_ok = settings.llm_provider == "ollama"

    results.append(
        check(
            "llm-provider",
            provider_ok,
            settings.llm_provider,
        )
    )

    try:
        with engine.connect() as connection:
            value = connection.scalar(
                text("SELECT 1")
            )

        results.append(
            check(
                "database-connectivity",
                value == 1,
                settings.postgres_db,
            )
        )
    except Exception as exc:
        results.append(
            check(
                "database-connectivity",
                False,
                str(exc),
            )
        )

    try:
        with engine.connect() as connection:
            vector_exists = bool(
                connection.scalar(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM pg_extension
                            WHERE extname = 'vector'
                        )
                        """
                    )
                )
            )

            hnsw_exists = bool(
                connection.scalar(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM pg_indexes
                            WHERE schemaname = 'public'
                              AND indexname =
                              'ix_retrieval_embedding_hnsw_cosine'
                        )
                        """
                    )
                )
            )

        results.append(
            check(
                "pgvector",
                vector_exists,
                "extension present"
                if vector_exists
                else "missing",
            )
        )

        results.append(
            check(
                "hnsw-index",
                hnsw_exists,
                "present"
                if hnsw_exists
                else "missing",
            )
        )

    except Exception as exc:
        results.append(
            check(
                "rag-schema",
                False,
                str(exc),
            )
        )

    print()
    print(
        "Architecture reminder: run one "
        "application worker only."
    )

    passed = sum(results)
    total = len(results)

    print(
        f"Preflight: {passed}/{total} checks passed"
    )

    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
