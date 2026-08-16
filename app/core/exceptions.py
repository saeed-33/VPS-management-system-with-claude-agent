"""
مكوّن مشترك مثل config أو exceptions أو logging.

الموقع في المعمارية: Core foundation.
يُستدعى بواسطة: الطبقات الأعلى.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يعتمد على capabilities أو infrastructure.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
class ApplicationError(Exception):
    """Base exception for application errors."""


class EntityNotFoundError(ApplicationError):
    """Raised when a database entity is not found."""


class ServerNotFoundError(EntityNotFoundError):
    """
    يمثل ServerNotFoundError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على EntityNotFoundError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, server_id: int) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: server_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"Server with id {server_id} was not found."
        )


class CommandNotFoundError(EntityNotFoundError):
    """
    يمثل CommandNotFoundError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على EntityNotFoundError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, command_id: int) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: command_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"Monitoring command with id "
            f"{command_id} was not found."
        )


class ReportNotFoundError(EntityNotFoundError):
    """
    يمثل ReportNotFoundError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على EntityNotFoundError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, report_id: int) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: report_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"Monitoring report with id "
            f"{report_id} was not found."
        )


class DuplicateEntityError(ApplicationError):
    """Raised when an entity already exists."""


class DuplicateServerError(DuplicateEntityError):
    """
    يمثل DuplicateServerError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على DuplicateEntityError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, name: str) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: name.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"A server named '{name}' already exists."
        )


class DuplicateCommandError(DuplicateEntityError):
    """
    يمثل DuplicateCommandError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على DuplicateEntityError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, name: str) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: name.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"A monitoring command named "
            f"'{name}' already exists."
        )


class InvalidOperationError(ApplicationError):
    """Raised when an operation cannot be performed."""


class CommandAlreadyAssignedError(
    InvalidOperationError
):
    """
    يمثل CommandAlreadyAssignedError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على InvalidOperationError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        server_id: int,
        command_id: int,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: server_id، command_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"Command {command_id} is already assigned "
            f"to server {server_id}."
        )
class MonitoringProfileNotFoundError(
    EntityNotFoundError
):
    """
    يمثل MonitoringProfileNotFoundError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على EntityNotFoundError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, profile_id: int) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: profile_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"Monitoring profile with id "
            f"{profile_id} was not found."
        )


class DuplicateMonitoringProfileError(
    DuplicateEntityError
):
    """
    يمثل DuplicateMonitoringProfileError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على DuplicateEntityError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, name: str) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: name.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"A monitoring profile named "
            f"'{name}' already exists."
        )


class ProfileCommandNotFoundError(
    EntityNotFoundError
):
    """
    يمثل ProfileCommandNotFoundError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على EntityNotFoundError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        profile_id: int,
        command_id: int,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: profile_id، command_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"Command {command_id} is not assigned "
            f"to monitoring profile {profile_id}."
        )

class SpecialistDefinitionNotFoundError(
    EntityNotFoundError
):
    """
    يمثل SpecialistDefinitionNotFoundError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على EntityNotFoundError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, specialist_id: int) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: specialist_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"Specialist definition with id "
            f"{specialist_id} was not found."
        )


class DuplicateSpecialistDefinitionError(
    DuplicateEntityError
):
    """
    يمثل DuplicateSpecialistDefinitionError مسؤولية محددة داخل طبقة Core foundation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه الطبقات الأعلى
    ويعتمد على DuplicateEntityError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, slug: str) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core foundation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: slug.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(
            f"A specialist with slug '{slug}' already exists."
        )
