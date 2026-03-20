from __future__ import annotations

import warnings
from collections.abc import Callable, Iterable
from typing import Any, Never, Self, cast


class Maybe[T]:
    """
    Wraps a value that may be ``T`` or ``None``, providing methods for conditionally using that value or
    short-circuiting to ``None`` without longer checks.
    """
    __match_args__ = ('_val',)

    def __init__(self, val: T | None) -> None:
        warnings.warn(
            'Direct instancing of Maybe() not intended and may cause unexpected behavior,'
            + ' use the maybe() function instead',
            stacklevel=2,
        )
        self._val: T | None = val

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._val!r})'

    def __bool__(self) -> bool:
        return self._val is not None

    def __eq__(self, other: object) -> bool:
        """
        Returns ``False`` if the compared object is not a ``Maybe`` instance, otherwise compares their wrapped values.
        """
        if not isinstance(other, Maybe):
            return False
        return self._val == other._val

    def __hash__(self) -> int:
        return hash(self._val)

    @staticmethod
    def cat(vals: Iterable[Maybe[T]]) -> list[T]:
        """
        Takes an iterable of ``Maybe`` and returns a list of the unwrapped values of all ``Some`` objects.

        >>> vals = [maybe(5), maybe(None), maybe(10), maybe(None)]
        >>> assert vals == [Some(5), Nothing, Some(10), Nothing]
        >>> assert Maybe.cat(vals) == [5, 10]
        """
        return [i.unwrap() for i in vals if i]

    @staticmethod
    def sequence(vals: Iterable[Maybe[T]]) -> Maybe[list[T]]:
        """
        Returns ``Nothing`` if any of ``vals`` is ``Nothing``, otherwise returns a ``Some`` of a list of unwrapped
        items of ``vals``.

        >>> assert Maybe.sequence([Some(1), Some(2), Some(3)]) == Some([1, 2, 3])
        >>> assert Maybe.sequence([Some(1), Nothing, Some(3)]) is Nothing
        """
        unwrapped: list[T] = []
        for i in vals:
            if i is Nothing:
                return Nothing
            unwrapped.append(i.unwrap())
        return Some(unwrapped)

    @staticmethod
    def try_int(val: Any) -> Maybe[int]:  # noqa: ANN401
        """
        Attempts to convert ``val`` to an ``int``, returning a ``Some``-wrapped ``int`` if successful, or
        ``Nothing`` on failure.
        """
        try:
            i: int = int(val)
            return Some(i)
        except ValueError:
            return Nothing

    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """
        Returns the result of ``func`` (which must return a ``Maybe``) called with this instance's wrapped value if
        ``Some``, otherwise returns ``Nothing``.
        """
        return func(self._val) if self._val is not None else Nothing

    def attr[U](self, name: str, default: U | None = None, typ: type[U] | None = None) -> Maybe[U]:
        """
        Attempts to access an attribute ``name`` on the wrapped object, returning a ``Some`` instance wrapping the
        the value if it exists, or ``Nothing`` otherwise.

        :param name: The name of the attribute to access.
        :param default: An optional default value to use if the attribute does not exist, returning ``Some(default)``
            in that case.
        :param typ: Specifies the generic type of the resulting ``Maybe``. This does not affect the value's real type
            at runtime; it is only used for type checkers.
            This is generally unnecessary if the ``default`` parameter is given, as the type will be inferred from its
            value.
        """
        try:
            return Some(getattr(self._val, name) if default is None else getattr(self._val, name, default))
        except AttributeError:
            return Nothing

    def bind[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """
        Returns the result of ``func`` called with the wrapped value as its argument if ``Some``, otherwise returns
        ``Nothing``.
        """
        if self._val is None:
            return Nothing
        return func(self._val)

    def cast[U](self, typ: type[U]) -> Maybe[U]:
        """Returns a reference to this instance after casting its type as ``Maybe[typ]``."""
        return cast(Maybe[U], self)

    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        """
        Returns ``self`` if ``Some`` and ``predicate`` called with this instance's wrapped value returns ``True``,
        otherwise returns ``Nothing``.

        >>> assert Some(1).filter(lambda n: n > 0).unwrap() == 1
        >>> assert Some(1).filter(lambda n: n > 1) is Nothing
        >>> assert Nothing.filter(lambda n: n > 1) is Nothing
        """
        return self if (self._val is not None) and predicate(self._val) else Nothing

    def flatten(self) -> Maybe[T]:
        """
        Converts ``Maybe[Maybe[T]]`` to ``Maybe[T]``. Only flattens one level at a time, and will raise a ``TypeError``
        if called when the wrapped value is not ``Maybe``.

        .. note::
            It's expected that the resulting type of this method may not be correctly inferred and will return
            returning ``Maybe[Unknown]``. For now, :py:meth:`cast` can be used to specify a type for type checkers.

        :raises TypeError:
            The wrapped value is not ``Maybe``.
        """
        if not isinstance(self._val, Maybe):
            raise TypeError(f'Cannot flatten when wrapped value is not of type Maybe: {self!r}')
        return maybe(cast(T, self._val._val))  # noqa: SLF001

    def get[U](self,
            accessor: Any,  # noqa: ANN401
            typ: type[U] | None = None,
            *,
            err: bool = False,
            default: U | None = None,
        ) -> Maybe[U]:
        """
        Attempts to access an item by ``accessor`` on the wrapped object if it supports ``__getitem__``.
        If it does not, or if the value does not exist (list index out of range, key does not exist on
        a dictionary, etc.), ``Nothing`` is returned.

        :param typ: Specifies the generic type of the resulting ``Maybe``. No conversion is performed; this argument is
            only for typing purposes.
        :param err: By default, ``IndexError`` and ``KeyError`` are not raised when ``__getitem__`` is called on the
            wrapped value, and ``Nothing`` is returned instead. Setting ``err`` to ``True`` allows these errors to
            be raised as they normally would. Note that if ``__getitem__`` did not exist on the wrapped value in the
            first placed (such as with ``Nothing``), no error is raised, and ``Nothing`` is returned regardless.
        :param default: Specifies an alternate value to return a ``Some`` of instead of returning ``Nothing``.
        """
        if hasattr(self._val, '__getitem__'):
            try:
                return Some(self._val.__getitem__(accessor))  # ty:ignore[call-non-callable]
            except (IndexError, KeyError):
                if err:
                    raise
        return maybe(default)

    def inspect(self, func: Callable[[T], Any]) -> Self:
        """Calls a functioned with the wrapped value if ``Some``, otherwise does nothing. Returns this instance."""
        if self._val is not None:
            func(self._val)
        return self

    def map[U](self, func: Callable[[T], U]) -> Maybe[U]:
        """
        Returns a new ``Maybe`` with the result of calling ``func`` with the wrapped value of this instance if
        ``Some``, otherwise returns ``Nothing``.
        """
        return Some(func(self._val)) if self._val is not None else Nothing

    def reduce[U, R](self,
            other: Maybe[U],
            func: Callable[[T, U], R],
            *,
            strict: bool = False,
        ) -> Maybe[T] | Maybe[U] | Maybe[R]:
        """
        Reduces the values of two ``Maybe`` instances to one value returned in a new ``Maybe`` using ``func``.

        If only one of ``self`` and ``other`` is ``Some``, that instance is returned. If neither are, ``Nothing`` is
        returned.

        >>> assert Some(1).reduce(Some(2), lambda a, b: a + b) == Some(3)
        >>> assert Some(1).reduce(Nothing, lambda a, b: a + b) == Some(1)
        >>> assert Nothing.reduce(Some(2), lambda a, b: a + b) == Some(2)
        >>> assert Nothing.reduce(Nothing, lambda a, b: a + b) is Nothing

        :param strict: If ``True``, returns ``Nothing`` if ``self`` and ``other`` are not both ``Some``.
        """
        if self and other:
            return Some(func(self.unwrap(), other.unwrap()))
        return Nothing if strict else (self or other)

    def replace(self, new_val: T) -> Maybe[T]:
        """
        Replaces the wrapped value with ``new_val`` and returns a reference to this same instance if ``Some``,
        otherwise returns ``Nothing``.
        """
        if not self:
            return Nothing
        self._val = new_val
        return self

    def then[U](self, func: Callable[[T], U]) -> U | None:
        """
        Returns ``func`` called with this instance's wrapped value if ``Some``, otherwise returns ``None``.

        :param func: A ``Callable`` which takes a type of the possible wrapped value (``T``) and can return any type
            (``U``).
        """
        return func(self._val) if self._val is not None else None

    def unwrap(self, exc: str | Exception | Callable[[], Never] = 'unwrapped Nothing') -> T:
        """
        Returns the wrapped value if ``Some``, otherwise raises ``ValueError`` or fails according to ``exc``.

        :param exc: The exception to raise when unwrapping ``Nothing``. If a string is given, ``ValueError`` is raised
            as ``ValueError(exc)``. If an ``Exception`` object is given, it is raised. If a ``Callable`` is given, it
            is called with no arguments.
        """
        if self._val is None:
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
        return self._val if self._val is not None else other

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Returns the wrapped value if ``Some``, otherwise returns the result of calling ``func``."""
        return self._val if self._val is not None else func()

    def unzip[U](self) -> tuple[Maybe[T], Maybe[U]]:
        """
        Returns ``(Some(a), Some(b))`` if the wrapped value is a tuple of two items. If ``Nothing``,
        ``(Nothing, Nothing)`` is returned. Otherwise, ``TypeError`` is raised.

        :raises TypeError:
            The wrapped value is not a 2-tuple.
        """
        if isinstance(self._val, tuple) and (len(self._val) == 2):  # noqa: PLR2004
            return (Some(self._val[0]), Some(self._val[1]))
        if self._val is None:
            return (Nothing, Nothing)
        raise TypeError(f'Cannot unzip Maybe if the wrapped value is not a 2-tuple: {self!r}')

    def zip[U](self, other: Maybe[U]) -> Maybe[tuple[T, U]]:
        """
        Returns a wrapped tuple of this and another ``Maybe`` instance's wrapped values if both are ``Some``, otherwise
        returns ``Nothing``.
        """
        return Some((self._val, other._val)) if (self._val is not None) and (other._val is not None) else Nothing

class Some[T](Maybe):
    def __init__(self, val: T) -> None:
        self._val: T = val

    def __bool__(self) -> bool:
        return True

class NothingType(Maybe):
    __match_args__ = ()

    def __init__(self, _: None = None) -> None:
        """The ``val`` attribute of a ``NothingType`` is always ``None``, so any parameter given is unused."""
        self._val: None = None

    def __repr__(self) -> str:
        return 'Nothing'

    def __bool__(self) -> bool:
        return False

Nothing = NothingType()

def maybe[T](val: T | None, predicate: Callable[[T], bool] = lambda v: v is not None) -> Maybe[T]:
    """
    Returns a ``Some`` instance wrapping ``val`` if either ``val`` is not ``None`` or ``predicate(val)`` is ``True``,
    otherwise returns the ``Nothing`` singleton.

    :param val: A value to wrap.
    :param predicate: An function that takes ``val`` and, if it returns ``False``, discards ``val`` and returns a
    ``Nothing`` instance, by default simply checking if ``val`` is not ``None``. Regardless of the predicate,
    ``Nothing`` is always returned when ``val`` is ``None``.
    """
    return Nothing if (val is None) or not predicate(val) else Some(val)
