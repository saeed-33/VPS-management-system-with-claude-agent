from enum import StrEnum


class FingerprintStrategy(StrEnum):
    FULL_OUTPUT = "full_output"
    STATUS_ONLY = "status_only"
    CANONICAL_LINES = "canonical_lines"
    ERROR_SIGNATURE = "error_signature"
    EXCLUDE_OUTPUT = "exclude_output"