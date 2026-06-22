class MaybeInitError(Exception):
    """Raised when creating a ``Maybe`` object directly."""
class NothingTypeInitError(Exception):
    """Raised when calling ``NothingType.__init__()`` for a second time instead of using the ``Nothing`` singleton."""
class ResultInitError(Exception):
    """Raised when creating a ``Result`` object directly."""
class ResultUnwrapError(Exception):
    """Raised when calling ``Result.unwrap()`` if the instance is not ``Ok``."""
