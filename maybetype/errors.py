class ResultUnwrapError(Exception):
    """Raised when calling ``Result.unwrap()`` if the instance is not ``Ok``."""
