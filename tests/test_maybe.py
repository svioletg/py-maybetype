import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from string import ascii_lowercase

import pytest  # ty:ignore[unresolved-import, unused-ignore-comment]; seems to only show up in workflow runs?

from maybetype import Err, Maybe, Nothing, NothingType, Ok, Some, maybe

ALPHANUMERIC: str = ascii_lowercase + '0123456789'
MAYBE_UNWRAP_NONE_REGEX: re.Pattern[str] = re.compile(r"unwrapped Nothing")

def test_unwrap_nothing() -> None:
    assert bool(Nothing) is False
    with pytest.raises(ValueError, match=MAYBE_UNWRAP_NONE_REGEX):
        Nothing.unwrap()
    with pytest.raises(ValueError, match='Custom error message'):
        Nothing.unwrap('Custom error message')

def test_unwrap_nothing_callback() -> None:
    with pytest.raises(TypeError):
        Nothing.unwrap(TypeError('Nothing'))
    with pytest.raises(SystemExit):
        Nothing.unwrap(exit)

def test_maybe_none_is_nothing() -> None:
    assert maybe(None) is Nothing

def test_equality() -> None:
    assert maybe(1) == Some(1)
    assert maybe(1) != Some(2)
    assert maybe(1) != Nothing

@pytest.mark.parametrize(('val'),
    [
        None,
        0,
        1,
        '',
        'string',
        [],
        [1, 2, 3],
        True,
        False,
    ],
)
def test_nothing_instance_always_wraps_none(val: object) -> None:
    assert NothingType(val)._val is None  # ty:ignore[invalid-argument-type]  # noqa: SLF001

def test_maybe_or() -> None:
    assert (Maybe.try_int('10') or Some(0)).unwrap() == 10  # noqa: PLR2004
    assert (Maybe.try_int('ten') or Some(0)).unwrap() == 0
    with pytest.raises(ValueError, match=MAYBE_UNWRAP_NONE_REGEX):
        Maybe.try_int('ten').unwrap()

@pytest.mark.parametrize(('val', 'default'),
    [
        (5, 10),
        (5, None),
        ('string', 'fallback'),
        ('string', None),
    ],
)
def test_unwrap_or(val: object, default: object) -> None:
    assert maybe(val).unwrap_or(default) == val
    assert maybe(None).unwrap_or(default) == default

@pytest.mark.parametrize(('val', 'func', 'expected'),
    [
        (Some(1), lambda n: n * 10, Some(10)),
        (Nothing, lambda n: n * 10, Nothing),
        (Some('Hello!'), len, Some(6)),
        (Nothing, len, Nothing),
    ],
)
def test_maybe_map[T, U, V](val: Maybe[T], func: Callable[[T], U], expected: Maybe[V]) -> None:
    assert val.map(func) == expected

@pytest.mark.parametrize(('val', 'func', 'expected'),
    [
        (Some(1), lambda n: n * 10, 10),
        (Nothing, lambda n: n * 10, None),
        (Some('Hello!'), len, 6),
        (Nothing, len, None),
    ],
)
def test_maybe_then[T, U, V](val: Maybe[T], func: Callable[[T], U], expected: Maybe[V]) -> None:
    assert val.then(func) == expected

def test_maybe_attr() -> None:
    @dataclass
    class A:
        x: int

    @dataclass
    class B(A):
        y: str

    m_a: Maybe[A] = Some(A(1))
    m_b: Maybe[B] = Some(B(1, 'one'))
    m_none: Maybe[A] = Nothing

    assert m_a.attr('x').unwrap() == 1
    assert m_a.attr('x', 2).unwrap() == 1
    assert m_b.attr('x').unwrap() == 1
    assert m_b.attr('x', 2).unwrap() == 1
    assert m_b.attr('y').unwrap() == 'one'
    assert m_b.attr('y', 'two').unwrap() == 'one'
    assert m_a.attr('y') is Nothing
    assert m_a.attr('y', 2).unwrap() == 2  # noqa: PLR2004
    assert m_none.attr('x') is Nothing
    assert m_none.attr('x', 2).unwrap() == 2  # noqa: PLR2004

@pytest.mark.parametrize(('val', 'accessor', 'result'),
    [
        (None,             1,   Nothing),
        ([1, 2, 3],        1,   Some(2)),
        ([1, 2, 3],        3,   Nothing),
        ([],               1,   Nothing),
        ({'a': 1, 'b': 2}, 'a', Some(1)),
        ({'a': 1, 'b': 2}, 'c', Nothing),
        ({},               'a', Nothing),
    ],
    ids=[
        'none',
        'list_populated',
        'list_populated_out_of_range',
        'list_empty',
        'dict_populated',
        'dict_populated_no_key',
        'dict_empty',
    ],
)
def test_maybe_get(val: object, accessor: object, result: object) -> None:
    m: Maybe = maybe(val)
    assert m.get(accessor) == result

def test_maybe_cat() -> None:
    assert Maybe.cat((Some(1), Some('one'), Nothing, Some(2))) == [1, 'one', 2]
    assert Maybe.cat(map(Maybe.try_int, ALPHANUMERIC)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_maybe_cat_failure() -> None:
    with pytest.raises(AttributeError, match='has no attribute \'unwrap\''):
        Maybe.cat([1, 2, 3]) # type: ignore

def is_valid_uuid(s: str) -> bool:
    return re.match(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}|[0-9a-f]{32}", s) is not None

@pytest.mark.parametrize(('value', 'predicate', 'expected_bool'),
    [
        (0, lambda a: a > 0, False),
        ([], lambda a: len(a) > 0, False),
        ([], lambda a: 'x' in a, False),
        ({}, lambda a: len(a) > 0, False),
        ({}, lambda a: 'x' in a, False),
        ('3b1bcc3a-41d5-49a5-8273-10cc605e31f9', is_valid_uuid, True),
        ('3b1bcc3a41d549a5827310cc605e31f9', is_valid_uuid, True),
        ('qwertyuiopasdfghjklzxcvbnm', is_valid_uuid, False),
        ('nf0cmmdq-l0gt-rq5a-upry-706trht3ocv9', is_valid_uuid, False),
    ],
)
def test_maybe_with_predicate_and_filter[T](value: T, predicate: Callable[[T], bool], expected_bool: bool) -> None:
    assert bool(maybe(value, predicate)) is expected_bool
    assert maybe(value, predicate) == maybe(value).filter(predicate)
    if expected_bool is False:
        assert maybe(value, predicate) is Nothing
        assert maybe(value).filter(predicate) is Nothing
    else:
        assert maybe(value).filter(predicate)

@pytest.mark.parametrize(('value', 'predicate', 'expected'),
    [
        (0, lambda a: a > 0, None),
        ([], lambda a: len(a) > 0, None),
        ([], lambda a: 'x' in a, None),
        ({}, lambda a: len(a) > 0, None),
        ({}, lambda a: 'x' in a, None),
        ('3b1bcc3a-41d5-49a5-8273-10cc605e31f9', is_valid_uuid, ...),
        ('3b1bcc3a41d549a5827310cc605e31f9', is_valid_uuid, ...),
        ('qwertyuiopasdfghjklzxcvbnm', is_valid_uuid, None),
        ('nf0cmmdq-l0gt-rq5a-upry-706trht3ocv9', is_valid_uuid, None),
    ],
)
def test_pattern_matching[T](value: T, predicate: Callable[[T], bool], expected: T | None) -> None:
    if expected is Ellipsis:
        expected = value

    match maybe(value, predicate):
        case Some(value):
            result = value
        case _:
            result = None

    assert result == expected

@pytest.mark.parametrize(('value', 'func', 'expected'),
    [
        (Some('1'), Maybe.try_int, Some(1)),
        (Nothing, Maybe.try_int, Nothing),
    ],
)
def test_maybe_and_then[T, U](value: Maybe[T], func: Callable[[T], Maybe[U]], expected: Maybe[U]) -> None:
    assert value.and_then(func) == expected

@pytest.mark.parametrize(('vals', 'expected'),
    [
        ([Some(1), Some(2), Some(3)], Some([1, 2, 3])),
        ([Some(1), Nothing, Some(3)], Nothing),
        ([Nothing, Nothing, Nothing], Nothing),
    ],
)
def test_maybe_sequence[T](vals: Iterable[Maybe[T]], expected: Maybe[list[T]]) -> None:
    assert Maybe.sequence(vals) == expected

@pytest.mark.parametrize(('m', 'func', 'expected'),
    [
        (Some('1'), Maybe.try_int, Some(1)),
        (Some('one'), Maybe.try_int, Nothing),
        (Nothing, Maybe.try_int, Nothing),
    ],
)
def test_bind[T, U](m: Maybe[T], func: Callable[[T], Maybe[U]], expected: Maybe[U]) -> None:
    assert m.bind(func) == expected

@dataclass
class Point:
    x: int
    y: int

@pytest.mark.parametrize(('m_a', 'm_b', 'func', 'expected'),
    [
        (Some(1), Some(2), lambda a, b: a + b, Some(3)),
        (Some([1, 2]), Some([3, 4]), lambda a, b: a + b, Some([1, 2, 3, 4])),
        (Some(1), Some(2), Point, Some(Point(1, 2))),
    ],
)
def test_maybe_reduce[T, U, R](m_a: Some[T], m_b: Some[U], func: Callable[[T, U], R], expected: Maybe) -> None:
    assert m_a.reduce(m_b, func) == expected
    assert m_a.reduce(Nothing, func) == m_a
    assert Nothing.reduce(m_b, func) == m_b
    assert Nothing.reduce(Nothing, func) is Nothing

@pytest.mark.parametrize(('m', 'new_val', 'expected'),
    [
        (Some(1), 2, Some(2)),
        (Nothing, 2, Nothing),
    ],
)
def test_maybe_replace[T](m: Maybe[T], new_val: T, expected: Maybe[T]) -> None:
    m_id = id(m)
    m = m.replace(new_val)
    assert m == expected
    if m:
        # Assert that a reference to the same instance was returned and not a new instance
        assert id(m) == m_id

def test_maybe_zip() -> None:
    assert Some(1).zip(Some(2)) == Some((1, 2))
    assert Some(1).zip(Nothing) is Nothing
    assert Nothing.zip(Some(2)) is Nothing
    assert Nothing.zip(Nothing) is Nothing

def test_maybe_flatten() -> None:
    assert Some(Some(1)).flatten() == Some(1)
    assert Some(Nothing).flatten() is Nothing

    with pytest.raises(TypeError, match=r"Cannot flatten.*"):
        Some(1).flatten()

def test_maybe_cast() -> None:
    m = Some(1)
    m_id = id(m)
    assert id(m.cast(int)) == m_id

def test_maybe_inspect() -> None:
    lst = [1, 2, 3]
    m = Some(4)
    m_id = id(m)
    assert id(m.inspect(lst.append)) == m_id
    assert lst == [1, 2, 3, 4]
    Nothing.inspect(lst.append)
    assert lst == [1, 2, 3, 4]

def test_maybe_unwrap_or_else() -> None:
    def f() -> int:
        return 2

    s = Some(1)

    assert s.unwrap_or_else(f) == 1
    assert Nothing.unwrap_or_else(f) == 2  # noqa: PLR2004

def test_maybe_unzip() -> None:
    assert Some((1, 2)).unzip() == (Some(1), Some(2))
    assert Nothing.unzip() == (Nothing, Nothing)

    with pytest.raises(TypeError, match=r"Cannot unzip"):
        assert Some((1, 2, 3)).unzip()

    with pytest.raises(TypeError, match=r"Cannot unzip"):
        assert Some(1).unzip() == (Nothing, Nothing)

def test_maybe_xor() -> None:
    s_a = Some(1)
    s_b = Some(2)

    assert s_a.xor(s_b) == Nothing
    assert s_a.xor(Nothing) == s_a
    assert Nothing.xor(s_b) == s_b
    assert Nothing.xor(Nothing) == Nothing

def test_ok_or() -> None:
    s = Some(1)

    assert s.ok_or('failure') == Ok(1)
    assert Nothing.ok_or('failure') == Err('failure')
