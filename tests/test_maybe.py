import re
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from string import ascii_lowercase
from types import EllipsisType

import pytest

from maybetype import Maybe

ALPHANUMERIC: str = ascii_lowercase + '0123456789'
MAYBE_UNWRAP_NONE_REGEX: re.Pattern[str] = re.compile(r"Maybe\[.*\] unwrapped into None")

def test_maybe_none_unwrap_error() -> None:
    m_none: Maybe[None] = Maybe(None)
    assert bool(m_none) is False
    with pytest.raises(ValueError, match=MAYBE_UNWRAP_NONE_REGEX):
        m_none.unwrap()
    with pytest.raises(TypeError, match='Custom error message'):
        m_none.unwrap(exc=TypeError('Custom error message'))

def test_maybe_this_or() -> None:
    assert Maybe.int('10').this_or(0).unwrap() == 10  # noqa: PLR2004
    assert Maybe.int('ten').this_or(0).unwrap() == 0
    with pytest.raises(ValueError, match=MAYBE_UNWRAP_NONE_REGEX):
        Maybe.int('ten').unwrap()

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
    m: Maybe[T] = Maybe(val)
    assert bool(m) is True
    assert m.unwrap() == val
    m_before = deepcopy(m.val)
    assert m.then(then_fn[0]) == then_fn[1]
    assert m.unwrap() == (then_fn[2] if then_fn[2] is not Ellipsis else m_before)
    assert Maybe(None).then(then_fn[0]) is None

def test_maybe_attr() -> None:
    @dataclass
    class A:
        x: int

    @dataclass
    class B(A):
        y: float

    m_none: Maybe[A] = Maybe(None)
    assert m_none.attr('x').val is None
    assert m_none.attr_or('x', 2) == 2  # noqa: PLR2004

    m_a: Maybe[A] = Maybe(A(1))
    assert m_a.attr('x').unwrap() == 1
    assert m_a.attr_or('x', 2) == 1
    assert m_a.attr('y').val is None
    assert m_a.attr_or('y', 2) == 2  # noqa: PLR2004

    m_b: Maybe[B] = Maybe(B(1, 2.0))
    assert m_b.attr('x').unwrap() == 1
    assert m_b.attr_or('x', 2) == 1
    assert m_b.attr('y').unwrap() == 2.0  # noqa: PLR2004
    assert m_b.attr_or('y', 3) == 2.0  # noqa: PLR2004

@pytest.mark.parametrize(('val', 'accessor', 'result'),
    [
        (None,             1,   Maybe(None)),
        ([1, 2, 3],        1,   Maybe(2)),
        ([1, 2, 3],        3,   Maybe(None)),
        ([],               1,   Maybe(None)),
        ({'a': 1, 'b': 2}, 'a', Maybe(1)),
        ({'a': 1, 'b': 2}, 'c', Maybe(None)),
        ({},               'a', Maybe(None)),
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
    m: Maybe = Maybe(val)
    assert m.get(accessor) == result

def test_maybe_cat() -> None:
    assert Maybe.cat(map(Maybe.int, ALPHANUMERIC)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_maybe_map() -> None:
    assert Maybe.map(Maybe.int, ALPHANUMERIC) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def is_valid_uuid(s: str) -> bool:
    return re.match(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}|[0-9a-f]{32}", s) is not None

@pytest.mark.parametrize(('value', 'just_condition', 'expected_bool'),
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
def test_maybe_just_condition[T](value: T, just_condition: Callable[[T], bool], expected_bool: bool) -> None:  # noqa: FBT001
    assert bool(Maybe(value, just_condition)) is expected_bool
