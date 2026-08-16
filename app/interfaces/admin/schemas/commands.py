"""
جزء من واجهة الإدارة يعرّف route أو payload أو عرضًا للمشغل.

الموقع في المعمارية: Administration interface.
يُستدعى بواسطة: FastAPI أو متصفح الإدارة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: العرض والتحقق الشكلي لا يمنحان صلاحية تنفيذ؛ authorization في الخدمة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Literal


FingerprintStrategyValue = Literal[
    "full_output",
    "status_only",
    "canonical_lines",
    "error_signature",
    "exclude_output",
]

class CommandCreateRequest(BaseModel):
    """
    يمثل CommandCreateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str = Field(
        min_length=1,
        max_length=150,
    )
    fingerprint_strategy: (
        FingerprintStrategyValue
    ) = "full_output"

    fingerprint_config: dict[str, Any] = Field(
        default_factory=dict
    )
    command: str = Field(
        min_length=1,
    )

    description: str | None = None

    timeout_seconds: float = Field(
        default=20,
        gt=0,
    )

    enabled: bool = True


class CommandUpdateRequest(BaseModel):
    """
    يمثل CommandUpdateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    command: str | None = Field(
        default=None,
        min_length=1,
    )

    description: str | None = None

    timeout_seconds: float | None = Field(
        default=None,
        gt=0,
    )

    enabled: bool | None = None


class CommandResponse(BaseModel):
    """
    يمثل CommandResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    id: int
    name: str
    command: str
    description: str | None
    timeout_seconds: float
    enabled: bool
    created_at: datetime
    updated_at: datetime
    fingerprint_strategy: str
    fingerprint_config: dict[str, Any]
    model_config = ConfigDict(
        from_attributes=True
    )


class AssignCommandRequest(BaseModel):
    """
    يمثل AssignCommandRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    execution_order: int = Field(
        default=1,
        ge=1,
    )

    enabled: bool = True

    custom_timeout_seconds: float | None = Field(
        default=None,
        gt=0,
    )


class UpdateCommandAssignmentRequest(BaseModel):
    """
    يمثل UpdateCommandAssignmentRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    execution_order: int | None = Field(
        default=None,
        ge=1,
    )

    enabled: bool | None = None

    custom_timeout_seconds: float | None = Field(
        default=None,
        gt=0,
    )


class ServerCommandAssignmentResponse(BaseModel):
    """
    يمثل ServerCommandAssignmentResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    command_id: int
    name: str
    command: str
    default_timeout_seconds: float

    assignment_id: int
    execution_order: int
    enabled: bool
    custom_timeout_seconds: float | None