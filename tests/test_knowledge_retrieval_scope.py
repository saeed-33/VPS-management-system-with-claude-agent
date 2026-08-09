from sqlalchemy.dialects import postgresql

from app.shared.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)


def compile_condition(
    *,
    specialist_slug=None,
    domains=(),
):
    condition = (
        KnowledgeRetrievalRepository
        ._scope_condition(
            specialist_slug=specialist_slug,
            domains=domains,
        )
    )

    return str(
        condition.compile(
            dialect=postgresql.dialect(),
        )
    )


def test_scope_condition_contains_specialist():
    sql = compile_condition(
        specialist_slug="nginx",
    )

    assert "specialist_slugs" in sql
    assert "@>" in sql


def test_scope_condition_accepts_domains():
    sql = compile_condition(
        domains=("http", "proxy"),
    )

    assert "domains" in sql
    assert "@>" in sql
    assert " OR " in sql


def test_empty_scope_is_true():
    sql = compile_condition()

    assert sql == "TRUE"