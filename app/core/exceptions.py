"""أخطاء المجال الأساسية التي تشرح سبب توقف رحلة إدارة السيرفر.

تفرق الأنواع بين سجل غير موجود، وكيان مكرر، وعملية غير مسموحة، حتى تعرض
الواجهات سبب الفشل الصحيح ولا تحوله إلى خطأ عام غير مفيد."""
class ApplicationError(Exception):
    """
    الخطأ الأساسي الذي يمكن لخدمات التطبيق إرجاعه كفشل معروف للمستخدم.
    """


class EntityNotFoundError(ApplicationError):
    """
    أساس أخطاء البحث عندما لا يجد التطبيق سجلًا تحتاجه العملية الحالية.
    """


class ServerNotFoundError(EntityNotFoundError):
    """
    يوضح أن السيرفر المطلوب للمراقبة أو الإدارة غير موجود.
    """
    def __init__(self, server_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف السيرفر المطلوب."""
        super().__init__(
            f"Server with id {server_id} was not found."
        )


class CommandNotFoundError(EntityNotFoundError):
    """
    يوضح أن فحص المراقبة المطلوب غير موجود.
    """
    def __init__(self, command_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف أمر المراقبة المطلوب."""
        super().__init__(
            f"Monitoring command with id "
            f"{command_id} was not found."
        )


class ReportNotFoundError(EntityNotFoundError):
    """
    يوضح أن تقرير المراقبة الذي يعتمد عليه التحليل غير موجود.
    """
    def __init__(self, report_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف تقرير المراقبة المطلوب."""
        super().__init__(
            f"Monitoring report with id "
            f"{report_id} was not found."
        )


class DuplicateEntityError(ApplicationError):
    """
    أساس أخطاء محاولة إنشاء سجل يملك هوية مستخدمة مسبقًا.
    """


class DuplicateServerError(DuplicateEntityError):
    """
    يوضح أن اسم السيرفر مستخدم في سجل آخر.
    """
    def __init__(self, name: str) -> None:
        """ينشئ رسالة تربط التعارض باسم السيرفر المكرر."""
        super().__init__(
            f"A server named '{name}' already exists."
        )


class DuplicateCommandError(DuplicateEntityError):
    """
    يوضح أن اسم أمر المراقبة مستخدم في سجل آخر.
    """
    def __init__(self, name: str) -> None:
        """ينشئ رسالة تربط التعارض باسم أمر المراقبة المكرر."""
        super().__init__(
            f"A monitoring command named "
            f"'{name}' already exists."
        )


class InvalidOperationError(ApplicationError):
    """
    يوضح أن الطلب مفهوم لكنه يخالف حالة المجال الحالية.
    """


class CommandAlreadyAssignedError(
    InvalidOperationError
):
    """
    يوضح أن أمر المراقبة مرتبط بالسيرفر نفسه مسبقًا.
    """
    def __init__(
        self,
        server_id: int,
        command_id: int,
    ) -> None:
        """ينشئ رسالة تربط التعارض بمعرفي السيرفر والأمر."""
        super().__init__(
            f"Command {command_id} is already assigned "
            f"to server {server_id}."
        )
class MonitoringProfileNotFoundError(
    EntityNotFoundError
):
    """
    يوضح أن ملف المراقبة المطلوب للسيرفر غير موجود.
    """
    def __init__(self, profile_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف ملف المراقبة المطلوب."""
        super().__init__(
            f"Monitoring profile with id "
            f"{profile_id} was not found."
        )


class DuplicateMonitoringProfileError(
    DuplicateEntityError
):
    """
    يوضح أن اسم ملف المراقبة مستخدم مسبقًا.
    """
    def __init__(self, name: str) -> None:
        """ينشئ رسالة تربط التعارض باسم ملف المراقبة المكرر."""
        super().__init__(
            f"A monitoring profile named "
            f"'{name}' already exists."
        )


class ProfileCommandNotFoundError(
    EntityNotFoundError
):
    """
    يوضح أن أمر المراقبة غير مرتبط بملف المراقبة المطلوب.
    """
    def __init__(
        self,
        profile_id: int,
        command_id: int,
    ) -> None:
        """ينشئ رسالة تربط الفشل بمعرفي الملف والأمر."""
        super().__init__(
            f"Command {command_id} is not assigned "
            f"to monitoring profile {profile_id}."
        )

class SpecialistDefinitionNotFoundError(
    EntityNotFoundError
):
    """
    يوضح أن تعريف المتخصص المطلوب للتحقيق غير موجود.
    """
    def __init__(self, specialist_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف تعريف المتخصص."""
        super().__init__(
            f"Specialist definition with id "
            f"{specialist_id} was not found."
        )


class DuplicateSpecialistDefinitionError(
    DuplicateEntityError
):
    """
    يوضح أن معرف المتخصص النصي مستخدم مسبقًا.
    """
    def __init__(self, slug: str) -> None:
        """ينشئ رسالة تربط التعارض بالمعرف النصي المكرر."""
        super().__init__(
            f"A specialist with slug '{slug}' already exists."
        )
