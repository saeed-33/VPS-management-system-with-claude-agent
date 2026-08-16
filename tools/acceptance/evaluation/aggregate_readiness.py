"""
مشغل acceptance/evaluation ينفذ سيناريوهات readiness أو safety ويجمع نتائج قابلة للمراجعة.

الموقع في المعمارية: Acceptance tooling.
يُستدعى بواسطة: المشغل اليدوي أو CI.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يغير policy الإنتاجية؛ ينفذ evaluation خارج runtime المعتاد.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass

from tools.acceptance.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
    ProductionReadinessResult,
)
from tools.acceptance.evaluation.readiness_gate import (
    ProductionReadinessGate,
)


@dataclass(slots=True, frozen=True)
class AggregateEvaluationResult:
    """
    يمثل AggregateEvaluationResult جزءًا من طبقة Acceptance tooling.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه المشغل اليدوي أو CI. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    persisted_observations: tuple[
        EvaluationObservation,
        ...
    ]
    safety_observations: tuple[
        EvaluationObservation,
        ...
    ]
    observations: tuple[
        EvaluationObservation,
        ...
    ]
    readiness: ProductionReadinessResult
    sample_deficits: dict[
        EvaluationMetric,
        int,
    ]


class AggregateReadinessEvaluator:
    """
    يمثل AggregateReadinessEvaluator جزءًا من طبقة Acceptance tooling.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه المشغل اليدوي أو CI. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(
        self,
        *,
        gate: ProductionReadinessGate
        | None = None,
    ) -> None:
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: gate.
        تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self._gate = (
            gate
            or ProductionReadinessGate()
        )

    def evaluate(
        self,
        *,
        persisted_observations: tuple[
            EvaluationObservation,
            ...
        ],
        safety_observations: tuple[
            EvaluationObservation,
            ...
        ],
    ) -> AggregateEvaluationResult:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى evaluate؛ المدخلات المهمة: persisted_observations، safety_observations.
        تعيد AggregateEvaluationResult أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        observations = (
            *persisted_observations,
            *safety_observations,
        )

        readiness = self._gate.evaluate(
            observations
        )

        deficits = {}

        for metric in readiness.metrics:
            deficits[metric.metric] = max(
                0,
                metric.required_samples
                - metric.samples,
            )

        return AggregateEvaluationResult(
            persisted_observations=(
                persisted_observations
            ),
            safety_observations=(
                safety_observations
            ),
            observations=tuple(
                observations
            ),
            readiness=readiness,
            sample_deficits=deficits,
        )
