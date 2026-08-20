"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Any, Protocol

from datetime import datetime

from app.core.contracts.servers.create_server_dto import CreateServerDTO
from app.core.contracts.servers.update_server_dto import UpdateServerDTO
from .server_record import ServerRecord

class ServerRepositoryPort(Protocol):
    """
    عقد القراءة والتحديث الذي تحتاجه دورة المراقبة من مستودع السيرفر.
    """
    def get_by_id(
        self,
        server_id: int,
    ) -> ServerRecord | None:
        """
        يسترجع قيمة من دورة مراقبة السيرفر مرتبطة بالمعرف أو المفتاح المطلوب.
        """
        ...

    def get_by_name(self, name: str) -> Any | None: ...

    def list_all(self) -> list[Any]: ...

    def list_enabled_servers(self) -> list[Any]: ...

    def create(self, data: CreateServerDTO) -> Any: ...

    def update(self, server_id: int, data: UpdateServerDTO) -> Any | None: ...

    def delete(self, server_id: int) -> bool: ...

    def update_monitoring_status(
        self,
        *,
        server_id: int,
        status: str,
        checked_at: datetime,
        success_at: datetime | None,
        error_message: str | None,
        report_id: int | None,
    ) -> None:
        """
        يغير حالة أو علاقة في دورة مراقبة السيرفر مع الحفاظ على اتساق السجلات المرتبطة.
        """
        ...
