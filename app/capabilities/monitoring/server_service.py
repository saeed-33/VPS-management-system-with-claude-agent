"""
إدارة هوية السيرفر وإعدادات الاتصال وتفعيل المراقبة الخاصة به.
"""
from app.infrastructure.database.models.server import (
    ServerModel,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.core.contracts.servers import (
    CreateServerDTO,
    UpdateServerDTO,
)
from app.core.exceptions import (
    DuplicateServerError,
    ServerNotFoundError,
)


class ServerService:
    """
    خدمة تنشئ وتعدل وتحذف السيرفرات وتتحقق من بيانات الاتصال الأولية.
    """
    def __init__(
        self,
        repository: ServerRepository,
    ) -> None:
        """
        يربط خدمة السيرفر بمستودع السيرفر وملفات المراقبة.
        """
        self._repository = repository

    def list_servers(self) -> list[ServerModel]:
        """
        يعرض السيرفرات المسجلة لإدارة الاتصال والمراقبة.
        """
        return self._repository.list_all()

    def get_server(
        self,
        server_id: int,
    ) -> ServerModel:
        """
        يسترجع سيرفرًا محددًا أو يوضح عدم وجوده.
        """
        server = self._repository.get_by_id(
            server_id
        )

        if server is None:
            raise ServerNotFoundError(server_id)

        return server

    def create_server(
        self,
        data: CreateServerDTO,
    ) -> ServerModel:
        """
        ينشئ سجل سيرفر بعد التحقق من بيانات الاتصال وملف المراقبة.
        """
        self._validate_create(data)

        existing = self._repository.get_by_name(
            data.name.strip()
        )

        if existing is not None:
            raise DuplicateServerError(data.name)

        return self._repository.create(data)

    def update_server(
        self,
        server_id: int,
        data: UpdateServerDTO,
    ) -> ServerModel:
        """
        يحدث بيانات السيرفر أو إعداد المراقبة مع الحفاظ على تقاريره.
        """
        existing = self._repository.get_by_id(
            server_id
        )

        if existing is None:
            raise ServerNotFoundError(server_id)

        if (
            data.name is not None
            and data.name.strip() != existing.name
        ):
            duplicate = (
                self._repository.get_by_name(
                    data.name.strip()
                )
            )

            if duplicate is not None:
                raise DuplicateServerError(
                    data.name
                )

        updated = self._repository.update(
            server_id,
            data,
        )

        if updated is None:
            raise ServerNotFoundError(server_id)

        return updated

    def delete_server(
        self,
        server_id: int,
    ) -> None:
        """
        يحذف سيرفرًا عندما تسمح سجلاته وعلاقاته بذلك.
        """
        deleted = self._repository.delete(
            server_id
        )

        if not deleted:
            raise ServerNotFoundError(server_id)

    @staticmethod
    def _validate_create(
        data: CreateServerDTO,
    ) -> None:
        """
        يتحقق من بيانات الاتصال الأولية قبل إنشاء سجل السيرفر.
        """
        if not data.name.strip():
            raise ValueError(
                "Server name is required."
            )

        if not data.host.strip():
            raise ValueError(
                "Server host is required."
            )

        if not data.username.strip():
            raise ValueError(
                "SSH username is required."
            )

        if not 1 <= data.port <= 65535:
            raise ValueError(
                "SSH port must be between "
                "1 and 65535."
            )

        if data.interval_seconds < 5:
            raise ValueError(
                "Monitoring interval must be "
                "at least 5 seconds."
            )