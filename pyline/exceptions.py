class PyLineError(Exception):
    """Base exception for PyLine framework."""
    pass

class HandlerNotFoundError(PyLineError):
    """Raised when a handler is not found for a command or query."""
    pass

class PipelineError(PyLineError):
    """Raised when a pipeline configuration or execution fails."""
    pass
