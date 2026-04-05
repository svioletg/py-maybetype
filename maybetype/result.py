from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Any, Never, Self, cast

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

    def cast[U, F](self, t_type: type[U], e_type: type[F]) -> Result[U, F]:
        """Returns a reference to this instance after casting its type as ``Result[t_type, e_type]``."""
        return cast(Result[U, F], self)

    def err(self) -> Maybe[E]:
        """Returns a ``Some`` with the wrapped value if ``Err``, otherwise returns ``Nothing``."""
        if self:
            return Nothing
        return Some(self._val)

    def flatten(self) -> Result[T, E]:
        """
        Returns a new ``Result[T, E]`` from a``Result[Result[T, E], E]``. Only flattens one level at a time, and will
        raise a ``TypeError`` if called when the wrapped value is not ``Result``.

        .. note::
            It's expected that the resulting type of this method may not be correctly inferred and will return
            returning ``Result[Unknown, Unknown]``. For now, :py:meth:`cast` can be used to specify a type for type
            checkers.

        :raises TypeError:
            The wrapped value is not ``Result``.
        """
        if not isinstance(self._val, Result):
            raise TypeError(f'Cannot flatten when wrapped value is not of type Result: {self!r}')
        return self._val

    def inspect(self, func: Callable[[T], Any]) -> Self:
        """Calls a function with the wrapped value if ``Ok``, otherwise does nothing. Returns this instance."""
        if self:
            func(cast(T, self._val))
        return self

    def inspect_err(self, func: Callable[[E], Any]) -> Self:
        """Calls a function with the wrapped value if ``Err``, otherwise does nothing. Returns this instance."""
        if self:
            func(cast(E, self._val))
        return self

    def ok(self) -> Maybe[E]:
        """Returns a ``Some`` with the wrapped value if ``Ok``, otherwise returns ``Nothing``."""
        if not self:
            return Nothing
        return Some(self._val)

    def _unwrap_fail(self, exc: str | type[Exception] | Callable[[E], Never]) -> Never:
        if isinstance(exc, str):
            raise ResultUnwrapError(f'{exc}: {self._val!r}')
        if isinstance(exc, type) and issubclass(exc, Exception):
            raise exc(repr(self._val))
        if isinstance(exc, Callable):
            exc(cast(E, self._val))
        raise TypeError(f'Unexpected type for unwrap argument exc: {exc!r}')

    def unwrap(self, exc: str | type[Exception] | Callable[[E], Never] = ResultUnwrapError) -> T:
        """
        Returns the wrapped value if ``Ok``, otherwise raises an error according to ``exc`` with the wrapped value as
        the passed argument if ``exc`` is callable.

        :param exc: If ``None``, a ``ResultUnwrapError`` is raised with the wrapped value as the exception message.
            If given a string, ``ResultUnwrapError`` is raised with the message format ``{msg}: {repr(val)}``, where
            ``val`` is the wrapped ``Err`` value.
            If given an ``Exception`` type, that type of exception is raised with the wrapped value as the exception
            argument.
            If given a ``Callable``, ``exc`` is called with the wrapped value as the passed argument.
        """
        if self:
            return cast(T, self._val)
        return self._unwrap_fail(exc)

    def unwrap_err(self, exc: str | type[Exception] | Callable[[E], Never] = ResultUnwrapError) -> E:
        """
        Returns the wrapped value if ``Err``, otherwise raises an error according to ``exc`` with the wrapped value as
        the passed argument if ``exc`` is callable.

        :param exc: If ``None``, a ``ResultUnwrapError`` is raised with the wrapped value as the exception message.
            If given a string, ``ResultUnwrapError`` is raised with the message format ``{msg}: {repr(val)}``, where
            ``val`` is the wrapped ``Ok`` value.
            If given an ``Exception`` type, that type of exception is raised with the wrapped value as the exception
            argument.
            If given a ``Callable``, ``exc`` is called with the wrapped value as the passed argument.
        """
        if not self:
            return cast(E, self._val)
        return self._unwrap_fail(exc)

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
