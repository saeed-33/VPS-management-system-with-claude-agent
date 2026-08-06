from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class MonitoringProfileCreateRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None
    enabled: bool = True


class MonitoringProfileUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None
    enabled: bool | None = None


class MonitoringProfileResponse(BaseModel):
    id: int
    name: str
    description: str | None
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AssignProfileCommandRequest(BaseModel):
    execution_order: int = Field(
        default=1,
        ge=1,
    )

    enabled: bool = True

    custom_timeout_seconds: float | None = Field(
        default=None,
        gt=0,
    )


class UpdateProfileCommandRequest(BaseModel):
    execution_order: int | None = Field(
        default=None,
        ge=1,
    )

    enabled: bool | None = None
    custom_timeout_seconds: float | None = None


class ProfileCommandResponse(BaseModel):
    assignment_id: int
    command_id: int
    name: str
    command: str
    description: str | None
    default_timeout_seconds: float

    execution_order: int
    enabled: bool
    custom_timeout_seconds: float | None


class AssignServerProfileRequest(BaseModel):
    profile_id: int | None