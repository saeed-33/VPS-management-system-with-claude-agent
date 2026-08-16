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

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class MonitoringProfileCreateRequest(BaseModel):
    """
    يمثل MonitoringProfileCreateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None
    enabled: bool = True


class MonitoringProfileUpdateRequest(BaseModel):
    """
    يمثل MonitoringProfileUpdateRequest مسؤولية محددة داخل طبقة Administration interface.

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

    description: str | None = None
    enabled: bool | None = None


class MonitoringProfileResponse(BaseModel):
    """
    يمثل MonitoringProfileResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
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
    """
    يمثل AssignProfileCommandRequest مسؤولية محددة داخل طبقة Administration interface.

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


class UpdateProfileCommandRequest(BaseModel):
    """
    يمثل UpdateProfileCommandRequest مسؤولية محددة داخل طبقة Administration interface.

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
    custom_timeout_seconds: float | None = None


class ProfileCommandResponse(BaseModel):
    """
    يمثل ProfileCommandResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
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
    """
    يمثل AssignServerProfileRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    profile_id: int | None