"""Create the first local Admin account without printing credentials."""

from __future__ import annotations

import argparse
import getpass
import sys

from app.interfaces.admin.auth import AdminAuthService, AdminRole


def main(argv: list[str] | None = None) -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: argv.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description="Create a persisted local Admin operator account."
    )
    parser.add_argument("--username", required=True)
    parser.add_argument(
        "--role",
        choices=[role.value for role in AdminRole],
        default=AdminRole.ADMIN.value,
    )
    args = parser.parse_args(argv)

    password = getpass.getpass("Admin password: ")
    confirmation = getpass.getpass("Confirm admin password: ")
    if password != confirmation:
        print("ERROR: password confirmation does not match.", file=sys.stderr)
        return 2

    try:
        principal = AdminAuthService().create_admin(
            username=args.username,
            password=password,
            role=args.role,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: unable to create Admin account: {exc}", file=sys.stderr)
        return 1

    print(
        "Admin account created: "
        f"username={principal.username} role={principal.role.value}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
