"""Knowledge capability package with lazy public exports."""

from importlib import import_module

_MODULES = (
    "chunker",
    "chunking_service",
    "indexer",
    "ingestion_contracts",
    "ingestion_service",
    "parsers",
    "retrieval",
    "source_loader",
    "source_registry",
)


def __getattr__(name: str):
    for module_name in _MODULES:
        module = import_module(f"{__name__}.{module_name}")
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
