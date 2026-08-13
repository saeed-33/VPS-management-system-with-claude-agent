from app.infrastructure.database.repositories.agent_job_repository import (
    _bounded_error_message,
)


def test_agent_job_error_messages_are_bounded_to_schema_contract():
    assert _bounded_error_message("x" * 2500) == "x" * 2000
    assert _bounded_error_message(None) is None
