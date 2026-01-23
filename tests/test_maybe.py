import re
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from string import ascii_lowercase
from types import EllipsisType
from typing import Any

import pytest

from maybetype import Maybe, Nothing, Some, _Nothing, maybe

ALPHANUMERIC: str = ascii_lowercase + '0123456789'
MAYBE_UNWRAP_NONE_REGEX: re.Pattern[str] = re.compile(r"Maybe\[.*\] unwrapped into None")

def square(n: int) -> int:
    return n * n

def test_maybe_none_unwrap_error() -> None:
    m_none: Maybe[Any] = Nothing
    assert bool(m_none) is False
    with pytest.raises(ValueError, match=MAYBE_UNWRAP_NONE_REGEX):
        m_none.unwrap()
    with pytest.raises(TypeError, match='Custom error message'):
        m_none.unwrap(exc=TypeError('Custom error message'))

def test_maybe_none_is_nothing() -> None:
    assert maybe(None) is Nothing

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
    assert _Nothing(val).val is None # type: ignore

def test_maybe_this_or() -> None:
    assert Maybe.int('10').this_or(0).unwrap() == 10  # noqa: PLR2004
    assert Maybe.int('ten').this_or(0).unwrap() == 0
    with pytest.raises(ValueError, match=MAYBE_UNWRAP_NONE_REGEX):
        Maybe.int('ten').unwrap()

@pytest.mark.parametrize(('val', 'default'),
    [
        (5, 10),
        (5, None),
        ('string', 'fallback'),
        ('string', None),
    ],
)
def test_maybe_unwrap_or(val: object, default: object) -> None:
    assert maybe(val).unwrap_or(default) == val
    assert maybe(None).unwrap_or(default) == default

@pytest.mark.parametrize(('val', 'then_fn'),
    [
      # (wrapped value, (.then() function, expected return val), expected wrapped value after function)
        (0,                (lambda i: i * 10, 0, ...)),
        (1,                (lambda i: i * 10, 10, ...)),
        ('',               (lambda s: s.upper(), '', ...)),
        ('string',         (lambda s: s.upper(), 'STRING', ...)),
        ('a,b,c',          (lambda s: s.split(','), ['a', 'b', 'c'], ...)),
        ([1, 2, 3],        (lambda l: l.append(4), None, [1, 2, 3, 4])), # noqa: E741
        ({'a': 1, 'b': 2}, (lambda d: d.get('a'), 1, ...)),
    ],
    ids=[
        'int_zero',
        'int_one',
        'str_empty',
        'str_nonempty',
        'str_split',
        'list',
        'dict',
    ],
)
def test_maybe_then[T, R, A](val: T, then_fn: tuple[Callable[[T], R], R, A | EllipsisType]) -> None:
    m: Maybe[T] = maybe(val)
    assert bool(m) is True
    assert m.unwrap() == val
    m_before = deepcopy(m.val)
    assert m.then(then_fn[0]) == then_fn[1]
    assert m.unwrap() == (then_fn[2] if then_fn[2] is not Ellipsis else m_before)
    assert maybe(None).then(then_fn[0]) is None

def test_maybe_attr() -> None:
    @dataclass
    class A:
        x: int

    @dataclass
    class B(A):
        y: float

    m_none: Maybe[A] = maybe(None)
    assert m_none.attr('x').val is None
    assert m_none.attr_or('x', 2) == 2  # noqa: PLR2004

    m_a: Maybe[A] = maybe(A(1))
    assert m_a.attr('x').unwrap() == 1
    assert m_a.attr_or('x', 2) == 1
    assert m_a.attr('y').val is None
    assert m_a.attr_or('y', 2) == 2  # noqa: PLR2004

    m_b: Maybe[B] = maybe(B(1, 2.0))
    assert m_b.attr('x').unwrap() == 1
    assert m_b.attr_or('x', 2) == 1
    assert m_b.attr('y').unwrap() == 2.0  # noqa: PLR2004
    assert m_b.attr_or('y', 3) == 2.0  # noqa: PLR2004

@pytest.mark.parametrize(('val', 'accessor', 'result'),
    [
        (None,             1,   maybe(None)),
        ([1, 2, 3],        1,   maybe(2)),
        ([1, 2, 3],        3,   maybe(None)),
        ([],               1,   maybe(None)),
        ({'a': 1, 'b': 2}, 'a', maybe(1)),
        ({'a': 1, 'b': 2}, 'c', maybe(None)),
        ({},               'a', maybe(None)),
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
    assert Maybe.cat(map(Maybe.int, ALPHANUMERIC)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_maybe_cat_failure() -> None:
    with pytest.raises(AttributeError, match='has no attribute \'unwrap\''):
        Maybe.cat([1, 2, 3]) # type: ignore

def test_maybe_map() -> None:
    assert Maybe.map(Maybe.int, ALPHANUMERIC) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

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
def test_maybe_with_predicate[T](value: T, predicate: Callable[[T], bool], expected_bool: bool) -> None:
    assert bool(maybe(value, predicate)) is expected_bool
    if expected_bool is False:
        assert maybe(value, predicate) is Nothing

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
def test_maybe_pattern_matching[T](value: T, predicate: Callable[[T], bool], expected: T | None) -> None:
    if expected is Ellipsis:
        expected = value

    match maybe(value, predicate):
        case Some(value):
            result = value
        case _:
            result = None

    assert result == expected

@pytest.mark.parametrize(('value', 'fn', 'expected'),
    [
        (None, square, Nothing),
        (0, square, Some(0)),
        (5, square, Some(25)),
        ('image.png', lambda s: s.split('.')[0], Some('image')),
    ],
)
def test_maybe_and_then[T, U](value: T, fn: Callable[[T], U], expected: Maybe[T]) -> None:
    assert maybe(value).and_then(fn) == expected
