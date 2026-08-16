"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.analysis، app.capabilities.investigation، app.runtime.claude، app.runtime.claude.supervisor، app.capabilities.monitoring.service.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import asyncio
import inspect
from pathlib import Path

import pytest

import app.capabilities.analysis as analysis_domain
import app.capabilities.investigation as investigation_domain
import app.runtime.claude as claude_runtime
from app.runtime.claude.supervisor import ClaudeSupervisor
from app.capabilities.monitoring.service import MonitoringService


ROOT = Path(__file__).resolve().parents[1]


LEGACY_PATHS = (
    "app/runtime/claude/monitoring_cycle.py",
    "app/runtime/claude/multi_specialist_supervision.py",
    "app/capabilities/investigation/server_coordinator.py",
    "app/capabilities/analysis/analysis_agent_manager.py",
    "app/capabilities/analysis/server_analysis_agent.py",
    "tools/run_server_coordinator_acceptance.py",
)


def test_c14_9_legacy_python_orchestrators_are_removed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_9_legacy_python_orchestrators_are_removed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    for relative in LEGACY_PATHS:
        assert not (ROOT / relative).exists()


def test_c14_9_monitoring_service_is_execution_only():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_9_monitoring_service_is_execution_only؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    signature = inspect.signature(
        MonitoringService.__init__
    )

    assert (
        "analysis_agent_manager"
        not in signature.parameters
    )
    assert not hasattr(
        MonitoringService,
        "_enqueue_analysis",
    )


def test_c14_9_runtime_exports_only_native_claude_orchestration():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_9_runtime_exports_only_native_claude_orchestration؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert hasattr(
        claude_runtime,
        "ClaudeNativeMonitoringRunner",
    )

    for legacy_name in (
        "ClaudeSupervisedMonitoringCycle",
        "ClaudeMonitoringCycleResult",
        "ClaudeMultiSpecialistSupervisor",
        "ClaudeMultiSpecialistResult",
        "ClaudeSpecialistRunSummary",
    ):
        assert not hasattr(
            claude_runtime,
            legacy_name,
        )


def test_c14_9_domain_packages_drop_old_orchestration_exports():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_9_domain_packages_drop_old_orchestration_exports؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert not hasattr(
        analysis_domain,
        "AnalysisAgentManager",
    )
    assert not hasattr(
        analysis_domain,
        "ServerAnalysisAgent",
    )
    assert not hasattr(
        investigation_domain,
        "ServerCoordinator",
    )


def test_c14_9_supervisor_fails_closed_when_runtime_disabled():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_9_supervisor_fails_closed_when_runtime_disabled؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    supervisor = ClaudeSupervisor(
        runner=None
    )

    assert supervisor.status == {
        "runtime": "claude",
        "state": "disabled",
    }

    with pytest.raises(
        RuntimeError,
        match="CLAUDE_RUNTIME_ENABLED=true",
    ):
        asyncio.run(
            supervisor.run(2)
        )


def test_c14_9_composition_has_no_python_orchestration_fallback():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_9_composition_has_no_python_orchestration_fallback؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    runtime_text = (
        ROOT / "app" / "composition" / "runtime.py"
    ).read_text(
        encoding="utf-8"
    )
    analysis_text = (
        ROOT / "app" / "composition" / "analysis.py"
    ).read_text(
        encoding="utf-8"
    )

    combined = runtime_text + "\n" + analysis_text

    for legacy_name in (
        "ClaudeSupervisedMonitoringCycle",
        "ClaudeMultiSpecialistSupervisor",
        "ServerCoordinator",
        "AnalysisAgentManager",
    ):
        assert legacy_name not in combined

    assert "claude_supervisor_runner = None" in runtime_text
    assert "ClaudeNativeMonitoringRunner(" in runtime_text

    assert "AnalysisOrchestrator(" in analysis_text
    assert "SpecialistInvestigationLoop(" in analysis_text




def test_c14_9_main_has_no_analysis_worker_lifecycle():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_9_main_has_no_analysis_worker_lifecycle؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    text = (
        ROOT / "app" / "main.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "analysis_agent_manager" not in text
    assert "recover_pending_jobs" not in text
    assert "stop_all" not in text
    assert 'status["state"] == "active"' in text
