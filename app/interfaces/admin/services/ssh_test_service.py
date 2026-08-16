"""
جزء من واجهة الإدارة يعرّف route أو payload أو عرضًا للمشغل.

الموقع في المعمارية: Administration interface.
يُستدعى بواسطة: FastAPI أو متصفح الإدارة.
يعتمد مباشرة على: app.infrastructure.ssh.client، app.infrastructure.ssh.command_executor، app.infrastructure.database.repositories.server_repository، app.core.exceptions.
الحد المعماري: العرض والتحقق الشكلي لا يمنحان صلاحية تنفيذ؛ authorization في الخدمة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from dataclasses import dataclass

from app.infrastructure.ssh.client import (
    SSHClient,
    SSHConnectionConfig,
)
from app.infrastructure.ssh.command_executor import (
    SSHCommandExecutor,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.core.exceptions import ServerNotFoundError


@dataclass(slots=True, frozen=True)
class SSHTestResult:
    """
    يمثل SSHTestResult مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    success: bool
    message: str
    hostname: str | None = None


class SSHTestService:
    """
    يمثل SSHTestService مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        server_repository: ServerRepository,
        default_private_key_path: str,
        known_hosts_path: str,
        connect_timeout_seconds: float,
        command_timeout_seconds: float,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Administration interface.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: server_repository، default_private_key_path، known_hosts_path، connect_timeout_seconds، command_timeout_seconds.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._server_repository = server_repository
        self._default_private_key_path = (
            default_private_key_path
        )
        self._known_hosts_path = known_hosts_path
        self._connect_timeout_seconds = (
            connect_timeout_seconds
        )
        self._command_timeout_seconds = (
            command_timeout_seconds
        )

    async def test(
        self,
        server_id: int,
    ) -> SSHTestResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

        تُستدعى عندما يصل workflow إلى test؛ المدخلات المهمة: server_id.
        تعيد SSHTestResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        server = self._server_repository.get_by_id(
            server_id
        )

        if server is None:
            raise ServerNotFoundError(server_id)

        private_key_path = (
            server.private_key_path
            or self._default_private_key_path
        )

        config = SSHConnectionConfig(
            host=server.host,
            port=server.port,
            username=server.username,
            private_key_path=private_key_path,
            known_hosts_path=self._known_hosts_path,
            connect_timeout_seconds=(
                self._connect_timeout_seconds
            ),
        )

        try:
            async with SSHClient(config) as client:
                executor = SSHCommandExecutor(client)

                result = await executor.execute(
                    command_id=None,
                    command_name="SSH connection test",
                    command_text="hostname",
                    execution_order=1,
                    timeout_seconds=(
                        self._command_timeout_seconds
                    ),
                    fingerprint_strategy="ssh_connection_test",
                    fingerprint_config={
                        "command_name": "hostname",
                        "purpose": "admin_ssh_connectivity_test",
                    },
                )

            if not result.success:
                return SSHTestResult(
                    success=False,
                    message=(
                        result.error_message
                        or result.stderr
                        or "SSH test failed."
                    ),
                )

            return SSHTestResult(
                success=True,
                message="SSH connection succeeded.",
                hostname=result.stdout.strip(),
            )

        except Exception as exc:
            return SSHTestResult(
                success=False,
                message=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )
