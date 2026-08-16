"""
قواعد السلامة التي تحكم جمع الأدلة وتشخيص الأعطال وتطبيق المعالجة.

تحدد هذه الحزمة ما يمكن للمتخصص فحصه، وما يحتاج إلى موافقة، وما الذي يمنع
التغيير حتى لو طلبه النموذج أو اقترحته الخطة.
"""
from app.core.policies.diagnostic_policy import *  # noqa: F401,F403
from app.core.policies.diagnostic_tools import *  # noqa: F401,F403
