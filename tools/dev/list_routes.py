"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.main.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.routing import (
    APIRoute,
    iter_route_contexts,
)

from app.main import app


def collect_routes() -> list[dict]:
    """
    Return the effective FastAPI APIRoute inventory.

    FastAPI 0.137+ keeps include_router() branches as _IncludedRouter
    objects instead of flattening every route into app.routes.
    iter_route_contexts() is FastAPI's route-tree traversal helper and
    exposes the effective path/method/schema context after inclusion.
    """
    result: list[dict] = []

    for context in iter_route_contexts(
        app.routes
    ):
        original_route = context.original_route

        if not isinstance(
            original_route,
            APIRoute,
        ):
            continue

        methods = sorted(
            method
            for method in (
                context.methods
                or original_route.methods
                or set()
            )
            if method not in {
                "HEAD",
                "OPTIONS",
            }
        )

        path = (
            context.path
            or original_route.path
        )

        name = (
            context.name
            or original_route.name
        )

        include_in_schema = bool(
            getattr(
                context,
                "include_in_schema",
                original_route.include_in_schema,
            )
        )

        tags = list(
            getattr(
                context,
                "tags",
                original_route.tags or [],
            )
            or []
        )

        result.append(
            {
                "path": path,
                "methods": methods,
                "name": name,
                "tags": tags,
                "include_in_schema": (
                    include_in_schema
                ),
            }
        )

    deduplicated = {
        (
            item["path"],
            tuple(item["methods"]),
            item["name"],
        ): item
        for item in result
    }

    return sorted(
        deduplicated.values(),
        key=lambda item: (
            item["path"],
            ",".join(
                item["methods"]
            ),
            item["name"],
        ),
    )


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Print the effective FastAPI route tree, "
            "including routes registered through "
            "include_router()."
        )
    )

    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help=(
            "Optional path to save the "
            "route inventory as JSON."
        ),
    )

    args = parser.parse_args()

    routes = collect_routes()

    print()
    print(
        "FastAPI Route Inventory"
    )
    print("=" * 100)
    print(
        f"{'METHOD':10} "
        f"{'SCHEMA':6} "
        f"{'PATH':56} "
        "NAME"
    )
    print("-" * 100)

    for route in routes:
        print(
            f"{','.join(route['methods']):10} "
            f"{'yes' if route['include_in_schema'] else 'no':6} "
            f"{route['path']:56} "
            f"{route['name']}"
        )

    print()
    print(
        f"Total APIRoutes: "
        f"{len(routes)}"
    )
    print(
        "OpenAPI routes:  "
        f"{sum(
            route['include_in_schema']
            for route in routes
        )}"
    )
    print(
        "Web-only routes: "
        f"{sum(
            not route['include_in_schema']
            for route in routes
        )}"
    )

    if args.json is not None:
        args.json.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        args.json.write_text(
            json.dumps(
                routes,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        print(
            f"JSON report: "
            f"{args.json}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
