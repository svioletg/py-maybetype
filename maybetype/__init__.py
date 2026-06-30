"""A basic implementation of a maybe/option type in Python, as well as a Result type."""
from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any, ClassVar, Never, Self, cast, overload, override

from maybetype.errors import MaybeInitError, NothingTypeInitError, ResultInitError, ResultUnwrapError

__version__ = '0.12.0'

class Maybe[T]:
    """Wraps a possible value of type ``T``.

    This is a base class that is subclassed by :py:class:`Some` and :py:class:`NothingType`, and will raise
    :py:class:`errors.MaybeInstanceError` if instanced directly
    """

    __match_args__ = ('_val',)

    _val: T

    def __init__(self, _val: T) -> Never:
        raise MaybeInitError('Maybe is not intended for direct usage, use maybe() or Some/Nothing')

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}({self._val!r})'

    def __bool__(self) -> bool:
        """Returns ``True`` if ``Some``, ``False`` if ``Nothing``."""
        return self is not Nothing

    def __eq__(self, other: object) -> bool:
        """Compares the wrapped values if both are ``Maybe``, otherwise returns ``False``."""
        if not isinstance(other, Maybe):
            return False
        return self._val == other._val

    def __hash__(self) -> int:
        """Returns the hash of the wrapped value."""
        return hash(self._val)

    @staticmethod
    def cat(vals: Iterable[Maybe[T]]) -> list[T]:
        """Takes an iterable of ``Maybe`` objects and returns a list of the unwrapped values of the ``Some`` objects.

        >>> vals = [maybe(5), maybe(None), maybe(10), maybe(None)]
        >>> assert vals == [Some(5), Nothing, Some(10), Nothing]
        >>> assert Maybe.cat(vals) == [5, 10]
        """
        return [i._val for i in vals if i]  # noqa: SLF001

    @staticmethod
    def sequence(vals: Iterable[Maybe[T]]) -> Maybe[list[T]]:
        """Returns ``Nothing`` if any of ``vals`` is ``Nothing``, otherwise returns ``Some`` of a list of unwrapped
        items of ``vals``.

        >>> assert Maybe.sequence([Some(1), Some(2), Some(3)]) == Some([1, 2, 3])
        >>> assert Maybe.sequence([Some(1), Nothing, Some(3)]) is Nothing
        """  # noqa: D205
        unwrapped: list[T] = []
        for i in vals:
            if i is Nothing:
                return Nothing
            unwrapped.append(i._val)  # noqa: SLF001
        return Some(unwrapped)

    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Returns ``func(val)`` if ``Some``, otherwise returns ``Nothing``."""
        return func(self._val) if self else Nothing

    def as_list(self) -> list[T]:
        """Returns a list containing the wrapped value if ``Some``, otherwise returns an empty list."""
        return [self._val] if self else []

    def as_tuple(self) -> tuple[T] | tuple[()]:
        """Returns a tuple containing the wrapped value if ``Some``, otherwise returns an empty tuple."""
        return (self._val,) if self else ()

    def attr[U](self, name: str, default: U | None = None, _typ: type[U] | None = None) -> Maybe[U]:
        """Attempts to access an attribute ``name`` in the wrapped value, returning ``Some`` wrapping the
        the attribute's value if it exists, or ``Nothing`` otherwise.

        :param name: The name of the attribute to access.
        :param default: An optional default value to use if the attribute does not exist, returning ``Some(default)``
            in that case.
        :param typ: Specifies the generic type of the resulting ``Maybe``. This does not affect the value's real type
            at runtime; it is only used for type checkers.
            This is generally unnecessary if the ``default`` parameter is given, as the type will be inferred from its
            value.
        """  # noqa: D205
        try:
            return Some(getattr(self._val, name) if default is None else getattr(self._val, name, default))
        except AttributeError:
            return Nothing

    def cast[U](self, typ: type[U]) -> Maybe[U]:  # noqa: ARG002
        """Returns this instance casted to ``Maybe[typ]``."""
        return cast('Maybe[U]', self)

    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        """Returns ``self`` if it is ``Some`` and ``predicate(val)`` is ``True``, otherwise returns ``Nothing``.

        >>> assert Some(1).filter(lambda n: n > 0).unwrap() == 1
        >>> assert Some(1).filter(lambda n: n > 1) is Nothing
        >>> assert Nothing.filter(lambda n: n > 1) is Nothing
        """
        return self if self and predicate(self._val) else Nothing

    def flatten(self) -> Maybe[T]:
        """Returns a new ``Maybe[T]`` from a ``Maybe[Maybe[T]]``.

        Only flattens one level at a time, and will raise a ``TypeError`` if called when the wrapped value is not
        ``Maybe``.

        .. note::
            It's expected that the resulting type of this method may not be correctly inferred and will return
            returning ``Maybe[Unknown]``. For now, :py:meth:`cast` can be used to specify a type for type checkers.

        :raises TypeError:
            The wrapped value is not ``Maybe``.
        """
        if not isinstance(self._val, Maybe):
            raise TypeError(f'Cannot flatten when wrapped value is not of type Maybe: {self!r}')
        return maybe(cast('T', self._val._val))  # noqa: SLF001

    def get[U](self,
            accessor: object,
            _typ: type[U] | None = None,
            *,
            err: bool = False,
            default: U | None = None,
        ) -> Maybe[U]:
        """Attempts to access an item by ``accessor`` on the wrapped object if it supports ``__getitem__``.

        If it does not, or if the value does not exist (list index out of range, key does not exist on a dictionary,
        etc.), ``Nothing`` is returned.

        :param typ: Specifies the generic type of the resulting ``Maybe``. No conversion is performed; this argument is
            only for typing purposes.
        :param err: Whether to allow ``IndexError`` and ``KeyError`` to propagate from the ``__getitem__`` call. When
            ``False`` (default), these errors are ignored and ``Nothing`` is returned.
        :param default: Specifies an alternate value to return a ``Some`` of instead of returning ``Nothing``.
        """
        default_maybe: Maybe[U] = Nothing if default is None else Some(default)

        if hasattr(self._val, '__getitem__'):
            try:
                return Some(self._val.__getitem__(accessor))  # ty:ignore[call-non-callable]
            except (IndexError, KeyError):
                if err:
                    raise
                return default_maybe

        return default_maybe

    def inspect(self, func: Callable[[T], Any]) -> Self:
        """Calls a function with the wrapped value if ``Some``, otherwise does nothing. Returns this instance."""
        if self:
            func(self._val)
        return self

    def map[U](self, func: Callable[[T], U]) -> Maybe[U]:
        """Returns ``Some(func(val))`` if ``Some``, otherwise ``Nothing``."""
        return Some(func(self._val)) if self else Nothing

    def ok_or[E](self, err: E) -> Result[T, E]:
        """Converts this ``Maybe[T]`` to a ``Result[T, E]``.

        ``Some(val)`` becomes ``Ok(val)``, ``Nothing`` becomes ``Err(err)``.
        """
        return Ok(self._val) if self else Err(err)

    def ok_or_else[E](self, err: Callable[[], E]) -> Result[T, E]:
        """Converts this ``Maybe[T]`` to a ``Result[T, E]``.

        ``Some(val)`` becomes ``Ok(val)``, ``Nothing`` becomes ``Err(err())``.
        """
        return Ok(self._val) if self else Err(err())

    def reduce[U, R](self,
            other: Maybe[U],
            func: Callable[[T, U], R],
            *,
            strict: bool = False,
        ) -> Maybe[T] | Maybe[U] | Maybe[R]:
        """Reduces the values of two ``Maybe`` instances to one value returned in a new ``Maybe`` using ``func``.

        If only one of ``self`` and ``other`` is ``Some``, that instance is returned. If neither are, ``Nothing`` is
        returned.

        >>> assert Some(1).reduce(Some(2), lambda a, b: a + b) == Some(3)
        >>> assert Some(1).reduce(Nothing, lambda a, b: a + b) == Some(1)
        >>> assert Nothing.reduce(Some(2), lambda a, b: a + b) == Some(2)
        >>> assert Nothing.reduce(Nothing, lambda a, b: a + b) is Nothing

        :param strict: If ``True``, returns ``Nothing`` if ``self`` and ``other`` are not both ``Some``.
        """
        if self and other:
            return Some(func(self._val, other._val))
        return Nothing if strict else (self or other)

    def replace(self, new_val: T) -> Maybe[T]:
        """Replaces the wrapped value with ``new_val`` and returns a reference to this same instance if ``Some``."""
        if not self:
            return Nothing
        self._val = new_val
        return self

    def then[U](self, func: Callable[[T], U]) -> U | None:
        """Returns ``func`` called with the wrapped value if ``Some``, otherwise returns ``None``.

        :param func: A ``Callable`` which takes a type of the possible wrapped value (``T``) and can return any type
            (``U``).
        """
        return func(self._val) if self else None

    def transpose[E](self: Maybe[Result[Any, E]]) -> Result[Maybe[Any], E]:
        """Transposes a ``Maybe`` of ``Result`` to a ``Result`` of ``Maybe``.

        ``Some(Ok(x))`` becomes ``Ok(Some(x))``, ``Some(Err(x))`` becomes ``Err(x)``, ``Nothing`` becomes
        ``Ok(Nothing)``.

        >>> assert Some(Ok(1)).transpose()  == Ok(Some(1))
        >>> assert Some(Err(0)).transpose() == Err(0)
        >>> assert Nothing.transpose()      == Ok(Nothing)

        .. note::
            Currently the type information of the wrapped ``Result`` can't be known and used for the return type of
            this method, so it will return ``Result[Maybe[Any], Any]``. You can use the :py:meth:`cast` method to
            work around this for now.

        :raises TypeError:
            The wrapped value is not ``Result``.
        """
        if self is Nothing:
            return Ok(Nothing)
        if not isinstance(self._val, Result):
            raise TypeError(f'Cannot transpose Some instance which does not wrap Result: {self!r}')

        return Ok(Some(self._val._val)) if self._val else Err(self._val._val)  # noqa: SLF001

    def unwrap(self, exc: str | Exception | Callable[[], Never] = 'unwrapped Nothing') -> T:
        """Returns the wrapped value if ``Some``, otherwise raises ``ValueError`` or fails according to ``exc``.

        :param exc: If a string is given, ``ValueError`` is raised with the string as its argument.
            If an ``Exception`` instance is given, it is raised.
            If a ``Callable`` is given, it is called with no arguments.
        """
        if not self:
            if isinstance(exc, str):
                raise ValueError(exc)
            if isinstance(exc, Exception):
                raise exc
            if isinstance(exc, Callable):
                exc()
            raise ValueError('unwrapped Nothing')
        return self._val

    def unwrap_or(self, other: T) -> T:
        """Returns the wrapped value if ``Some``, otherwise returns ``other``."""
        return self._val if self else other

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Returns the wrapped value if ``Some``, otherwise returns the result of calling ``func``."""
        return self._val if self else func()

    def unzip[U](self) -> tuple[Maybe[T], Maybe[U]]:
        """Returns ``(Some(a), Some(b))`` if the wrapped value is a tuple of two items.

        If ``Nothing``, ``(Nothing, Nothing)`` is returned.

        :raises TypeError:
            The wrapped value is not a 2-tuple.
        """
        if isinstance(self._val, tuple) and (len(self._val) == 2):  # noqa: PLR2004
            return (Some(self._val[0]), Some(self._val[1]))
        if not self:
            return (Nothing, Nothing)
        raise TypeError(f'Cannot unzip Maybe if the wrapped value is not a 2-tuple: {self!r}')

    def xor(self, other: Maybe[T]) -> Maybe[T]:
        """Returns ``Some`` if exactly one of ``self`` and ``other`` is ``Some``, otherwise returns ``Nothing``."""
        return Nothing if self and other else self or other

    def zip[U](self, other: Maybe[U]) -> Maybe[tuple[T, U]]:
        """Returns ``Some`` wrapping a tuple of ``self`` and ``other``'s values if both are ``Some``, otherwise returns
        ``Nothing``.
        """  # noqa: D205
        return Some((self._val, other._val)) if self and other else Nothing

