from collections.abc import Callable, Iterable
from typing import Any, Never


class Maybe[T]:
    """
    Wraps a value that may be ``T`` or ``None``, providing methods for conditionally using that value or
    short-circuiting to ``None`` without longer checks.
    """
    def __init__(self,
            val: T | None,
            predicate: Callable[[T], bool] = lambda v: v is not None,
        ) -> None:
        """
        :param val: A value to wrap.
        :param predicate: An optional function that takes ``val`` and, if it returns ``False``, discards ``val``
            and makes this a ``Maybe(None)`` instance. This function does not need to additionally check if ``val`` is
            ``None``, as this check will be made on init before attempting to the call the function.
        """
        self.val = None if (val is None) or not predicate(val) else val

    def __repr__(self) -> str:
        return f'Maybe({self.val!r})'

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
        Takes an iterable of ``Maybe`` and returns a list of the unwrapped values of non-``Maybe(None)`` objects.

        >>> vals = [Maybe(5), Maybe(None), Maybe(10), Maybe(None)]
        >>> assert Maybe.cat(vals) == [5, 10]
        """
        return [i.unwrap() for i in vals if i]

    @staticmethod
    def int(val: Any) -> 'Maybe[int]':  # noqa: ANN401
        """
        Attempts to convert ``val`` to an ``int``, returning a ``Maybe``-wrapped ``int`` if successful, or
        ``Maybe(None)`` on failure.
        """
        try:
            i: int = int(val)
            return Maybe(i)
        except ValueError:
            return Maybe(None)

    @staticmethod
    def map[A, B](fn: 'Callable[[A], Maybe[B]]', vals: Iterable[A]) -> list[B]:
        """Maps ``fn`` onto ``vals``, taking the unwrapped values and discarding ``Maybe(None)``s."""
        return [i.unwrap() for i in map(fn, vals) if i]

    def attr[V](self, name: str, typ: type[V] | None = None, *, err: bool = False) -> 'Maybe[V]':
        """
        Attempts to access an attribute ``name`` on the wrapped object, returning another ``Maybe``-wrapped value which
        wraps the value if it exists, or ``Maybe(None)`` otherwise.

        :param typ: Specifies the generic type of the resulting ``Maybe``. Note that the potential value returned by
            this method will not be coerced to the given type at runtime; this argument is only for typing purposes.
        :param err: If ``True``, ``AttributeError`` is raised instead of returning ``Maybe(None)`` if ``name`` does not
            exist.
        """
        return Maybe(getattr(self.val, name)) if err else Maybe(getattr(self.val, name, None))

    def attr_or[V](self, name: str, default: V) -> V:
        """
        Similar to the ``attr`` method, but unwraps the result if the attribute exists or returns the required default
        value otherwise.
        """
        try:
            return self.attr(name, err=True).unwrap()
        except AttributeError:
            return default

    def get[V](self,
            accessor: Any,  # noqa: ANN401
            _typ: type[V] | None = None,
            *,
            err: bool = False,
            default: V | None = None,
        ) -> 'Maybe[V]':
        """
        Attempts to access an item by ``accessor`` on the wrapped object, assuming the wrapped value implements
        ``__getitem__``. If it does not, or if the value does not exist (list index out of range, key does not exist on
        a dictionary, etc.), ``Maybe(None)`` is returned.

        :param typ: Specifies the generic type of the resulting ``Maybe``. Note that the potential value returned by
            this method will not be coerced to the given type at runtime; this argument is only for typing purposes.
        :param err: By default, ``IndexError`` and ``KeyError`` are not raised when ``__getitem__`` is called on the
            wrapped value, and ``Maybe(None)`` is returned instead. Setting ``err`` to ``True`` allows these errors to
            be raised as they normally would. Note that if ``__getitem__`` did not exist on the wrapped value in the
            first placed (such as with ``Maybe(None)``), no error is raised, and ``Maybe(None)`` is returned regardless.
        :param default: Specifies an alternate value to return a ``Maybe`` of instead of ``None``.
        """
        if hasattr(self.val, '__getitem__'):
            try:
                return Maybe(self.val.__getitem__(accessor)) # type: ignore
            except (IndexError, KeyError):
                if err:
                    raise
        return Maybe(default)

    def then[R](self, func: Callable[[T], R]) -> R | None:
        """
        Calls ``func`` with the wrapped value as the argument and returns its value, or returns ``None`` if the wrapped
        value is ``None``.

        :param func: A ``Callable`` which takes a type of the possible wrapped value (``T``) and can return any type
            (``R``).
        """
        return func(self.val) if self.val is not None else None

    def this_or(self, other: T) -> 'Maybe[T]':
        """Returns the original wrapped value if not ``None``, otherwise returns a ``Maybe``-wrapped ``other``."""
        return self if self else Maybe(other)

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
