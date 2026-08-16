"""
مشغل acceptance/evaluation ينفذ سيناريوهات readiness أو safety ويجمع نتائج قابلة للمراجعة.

الموقع في المعمارية: Acceptance tooling.
يُستدعى بواسطة: المشغل اليدوي أو CI.
يعتمد مباشرة على: app.composition، app.core.config، app.infrastructure.database.engine.
الحد المعماري: لا يغير policy الإنتاجية؛ ينفذ evaluation خارج runtime المعتاد.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT_TEXT = str(PROJECT_ROOT)

if PROJECT_ROOT_TEXT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_TEXT)


from app.composition import build_container
from app.core.config import settings
from app.infrastructure.database.engine import (
    create_database_tables,
)


def parse_args():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى parse_args؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run one real Ollama-backed Claude monitoring "
            "session for an existing server."
        )
    )
    parser.add_argument(
        "--server-id",
        type=int,
        required=True,
    )
    return parser.parse_args()


def jsonable(value):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى jsonable؛ المدخلات المهمة: value.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if isinstance(value, Enum):
        return value.value

    if is_dataclass(value):
        return {
            key: jsonable(item)
            for key, item in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            str(key): jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]

    return value


def prepare_database_schema() -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى prepare_database_schema؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    # The standalone smoke does not enter FastAPI lifespan.
    # Mirror application startup so newly-added runtime tables exist.
    create_database_tables()


async def main_async(server_id: int) -> int:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى main_async؛ المدخلات المهمة: server_id.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if server_id < 1:
        print("server-id must be a positive integer.")
        return 2

    if not settings.claude_runtime_enabled:
        print(
            "CLAUDE_RUNTIME_ENABLED must be true "
            "for the real C.14.7 smoke test."
        )
        return 2

    if not settings.llm_enabled:
        print(
            "LLM_ENABLED must be true "
            "for the real C.14.7 smoke test."
        )
        return 2

    if settings.llm_provider != "ollama":
        print(
            "LLM_PROVIDER must be ollama for C.14.7."
        )
        return 2

    print(
        "C.14.7 real smoke starting | "
        f"server_id={server_id} | "
        f"model={settings.effective_claude_runtime_model}"
    )

    print(
        "C.14.7 smoke preflight | "
        "initializing missing database tables"
    )
    prepare_database_schema()

    container = build_container()

    result = await container.claude_supervisor.run(
        server_id
    )

    print(
        json.dumps(
            jsonable(result),
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    args = parse_args()
    return asyncio.run(
        main_async(args.server_id)
    )


if __name__ == "__main__":
    raise SystemExit(main())