class NothingType(Maybe):
    """Subclass of ``Maybe`` representing no value."""

    __match_args__ = ()

    _exists: ClassVar[bool] = False

    def __new__(cls, _: None = None) -> Self:
        """Creates a new ``NothingType`` instance only if one does not exist.

        :raises NothingTypeInitError:
            A ``NothingType`` instance already exists (the ``_exists`` classvar is ``True``).
        """
        if cls._exists:
            raise NothingTypeInitError('Cannot instance a second NothingType, use the Nothing singleton')
        cls._exists = True

        return super().__new__(cls)

    def __init__(self) -> None:
        """The ``_val`` attribute of ``NothingType`` is irrelevant, so ``__init__`` accepts no parameters."""
        self._val: None = None

    @override
    def __repr__(self) -> str:
        """Returns ``'Nothing'``."""
        return 'Nothing'

    @override
    def __bool__(self) -> bool:
        return False

Nothing = NothingType()

class Some[T](Maybe):
    """Subclass of ``Maybe`` representing a present value of type ``T``."""

    def __init__(self, val: T) -> None:
        self._val: T = val

    @override
    def __bool__(self) -> bool:
        return True

@overload
def maybe[T](val: None, predicate: Callable[[T], bool] = lambda v: v is not None) -> NothingType: ...
@overload
def maybe[T](val: T, predicate: Callable[[T], bool] = lambda v: v is not None) -> Maybe[T]: ...
def maybe[T](val: T | None, predicate: Callable[[T], bool] = lambda v: v is not None) -> Maybe[T]:
    """Returns ``Nothing`` if ``val`` is ``None`` or ``not predicate(val)``, otherwise returns ``Some(val)``.

    :param val: A value to wrap.
    :param predicate: A function that must return ``True`` for ``predicate(val)`` in addition to ``val`` not being
        ``None`` in order for a ``Some`` to be returned; ``maybe(val, predicate)`` is then effectively shorthand for
        ``maybe(val).filter(predicate)``.
    """
    return Nothing if (val is None) or not predicate(val) else Some(val)

def maybe_exc[T](
        fn: Callable[[], T],
        *exc: type[Exception] | tuple[type[Exception], str | re.Pattern],
    ) -> Maybe[T]:
    r"""Returns ``Nothing`` if ``fn()`` raises the specified error(s), otherwise returns ``Some`` with its result.

    >>> assert maybe_exc(lambda: int('1'), ValueError) == Some(1)
    >>> assert maybe_exc(lambda: int('one'), ValueError) == Nothing
    >>> assert maybe_exc(lambda: int('one'), (ValueError, r'invalid literal for int\(\).*')) == Nothing

    :param fn: A function to call which takes no arguments.
    :param exc: One or more either exception types or a tuple of an exception type and regex pattern to match the raised
        exception's message against, where if any of the given exceptions are raised (and if a pattern is given,
        ``str(e)`` where ``e`` is the raised exception must match it), ``Nothing`` is returned instead of propagating
        the exception. If any exceptions not listed are raised or a pattern is given for an exception and it does not
        match, the exception is raised normally.
    """
    excmap: dict[type[Exception], str | re.Pattern[str]] = dict(i if isinstance(i, tuple) else (i, '') for i in exc)

    try:
        result: T = fn()
    except tuple(excmap) as e:
        if (p := excmap[e.__class__]) and not re.match(p, str(e)):
            raise
        return Nothing

    return Some(result)

