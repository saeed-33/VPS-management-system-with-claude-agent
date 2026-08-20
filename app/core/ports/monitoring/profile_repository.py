"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Any, Protocol

from app.core.contracts.profiles.create_monitoring_profile_dto import CreateMonitoringProfileDTO
from app.core.contracts.profiles.monitoring_profile_command_config import MonitoringProfileCommandConfig
from app.core.contracts.profiles.update_monitoring_profile_dto import UpdateMonitoringProfileDTO
from .monitoring_command_record import MonitoringCommandRecord

class MonitoringProfileRepositoryPort(
    Protocol
):
    """
    عقد يجلب الفحوص المفعلة المرتبطة بسيرفر.
    """
    def list_enabled_commands_for_server(
        self,
        server_id: int,
    ) -> list[MonitoringCommandRecord]:
        """
        يعرض بيانات دورة مراقبة السيرفر التي تحتاجها واجهة الإدارة أو الجدولة.
        """
        ...

    def get_by_id(self, profile_id: int) -> Any | None: ...

    def get_by_name(self, name: str) -> Any | None: ...

    def list_all(self) -> list[Any]: ...

    def create(self, data: CreateMonitoringProfileDTO) -> Any: ...

    def update(
        self,
        profile_id: int,
        data: UpdateMonitoringProfileDTO,
    ) -> Any | None: ...

    def delete(self, profile_id: int) -> bool: ...

    def list_profile_commands(self, profile_id: int) -> list[tuple[Any, Any]]: ...

    def assign_command(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int,
        enabled: bool = True,
        custom_timeout_seconds: float | None = None,
    ) -> Any: ...

    def update_command_assignment(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int | None = None,
        enabled: bool | None = None,
        custom_timeout_seconds: float | None = None,
        update_custom_timeout: bool = False,
    ) -> Any | None: ...

    def remove_command(self, *, profile_id: int, command_id: int) -> bool: ...

    def assign_profile_to_server(self, *, server_id: int, profile_id: int | None) -> Any | None: ...

    def count_servers(self, profile_id: int) -> int: ...
