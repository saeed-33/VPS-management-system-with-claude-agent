from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.routing import APIRoute
from app.main import app


def collect_routes() -> list[dict]:
    result = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        methods = sorted(
            m for m in (route.methods or set())
            if m not in {"HEAD", "OPTIONS"}
        )

        result.append({
            "path": route.path,
            "methods": methods,
            "name": route.name,
            "tags": list(route.tags or []),
            "include_in_schema": bool(route.include_in_schema),
        })

    return sorted(
        result,
        key=lambda item: (
            item["path"],
            ",".join(item["methods"]),
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    routes = collect_routes()

    print()
    print("FastAPI Route Inventory")
    print("=" * 88)
    print(f"{'METHOD':8} {'SCHEMA':6} {'PATH':48} NAME")
    print("-" * 88)

    for route in routes:
        print(
            f"{','.join(route['methods']):8} "
            f"{'yes' if route['include_in_schema'] else 'no':6} "
            f"{route['path']:48} "
            f"{route['name']}"
        )

    print()
    print(f"Total APIRoutes: {len(routes)}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(routes, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"JSON report: {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
