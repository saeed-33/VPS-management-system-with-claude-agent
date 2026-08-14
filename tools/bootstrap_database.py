from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_value = str(PROJECT_ROOT)
if project_root_value not in sys.path:
    sys.path.insert(0, project_root_value)

import psycopg
from psycopg import sql
from sqlalchemy import create_engine, text

from app.core.config import settings


EXPECTED_TABLES = {
    "servers",
    "monitor_commands",
    "monitoring_profiles",
    "monitoring_profile_commands",
    "monitoring_reports",
    "command_executions",
    "report_analyses",
    "report_analysis_sources",
    "report_retrieval_documents",
    "specialist_definitions",
    "investigations",
    "investigation_specialist_candidates",
    "knowledge_sources",
    "knowledge_documents",
    "knowledge_chunks",
    "remediation_plans",
    "remediation_sandbox_results",
    "remediation_approvals",
    "remediation_executions",
    "remediation_verifications",
    "remediation_rollbacks",
    "remediation_evidence",
    "remediation_audit_events",
    "sandbox_validations",
    "autonomous_remediation_policies",
    "autonomous_policy_decisions",
    "autonomous_authorizations",
    "autonomous_policy_execution_reservations",
    "autonomous_policy_runtime_state",
    "autonomous_policy_audit_events",
    "admin_users",
    "admin_sessions",
    "admin_auth_audit_events",
}

CUSTOM_INDEXES = {
    "ix_retrieval_search_vector_gin",
    "ix_retrieval_scope",
    "ix_retrieval_embedding_hnsw_cosine",
}


def connection_kwargs(*, database: str) -> dict:
    return {
        "host": settings.postgres_host,
        "port": settings.postgres_port,
        "dbname": database,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
    }


def database_exists(database: str) -> bool:
    with psycopg.connect(
        **connection_kwargs(database="postgres"),
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (database,),
            )
            return cursor.fetchone() is not None


def create_database_if_missing() -> bool:
    database = settings.postgres_db

    if database_exists(database):
        print(f"Database exists: {database}")
        return False

    print(f"Creating database: {database}")

    with psycopg.connect(
        **connection_kwargs(database="postgres"),
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(database)
                )
            )

    print(f"Created database: {database}")
    return True


def ensure_vector_extension() -> None:
    with psycopg.connect(
        **connection_kwargs(database=settings.postgres_db),
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE EXTENSION IF NOT EXISTS vector"
            )

    print("Extension ready: vector")


def create_model_tables() -> None:
    # Importing this module registers every mapped model in Base.metadata.
    import app.infrastructure.database.models  # noqa: F401
    from app.infrastructure.database.base import Base

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

    try:
        Base.metadata.create_all(engine)
    finally:
        engine.dispose()

    print("SQLAlchemy tables/indexes created or verified.")


def create_custom_indexes() -> None:
    """
    These indexes are part of the current RAG contract but are not declared
    as SQLAlchemy Index objects on the model, so create them explicitly.

    CONCURRENTLY keeps this command safe to re-run on a populated database.
    It requires autocommit and must not run inside an explicit transaction.
    """
    statements = [
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            ix_retrieval_search_vector_gin
        ON report_retrieval_documents
        USING gin (search_vector)
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            ix_retrieval_scope
        ON report_retrieval_documents (
            server_id,
            monitoring_profile_id,
            command_set_hash
        )
        """,
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            ix_retrieval_embedding_hnsw_cosine
        ON report_retrieval_documents
        USING hnsw (embedding vector_cosine_ops)
        WITH (
            m = 16,
            ef_construction = 64
        )
        """,
    ]

    with psycopg.connect(
        **connection_kwargs(database=settings.postgres_db),
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)

            cursor.execute(
                "ANALYZE report_retrieval_documents"
            )

    print("Custom RAG indexes created or verified.")


