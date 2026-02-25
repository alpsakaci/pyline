class PyLineError(Exception):
    """Base exception for all PyLine framework errors."""
    pass

class HandlerNotFoundError(PyLineError):
    """Raised when a handler cannot be found for a given command or query type."""
    pass

class PipelineError(PyLineError):
    """Raised when a pipeline configuration is invalid or execution fails."""
    pass
