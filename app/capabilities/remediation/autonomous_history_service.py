"""
جزء من Remediation من التشخيص والاقتراح حتى sandbox/authorization والتنفيذ.

الموقع في المعمارية: Application capability / remediation.
يُستدعى بواسطة: Admin API أو MCP.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation.
الحد المعماري: لا يسمح write operation بمجرد اقتراح LLM.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.core.contracts.autonomous_remediation import AutonomousHistorySnapshot


class AutonomousHistoryService:
    """
    يمثل AutonomousHistoryService مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, *, repository) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def snapshot(self, *, issue_fingerprint: str, action_type: str, target: str) -> AutonomousHistorySnapshot:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى snapshot؛ المدخلات المهمة: issue_fingerprint، action_type، target.
        تعيد AutonomousHistorySnapshot أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.history(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target)