# Result type

class Result[T, E]:  # noqa: PLW1641 ; Intentional, we want Ok and Err comparable but not hashable
    """A class which wraps a value of ``T`` if the instance is of the subclass ``Ok``, or wraps ``E`` if ``Err``.

    The ``Result`` class itself should only be using for type annotations and not instancing; use the ``Ok`` and ``Err``
    constructors otherwise. :py:class:`ResultInitError` is raised if ``Result()`` is called directly.

    ``Ok`` instances are always truthy, while ``Err`` instances are always falsy.
    """

    __match_args__ = ('_val',)

    _val: T | E

    def __init__(self, _val: T | E) -> None:
        raise ResultInitError('Result is not intended for direct usage, use Ok or Err')

    def __bool__(self) -> bool:
        """Returns ``True`` if ``Ok``, or ``False`` if ``Err``."""
        raise NotImplementedError

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}({self._val!r})'

    def __eq__(self, other: object) -> bool:
        """Compares the wrapped values if both objects are the same type, otherwise returns ``False``."""
        if not isinstance(other, self.__class__):
            return False
        return self._val == other._val

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Returns ``func`` called with the wrapped value if ``Ok``, otherwise returns this instance."""
        if self:
            return func(cast('T', self._val))
        return cast('Result[U, E]', self)

    def cast[U, F](self, _t: type[U], _e: type[F]) -> Result[U, F]:
        """Returns a reference to this instance after casting its type as ``Result[t_type, e_type]``."""
        return cast('Result[U, F]', self)

    def err(self) -> Maybe[E]:
        """Returns a ``Some`` with the wrapped value if ``Err``, otherwise returns ``Nothing``."""
        if self:
            return Nothing
        return Some(self._val)

    def flatten(self) -> Result[T, E]:
        """Returns a new ``Result[T, E]`` from a``Result[Result[T, E], E]``.

        Only flattens one level at a time, and will raise a ``TypeError`` if called when the wrapped value is not
        ``Result``.

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
            func(cast('T', self._val))
        return self

    def inspect_err(self, func: Callable[[E], Any]) -> Self:
        """Calls a function with the wrapped value if ``Err``, otherwise does nothing. Returns this instance."""
        if self:
            func(cast('E', self._val))
        return self

    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        """Returns a new ``Result`` with ``func`` mapped onto an ``Ok`` value, leaving an ``Err`` unmodified."""
        if self:
            return Ok(func(cast('T', self._val)))
        return cast('Result[U, E]', self)

    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        """Returns a new ``Result`` with ``func`` mapped onto an ``Err`` value, leaving an ``Ok`` unmodified."""
        if not self:
            return Err(func(cast('E', self._val)))
        return cast('Result[T, F]', self)

    def map_or[U](self, default: U, func: Callable[[T], U]) -> U:
        """Returns ``func`` mapped onto the wrapped value if ``Ok``, otherwise returns ``default``."""
        if self:
            return func(cast('T', self._val))
        return default

    def map_or_else[U](self, default: Callable[[E], U], func: Callable[[T], U]) -> U:
        """Returns the result of calling ``func`` with the wrapped value if ``Ok``, otherwise calls ``default``."""
        if self:
            return func(cast('T', self._val))

        return default(cast('E', self._val))

    def ok(self) -> Maybe[E]:
        """Returns a ``Some`` with the wrapped value if ``Ok``, otherwise returns ``Nothing``."""
        if not self:
            return Nothing
        return Some(self._val)

    def transpose(self) -> Maybe[Result[T, E]]:
        """Transposes a ``Result`` of ``Maybe`` to a ``Maybe`` of ``Result``.

        ``Ok(Nothing)`` becomes ``Nothing``, ``Ok(Some(x))`` becomes ``Some(Ok(x))``, and ``Err(x)`` becomes
        ``Some(Err(x))``.

        :raises TypeError:
            This is an ``Ok`` instance and the wrapped value is not ``Maybe``.
        """
        if not self:
            return Some(self)
        if not isinstance(self._val, Maybe):
            raise TypeError(f'Cannot transpose Ok which does not wrap Maybe: {self!r}')
        if self._val is Nothing:
            return Nothing
        return Some(Ok(self._val._val))  # noqa: SLF001

    def _unwrap_fail(self, exc: str | type[Exception] | Callable[[E], Never]) -> Never:
        if isinstance(exc, str):
            raise ResultUnwrapError(f'{exc}: {self._val!r}')
        if isinstance(exc, type) and issubclass(exc, Exception):
            raise exc(repr(self._val))
        if isinstance(exc, Callable):
            exc(cast('E', self._val))
        raise TypeError(f'Unexpected type for unwrap argument exc: {exc!r}')

    def unwrap(self, exc: str | type[Exception] | Callable[[E], Never] = ResultUnwrapError) -> T:
        """Returns the wrapped value if ``Ok``, otherwise raises an error according to ``exc``.

        :param exc: By default, ``ResultUnwrapError`` is raised with the wrapped value as the exception argument.
            If given a string, ``ResultUnwrapError`` is raised with the message format ``{msg}: {repr(val)}``, where
            ``val`` is the wrapped ``Err`` value.
            If given an ``Exception`` type, that type of exception is raised with the wrapped value as the exception
            argument.
            If given a ``Callable``, ``exc`` is called with the wrapped value as the passed argument.
        """
        if self:
            return cast('T', self._val)
        return self._unwrap_fail(exc)

    def unwrap_err(self, exc: str | type[Exception] | Callable[[E], Never] = ResultUnwrapError) -> E:
        """Returns the wrapped value if ``Err``, otherwise raises an error according to ``exc``.

        :param exc: By default, ``ResultUnwrapError`` is raised with the wrapped value as the exception argument.
            If given a string, ``ResultUnwrapError`` is raised with the message format ``{msg}: {repr(val)}``, where
            ``val`` is the wrapped ``Ok`` value.
            If given an ``Exception`` type, that type of exception is raised with the wrapped value as the exception
            argument.
            If given a ``Callable``, ``exc`` is called with the wrapped value as the passed argument.
        """
        if not self:
            return cast('E', self._val)
        return self._unwrap_fail(exc)

    def unwrap_or(self, default: T) -> T:
        """Returns the wrapped value if ``Ok``, otherwise returns ``default``."""
        return cast('T', self._val) if self else default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Returns the wrapped value if ``Ok``, otherwise returns ``func`` called with the wrapped value."""
        return cast('T', self._val) if self else func(cast('E', self._val))

class Ok[T, E](Result[T, E]):
    """Indicates a successful result of type ``T``."""

    def __init__(self, val: T) -> None:
        self._val: T = val

    @override
    def __bool__(self) -> bool:
        return True

class Err[T, E](Result[T, E]):
    """Indicates a failed result of type ``E``."""

    def __init__(self, val: E) -> None:
        self._val: E = val

    @override
    def __bool__(self) -> bool:
        return False
