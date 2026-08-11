class ClaudeRuntimeError(RuntimeError):
    """Base error for controlled Claude runtime failures."""


class ClaudeStructuredOutputError(ClaudeRuntimeError):
    """Raised when Claude returns output outside the accepted contract."""


class ClaudeToolAccessError(ClaudeRuntimeError):
    """Raised when a request asks for tools that are not enabled."""
