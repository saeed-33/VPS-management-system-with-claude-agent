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


class ServerCreateRequest(BaseModel):
    """
    يمثل ServerCreateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    host: str = Field(
        min_length=1,
        max_length=255,
    )

    port: int = Field(
        default=22,
        ge=1,
        le=65535,
    )

    username: str = Field(
        min_length=1,
        max_length=100,
    )

    private_key_path: str | None = Field(
        default=None,
        max_length=500,
    )

    description: str | None = None

    monitor_enabled: bool = True

    interval_seconds: int = Field(
        default=60,
        ge=5,
    )
    monitoring_profile_id: int | None = None


class ServerUpdateRequest(BaseModel):
    """
    يمثل ServerUpdateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )

    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    private_key_path: str | None = None
    description: str | None = None
    monitor_enabled: bool | None = None

    interval_seconds: int | None = Field(
        default=None,
        ge=5,
    )


class ServerResponse(BaseModel):
    """
    يمثل ServerResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    id: int
    name: str
    host: str
    port: int
    username: str

    private_key_path: str | None
    description: str | None

    monitor_enabled: bool
    interval_seconds: int
    status: str

    last_checked_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    last_report_id: int | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    monitoring_profile_id: int | None
    safety_designation: str = "unclassified"


class SSHTestResponse(BaseModel):
    """
    يمثل SSHTestResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    success: bool
    message: str
    hostname: str | None = None
