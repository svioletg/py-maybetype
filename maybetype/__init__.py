import warnings
from collections.abc import Callable, Iterable
from typing import Any, Never


class Maybe[T]:
    """
    Wraps a value that may be ``T`` or ``None``, providing methods for conditionally using that value or
    short-circuiting to ``None`` without longer checks.
    """
    __match_args__ = ('val',)

    def __init__(self, val: T | None) -> None:
        warnings.warn(
            'Direct instancing of Maybe() is not recommended as of v0.5.0, use the maybe() function instead',
            stacklevel=2,
        )
        self.val = val

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val!r})'

    def __bool__(self) -> bool:
        return self.val is not None

    def __eq__(self, other: object) -> bool:
        """
        Returns ``False`` if the compared object is not a ``Maybe`` instance, otherwise compares their wrapped values.
        """
        if not isinstance(other, Maybe):
            return False
        return self.val == other.val

    def __hash__(self) -> int:
        return self.val.__hash__()

    @staticmethod
    def cat(vals: 'Iterable[Maybe[T]]') -> list[T]:
        """
        Takes an iterable of ``Maybe`` and returns a list of the unwrapped values of all ``Some`` objects.

        >>> vals = [maybe(5), maybe(None), maybe(10), maybe(None)]
        >>> assert vals == [Some(5), Nothing, Some(10), Nothing]
        >>> assert Maybe.cat(vals) == [5, 10]
        """
        return [i.unwrap() for i in vals if i]

    @staticmethod
    def int(val: Any) -> 'Maybe[int]':  # noqa: ANN401
        """
        Attempts to convert ``val`` to an ``int``, returning a ``Some``-wrapped ``int`` if successful, or
        ``Nothing`` on failure.
        """
        try:
            i: int = int(val)
            return Some(i)
        except ValueError:
            return Nothing

    @staticmethod
    def map[A, B](fn: 'Callable[[A], Maybe[B]]', vals: Iterable[A]) -> list[B]:
        """Maps ``fn`` onto ``vals``, taking the unwrapped values of ``Some``s and discarding ``Nothing``s."""
        return [i.unwrap() for i in map(fn, vals) if i]

    def and_then[R](self, func: Callable[[T], R]) -> 'Maybe[R]':
        """
        Like :py:meth:`~maybetype.Maybe.then`, but returns a ``Maybe`` instance instead—``Nothing`` if this instance
        is a ``Nothing``, ``Some(R)`` if the instance is ``Some``, where ``R`` is the returned value of ``func``.
        """
        return Some(func(self.val)) if self.val is not None else Nothing

    def attr[U](self, name: str, typ: type[U] | None = None, *, err: bool = False) -> 'Maybe[U]':
        """
        Attempts to access an attribute ``name`` on the wrapped object, returning a ``Some`` instance wrapping the
        the value if it exists, or ``Nothing`` otherwise.

        :param typ: Specifies the generic type of the resulting ``Maybe``. Note that the potential value returned by
            this method will not be coerced to the given type at runtime; this argument is only for typing purposes.
        :param err: If ``True``, ``AttributeError`` is raised instead of returning ``Nothing`` if ``name`` does not
            exist.
        """
        return Some(getattr(self.val, name)) if err else maybe(getattr(self.val, name, None))

    def attr_or[U](self, name: str, default: U) -> U:
        """
        Similar to the ``attr`` method, but unwraps the result if the attribute exists or returns the required default
        value otherwise.
        """
        try:
            return self.attr(name, err=True).unwrap()
        except AttributeError:
            return default

    def get[U](self,
            accessor: Any,  # noqa: ANN401
            _typ: type[U] | None = None,
            *,
            err: bool = False,
            default: U | None = None,
        ) -> 'Maybe[U]':
        """
        Attempts to access an item by ``accessor`` on the wrapped object, assuming the wrapped value implements
        ``__getitem__``. If it does not, or if the value does not exist (list index out of range, key does not exist on
        a dictionary, etc.), ``Nothing`` is returned.

        :param typ: Specifies the generic type of the resulting ``Maybe``. Note that the potential value returned by
            this method will not be coerced to the given type at runtime; this argument is only for typing purposes.
        :param err: By default, ``IndexError`` and ``KeyError`` are not raised when ``__getitem__`` is called on the
            wrapped value, and ``Nothing`` is returned instead. Setting ``err`` to ``True`` allows these errors to
            be raised as they normally would. Note that if ``__getitem__`` did not exist on the wrapped value in the
            first placed (such as with ``Nothing``), no error is raised, and ``Nothing`` is returned regardless.
        :param default: Specifies an alternate value to return a ``Some`` of instead of returning ``Nothing``.
        """
        if hasattr(self.val, '__getitem__'):
            try:
                return Some(self.val.__getitem__(accessor)) # type: ignore
            except (IndexError, KeyError):
                if err:
                    raise
        return maybe(default)

    def test(self, predicate: Callable[[T], bool]) -> 'Maybe[T]':
        """
        Returns ``Nothing`` if the wrapped value does not return ``True`` when passed to ``predicate``, otherwise
        returns the instance the method was called from. When called from a ``Nothing`` instance, ``Nothing`` is always
        returned.
        """
        match self:
            case Some(val):
                return self if predicate(val) else Nothing
            case _:
                return Nothing

    def then[U](self, func: Callable[[T], U]) -> U | None:
        """
        Returns ``func`` called with this instance's wrapped value if ``Some``, otherwise returns ``None``.

        :param func: A ``Callable`` which takes a type of the possible wrapped value (``T``) and can return any type
            (``R``).
        """
        return func(self.val) if self.val is not None else None

    def this_or(self, other: T) -> 'Maybe[T]':
        """Returns the original wrapped value if not ``None``, otherwise returns a ``Some``-wrapped ``other``."""
        return self if self else Some(other)

    def unwrap(self,
            exc: Exception | Callable[..., Never] | None = None,
            *exc_args: object,
        ) -> T:
        """
        Returns the wrapped value if it is not ``None``, otherwise raises ``ValueError`` by default.

        :param exc: The exception to raise if the wrapped value is ``None``. Can be either an ``Exception`` object, or a
            ``Callable`` which takes any arguments and does not return. If given ``None``, the default behavior is to
            raise a ``ValueError`` with the message ``Maybe[<type>] unwrapped into None``.
        :param exc_args: Arguments to call ``exc`` with, if ``exc`` is a ``Callable``. Otherwise, this argument is not
            used.
        """
        if self.val is None:
            if isinstance(exc, Exception):
                raise exc
            if isinstance(exc, Callable):
                exc(*exc_args)
            raise ValueError(f'Maybe[{T.__name__}] unwrapped into None')
        return self.val

    def unwrap_or(self, other: T) -> T:
        """Returns the wrapped value if it is not ``None``, otherwise returns ``other``."""
        return self.val if self.val is not None else other

class Some[T](Maybe[T]):
    def __init__(self, val: T) -> None:
        self.val = val

    def __bool__(self) -> bool:
        return True

class _Nothing[T](Maybe[T]):
    __match_args__ = ()

    def __init__(self, _: None = None) -> None:
        self.val = None

    def __repr__(self) -> str:
        return 'Nothing'

    def __bool__(self) -> bool:
        return False

Nothing = _Nothing()

def maybe[T](val: T | None, predicate: Callable[[T], bool] = lambda v: v is not None) -> Maybe[T]:
    """
    Returns a ``Some`` instance wrapping ``val`` if either ``val`` is not ``None`` or ``predicate(val)`` is ``True``,
    otherwise returns the ``Nothing`` singleton.

    :param val: A value to wrap.
    :param predicate: An optional function that takes ``val`` and, if it returns ``False``, discards ``val``
        and returns a ``Nothing`` instance. Regardless of the predicate, ``Nothing`` is always returned if
        ``val`` is ``None``.
    """
    return Nothing if (val is None) or not predicate(val) else Some(val)
