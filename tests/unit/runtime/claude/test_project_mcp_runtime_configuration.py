"""Tests for test project mcp runtime configuration.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    """
    يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى read_json؛ المدخلات المهمة: path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def test_vps_project_mcp_is_explicitly_approved():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_vps_project_mcp_is_explicitly_approved؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    settings = read_json(
        ROOT / ".claude" / "settings.json"
    )

    enabled = settings.get(
        "enabledMcpjsonServers",
        [],
    )

    assert "vps" in enabled
    assert (
        settings.get(
            "enableAllProjectMcpServers",
            False,
        )
        is False
    )


def test_vps_mcp_launch_is_project_root_stable():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_vps_mcp_launch_is_project_root_stable؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    config = read_json(
        ROOT / ".mcp.json"
    )

    server = config["mcpServers"]["vps"]

    assert server["command"] == "uv"
    assert server["args"] == [
        "run",
        "--no-sync",
        "--project",
        "${CLAUDE_PROJECT_DIR:-.}",
        "python",
        (
            "${CLAUDE_PROJECT_DIR:-.}/"
            "tools/run_project_mcp_server.py"
        ),
    ]

    assert server["env"]["PYTHONUNBUFFERED"] == "1"
    assert server["env"]["UV_NO_PROGRESS"] == "1"
