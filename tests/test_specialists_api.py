from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.admin.api.specialists import router
from app.admin.dependencies import (
    get_specialist_definition_service,
)
from app.shared.exceptions import (
    DuplicateSpecialistDefinitionError,
    SpecialistDefinitionNotFoundError,
)


def model(
    specialist_id: int = 1,
    *,
    slug: str = "cpu",
    name: str = "CPU Specialist",
    enabled: bool = True,
):
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=specialist_id,
        slug=slug,
        name=name,
        description=None,
        instructions=None,
        enabled=enabled,
        domains=["cpu"],
        trigger_hints=[],
        knowledge_topics=["linux cpu"],
        allowed_tool_ids=[],
        priority=100,
        max_rounds=2,
        max_actions=4,
        specialist_metadata={},
        created_at=now,
        updated_at=now,
    )


class FakeService:
    def __init__(self):
        self.items = {
            1: model(),
        }

    def list_specialists(self, *, enabled_only=False):
        values = list(self.items.values())
        if enabled_only:
            values = [
                item
                for item in values
                if item.enabled
            ]
        return values

    def get_specialist(self, specialist_id):
        item = self.items.get(specialist_id)
        if item is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )
        return item

    def create_specialist(self, data):
        if data.slug == "duplicate":
            raise DuplicateSpecialistDefinitionError(
                data.slug
            )
        item = model(
            2,
            slug=data.slug.strip().lower(),
            name=data.name,
            enabled=data.enabled,
        )
        self.items[item.id] = item
        return item

    def update_specialist(self, specialist_id, data):
        item = self.get_specialist(specialist_id)
        if data.name is not None:
            item.name = data.name
        return item

    def set_enabled(self, specialist_id, enabled):
        item = self.get_specialist(specialist_id)
        item.enabled = enabled
        return item

    def delete_specialist(self, specialist_id):
        self.get_specialist(specialist_id)
        del self.items[specialist_id]


def client():
    app = FastAPI()
    service = FakeService()

    app.dependency_overrides[
        get_specialist_definition_service
    ] = lambda: service

    app.include_router(router)

    return TestClient(app), service


def test_list_specialists():
    api, _ = client()

    response = api.get(
        "/api/specialists"
    )

    assert response.status_code == 200
    assert response.json()[0]["slug"] == "cpu"


def test_create_specialist():
    api, _ = client()

    response = api.post(
        "/api/specialists",
        json={
            "slug": "memory",
            "name": "Memory Specialist",
        },
    )

    assert response.status_code == 201
    assert response.json()["slug"] == "memory"


def test_duplicate_specialist_returns_409():
    api, _ = client()

    response = api.post(
        "/api/specialists",
        json={
            "slug": "duplicate",
            "name": "Duplicate",
        },
    )

    assert response.status_code == 409


def test_update_and_enable():
    api, _ = client()

    response = api.patch(
        "/api/specialists/1",
        json={
            "name": "Linux CPU Investigator",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["name"]
        == "Linux CPU Investigator"
    )

    response = api.put(
        "/api/specialists/1/enabled",
        json={
            "enabled": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["enabled"] is False


def test_missing_specialist_returns_404():
    api, _ = client()

    response = api.get(
        "/api/specialists/999"
    )

    assert response.status_code == 404


def test_delete_specialist():
    api, _ = client()

    response = api.delete(
        "/api/specialists/1"
    )

    assert response.status_code == 204
