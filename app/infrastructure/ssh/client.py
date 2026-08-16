"""
Adapter لاتصال SSH وتنفيذ أوامر Linux مع timeouts ونتائج منظمة.

الموقع في المعمارية: External execution infrastructure.
يُستدعى بواسطة: Monitoring أو خدمات اختبار الاتصال.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يختار profile ولا يقرر remediation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

import asyncssh


@dataclass(slots=True, frozen=True)
class SSHConnectionConfig:
    """
    يمثل SSHConnectionConfig مسؤولية محددة داخل طبقة External execution infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Monitoring أو خدمات اختبار الاتصال
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    host: str
    port: int
    username: str

    private_key_path: str
    known_hosts_path: str

    connect_timeout_seconds: float = 15.0


class SSHClient:
    """
    مسؤول عن دورة حياة اتصال SSH واحد.

    لا ينفذ منطق المراقبة ولا يحفظ النتائج في قاعدة البيانات.
    """

    def __init__(
        self,
        config: SSHConnectionConfig,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: config.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._config = config
        self._connection: (
            asyncssh.SSHClientConnection | None
        ) = None

    @property
    def connection(
        self,
    ) -> asyncssh.SSHClientConnection:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى connection؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد asyncssh.SSHClientConnection أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if self._connection is None:
            raise RuntimeError(
                "SSH connection is not open."
            )

        return self._connection

    @property
    def is_connected(self) -> bool:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى is_connected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._connection is not None

    async def connect(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى connect؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if self._connection is not None:
            return

        private_key_path = Path(
            self._config.private_key_path
        )

        known_hosts_path = Path(
            self._config.known_hosts_path
        )

        if not private_key_path.is_file():
            raise FileNotFoundError(
                f"SSH private key does not exist: "
                f"{private_key_path}"
            )

        if not known_hosts_path.is_file():
            raise FileNotFoundError(
                f"SSH known_hosts file does not exist: "
                f"{known_hosts_path}"
            )

        self._connection = await asyncssh.connect(
            host=self._config.host,
            port=self._config.port,
            username=self._config.username,
            client_keys=[str(private_key_path)],
            known_hosts=str(known_hosts_path),
            connect_timeout=(
                self._config.connect_timeout_seconds
            ),
        )

    async def close(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى close؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if self._connection is None:
            return

        self._connection.close()
        await self._connection.wait_closed()

        self._connection = None

    async def __aenter__(self) -> "SSHClient":
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى __aenter__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد 'SSHClient' أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى __aexit__؛ المدخلات المهمة: exc_type، exc_value، traceback.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        await self.close()