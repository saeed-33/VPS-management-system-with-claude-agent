from app.core.policies.diagnostic_tools import (
    build_default_diagnostic_tool_registry,
)
from tools.dev.seed_specialists import (
    SPECIALISTS,
    build_create_dto,
    build_update_dto,
)


def test_seeded_specialists_reference_registered_read_only_tools():
    registered = {
        item.tool_id
        for item in build_default_diagnostic_tool_registry().definitions
    }

    for definition in SPECIALISTS:
        allowed = set(definition["allowed_tool_ids"])
        assert allowed
        assert allowed <= registered
        assert set(build_create_dto(definition).allowed_tool_ids) == allowed
        assert set(build_update_dto(definition).allowed_tool_ids) == allowed
