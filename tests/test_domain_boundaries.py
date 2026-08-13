from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
def test_removed_domain_package_has_no_boundary_to_audit():
    assert not (ROOT / "app" / "domain").exists()
