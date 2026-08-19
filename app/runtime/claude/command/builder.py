"""عقد بناء أمر عملية Claude."""
from typing import Protocol

from app.runtime.claude.models.runtime_request import ClaudeRuntimeRequest

from .process_command import ClaudeProcessCommand

class ClaudeProcessCommandBuilder(Protocol):
    """
    عقد يبني أمر العملية من طلب جلسة Claude قبل تشغيلها.
    """
    def build(self, request: ClaudeRuntimeRequest) -> ClaudeProcessCommand:
        """
        ينشئ وصف العملية من طلب الجلسة، بما في ذلك البرنامج والمجلد ومتغيرات البيئة.
        """
