from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import cast

from maybetype import Maybe, Nothing, Some
from maybetype.errors import ResultUnwrapError


class Result[T, E]:
    __match_args__ = ('_val',)

    def __init__(self, val: T | E) -> None:
        warnings.warn(
            'Direct instancing of Result is not intended and may cause unexpected behavior,'
            + ' instance Ok or Err instead',
            stacklevel=2,
        )
        self._val: T | E = val

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._val!r})'

    def __hash__(self) -> int:
        return hash((self.__class__, self._val))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return False
        return hash(self) == hash(other)

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Returns ``func`` called with the wrapped value if ``Ok``, otherwise returns this instance."""
        if self:
            return func(cast(T, self._val))
        return cast(Result[U, E], self)

    def err(self) -> Maybe[E]:
        """Returns a ``Some`` with the wrapped value if ``Err``, otherwise returns ``Nothing``."""
        if self:
            return Nothing
        return Some(self._val)

    def unwrap(self) -> T:
        """
        Returns the wrapped value if ``Ok``, otherwise raises ``ResultUnwrapError`` with the wrapped value as the
        exception argument.
        """
        if self:
            return cast(T, self._val)
        raise ResultUnwrapError(self._val)

class Ok[T](Result):
    def __init__(self, val: T) -> None:
        self._val: T = val

    def __bool__(self) -> bool:
        return True

class Err[E](Result):
    def __init__(self, val: E) -> None:
        self._val: E = val

    def __bool__(self) -> bool:
        return False
