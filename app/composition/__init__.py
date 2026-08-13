# Application composition root.
# This package owns dependency construction and wiring only.

from app.composition.builder import (
    ApplicationContainer,
    build_container,
)


container = build_container()


__all__ = [
    "ApplicationContainer",
    "build_container",
    "container",
]
