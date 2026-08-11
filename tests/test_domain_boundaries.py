from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "app" / "domain"


def test_domain_does_not_import_runtime_or_mcp_boundaries():
    forbidden = (
        "app.runtime",
        "app.mcp",
    )
    offenders = []

    for path in DOMAIN.rglob("*.py"):
        text = path.read_text(
            encoding="utf-8"
        )
        for item in forbidden:
            if item in text:
                offenders.append(
                    f"{path.relative_to(ROOT)}: {item}"
                )

    assert offenders == []
