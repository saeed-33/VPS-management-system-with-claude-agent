"""Port required to load servers for investigation evidence collection."""

from __future__ import annotations

from typing import Protocol

from .server_record import InvestigationServerRecord


class InvestigationServerRepositoryPort(Protocol):
    """
    يعرّف عملية جلب السيرفر لجمع الأدلة.
    """
    def get_by_id(
        self,
        server_id: int,
    ) -> InvestigationServerRecord | None:
        """
        يجلب سجل سيرفر حسب المعرف من أجل جمع الدليل.
        """
        ...
