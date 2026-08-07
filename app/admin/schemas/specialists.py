from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class SpecialistCreateRequest(BaseModel):
    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,99}$",
    )
    name: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    instructions: str | None = None
    enabled: bool = True
    domains: list[str] = Field(
        default_factory=list
    )
    trigger_hints: list[str] = Field(
        default_factory=list
    )
    knowledge_topics: list[str] = Field(
        default_factory=list
    )
    allowed_tool_ids: list[str] = Field(
        default_factory=list
    )
    priority: int = 100
    max_rounds: int = Field(
        default=2,
        ge=1,
    )
    max_actions: int = Field(
        default=4,
        ge=0,
    )
    metadata: dict = Field(
        default_factory=dict
    )

    @field_validator("slug")
    @classmethod
    def normalize_slug(
        cls,
        value: str,
    ) -> str:
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        return value.strip()


class SpecialistUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    instructions: str | None = None
    enabled: bool | None = None
    domains: list[str] | None = None
    trigger_hints: list[str] | None = None
    knowledge_topics: list[str] | None = None
    allowed_tool_ids: list[str] | None = None
    priority: int | None = None
    max_rounds: int | None = Field(
        default=None,
        ge=1,
    )
    max_actions: int | None = Field(
        default=None,
        ge=0,
    )
    metadata: dict | None = None


class SpecialistEnabledRequest(BaseModel):
    enabled: bool


class SpecialistResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None
    instructions: str | None
    enabled: bool
    domains: list[str]
    trigger_hints: list[str]
    knowledge_topics: list[str]
    allowed_tool_ids: list[str]
    priority: int
    max_rounds: int
    max_actions: int
    metadata: dict = Field(
        validation_alias="specialist_metadata"
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
