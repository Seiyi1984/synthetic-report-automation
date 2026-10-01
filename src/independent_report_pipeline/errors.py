"""Stable failure types for fail-closed input handling."""


class PipelineInputError(ValueError):
    """A known input failure that must prevent report generation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