def verify_schema() -> bool:
    failures: list[str] = []

    with psycopg.connect(
        **connection_kwargs(database=settings.postgres_db),
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT extname
                FROM pg_extension
                WHERE extname = 'vector'
                """
            )
            vector_ready = cursor.fetchone() is not None

            cursor.execute(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                """
            )
            tables = {
                row[0]
                for row in cursor.fetchall()
            }

            cursor.execute(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                """
            )
            indexes = {
                row[0]
                for row in cursor.fetchall()
            }

            cursor.execute(
                """
                SELECT
                    data_type,
                    is_generated,
                    generation_expression
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'report_retrieval_documents'
                  AND column_name = 'search_vector'
                """
            )
            search_vector = cursor.fetchone()

            cursor.execute(
                """
                SELECT format_type(a.atttypid, a.atttypmod)
                FROM pg_attribute a
                JOIN pg_class c
                  ON c.oid = a.attrelid
                JOIN pg_namespace n
                  ON n.oid = c.relnamespace
                WHERE n.nspname = 'public'
                  AND c.relname = 'report_retrieval_documents'
                  AND a.attname = 'embedding'
                  AND NOT a.attisdropped
                """
            )
            embedding_type_row = cursor.fetchone()

    missing_tables = EXPECTED_TABLES - tables
    missing_indexes = CUSTOM_INDEXES - indexes

    if not vector_ready:
        failures.append("pgvector extension is missing")

    if missing_tables:
        failures.append(
            "missing tables: "
            + ", ".join(sorted(missing_tables))
        )

    if missing_indexes:
        failures.append(
            "missing custom indexes: "
            + ", ".join(sorted(missing_indexes))
        )

    if search_vector is None:
        failures.append("search_vector column is missing")
    else:
        data_type, is_generated, expression = search_vector

        if data_type != "tsvector":
            failures.append(
                f"search_vector type is {data_type}, expected tsvector"
            )

        if is_generated != "ALWAYS":
            failures.append(
                "search_vector is not a generated ALWAYS column"
            )

        if not expression:
            failures.append(
                "search_vector generation expression is empty"
            )

    embedding_type = (
        embedding_type_row[0]
        if embedding_type_row
        else None
    )

    if embedding_type != "vector(768)":
        failures.append(
            f"embedding type is {embedding_type!r}, expected 'vector(768)'"
        )

    print()
    print("Database verification")
    print("=" * 40)
    print(f"Database:          {settings.postgres_db}")
    print(f"pgvector:          {'OK' if vector_ready else 'MISSING'}")
    print(
        f"Tables:            "
        f"{len(EXPECTED_TABLES - missing_tables)}/{len(EXPECTED_TABLES)}"
    )
    print(
        f"Custom RAG indexes:"
        f" {len(CUSTOM_INDEXES - missing_indexes)}/{len(CUSTOM_INDEXES)}"
    )
    print(f"Embedding column:  {embedding_type}")
    print(
        "search_vector:     "
        + (
            "generated tsvector"
            if search_vector is not None
            else "MISSING"
        )
    )

    if failures:
        print()
        print("FAILED:")
        for failure in failures:
            print(f" - {failure}")
        return False

    print()
    print("Schema verification: PASS")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create/verify the PostgreSQL database required by "
            "the current chat_system schema."
        )
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Do not create anything; only verify the current schema.",
    )
    parser.add_argument(
        "--skip-create-database",
        action="store_true",
        help=(
            "Assume POSTGRES_DB already exists. Useful when the DB role "
            "does not have CREATEDB permission."
        ),
    )
    args = parser.parse_args()

    try:
        if not args.verify_only:
            if not args.skip_create_database:
                create_database_if_missing()
            elif not database_exists(settings.postgres_db):
                print(
                    "ERROR: target database does not exist and "
                    "--skip-create-database was used.",
                    file=sys.stderr,
                )
                return 2

            ensure_vector_extension()
            create_model_tables()
            create_custom_indexes()

        return 0 if verify_schema() else 1

    except psycopg.errors.InsufficientPrivilege as exc:
        print(
            "ERROR: PostgreSQL role lacks required privileges.\n"
            "Database creation requires CREATEDB (unless the database is "
            "created by an administrator), and CREATE EXTENSION vector "
            "requires suitable database privileges.\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 3

    except Exception as exc:
        print(
            f"ERROR: database bootstrap failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
