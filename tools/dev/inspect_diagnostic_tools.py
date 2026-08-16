"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.core.policies.diagnostic_tools، app.composition.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from app.core.policies.diagnostic_tools import (
    build_default_diagnostic_tool_registry,
)
from app.composition import container


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--specialist",
    )
    args = parser.parse_args()

    registry = (
        build_default_diagnostic_tool_registry()
    )

    print()
    print(
        "Diagnostic Tool Registry"
    )
    print("=" * 120)

    definitions = registry.definitions

    if args.specialist:
        specialist = (
            container
            .specialist_registry
            .get_by_slug(
                args.specialist
            )
        )

        if specialist is None:
            raise SystemExit(
                f"Enabled Specialist not found: {args.specialist}"
            )

        definitions = (
            registry.allowed_for_specialist(
                specialist.allowed_tool_ids
            )
        )

        print(
            f"Specialist: {specialist.slug}"
        )
        print(
            "Allowed IDs: "
            + (
                ", ".join(
                    specialist.allowed_tool_ids
                )
                or "—"
            )
        )
        print()

    print(
        f"{'TOOL ID':24} "
        f"{'TIMEOUT':8} "
        f"{'SUDO':5} "
        f"{'RISK':10} "
        f"{'DOMAINS':38} "
        "COMMAND"
    )
    print("-" * 150)

    for item in definitions:
        try:
            example_arguments = {}

            for parameter in item.parameters:
                if parameter.default is not None:
                    example_arguments[
                        parameter.name
                    ] = parameter.default
                elif parameter.kind.value == "service":
                    example_arguments[
                        parameter.name
                    ] = "nginx"
                elif parameter.kind.value == "host":
                    example_arguments[
                        parameter.name
                    ] = "127.0.0.1"
                elif parameter.kind.value == "port":
                    example_arguments[
                        parameter.name
                    ] = 80
                elif parameter.kind.value == "path":
                    example_arguments[
                        parameter.name
                    ] = "/"

            command = item.render_command(
                example_arguments
            )
        except Exception:
            command = "—"

        print(
            f"{item.tool_id:24} "
            f"{item.timeout_seconds:<8g} "
            f"{str(item.requires_sudo):5} "
            f"{item.risk.value:10} "
            f"{','.join(item.domains)[:38]:38} "
            f"{command}"
        )

    print()
    print(
        f"Tools: {len(definitions)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
