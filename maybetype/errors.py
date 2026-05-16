class MaybeInstanceWarning(Warning):
    """Emitted when creating a ``Maybe`` object directly."""
class ResultInstanceWarning(Warning):
    """Emitted when creating a ``Result`` object directly."""
class NothingTypeInitWarning(Warning):
    """Emitted when calling ``NothingType.__init__()`` for a second time instead of using the ``Nothing`` singleton."""

class ResultUnwrapError(Exception):
    """Raised when calling ``Result.unwrap()`` if the instance is not ``Ok``."""
