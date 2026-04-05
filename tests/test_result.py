from typing import Never

import pytest

from maybetype import Nothing, Some
from maybetype.errors import ResultUnwrapError
from maybetype.result import Err, Ok, Result


def test_instance() -> None:
    ok = Ok('success')
    assert ok._val == 'success'  # noqa: SLF001
    err = Err('failure')
    assert err._val == 'failure'  # noqa: SLF001

def test_equality() -> None:
    assert Ok(1) == Ok(1)
    assert Ok(1) != Ok(2)
    assert Err('failure') == Err('failure')
    assert Err('failure') != Err('failed')
    assert Ok(1) != Err(1) != Ok(2) != Err(2)

# Result methods

def test_and_then() -> None:
    def func(n: int) -> Result[int, str]:
        return Ok(n * 2) if n < 10 else Err('too big!')  # noqa: PLR2004

    assert Ok(1).and_then(func) == Ok(2)
    assert Ok(10).and_then(func) == Err('too big!')
    assert Err('not a number').and_then(func) == Err('not a number')

def test_to_maybe_err() -> None:
    assert Ok(1).err() is Nothing
    assert Err('failure').err() == Some('failure')

def test_to_maybe_ok() -> None:
    assert Ok(1).ok() == Some(1)
    assert Err('failure').ok() is Nothing

def test_flatten() -> None:
    ok_nest = Ok(Ok(1))
    err_nest = Err(Err('failure'))
    ok_err = Ok(Err('failure'))
    err_ok = Err(Ok(1))

    assert ok_nest.flatten() == Ok(1)
    assert err_nest.flatten() == Err('failure')
    assert ok_err.flatten() == Err('failure')
    assert err_ok.flatten() == Ok(1)

def test_inspect() -> None:
    ok = Ok(1)
    err = Err('failure')

    assert ok.inspect(print) is ok
    assert err.inspect(print) is err

def test_map() -> None:
    ok = Ok(1)
    err = Err('failure')

    def double(n: int) -> int:
        return n * 2

    def to_upper(s: str) -> str:
        return s.upper()

    assert ok.map(double) == Ok(2)
    assert err.map(double) == Err('failure')

    assert ok.map_err(to_upper) == Ok(1)
    assert err.map_err(to_upper) == Err('FAILURE')

    assert ok.map_or(0, double) == 2  # noqa: PLR2004
    assert err.map_or(0, double) == 0

    assert ok.map_or_else(to_upper, double) == 2  # noqa: PLR2004
    assert err.map_or_else(to_upper, double) == 'FAILURE'

def test_unwrap() -> None:
    def abort(e: object) -> Never:
        raise ValueError(e)

    ok = Ok(1)
    err = Err('failure')

    assert ok.unwrap() == 1
    with pytest.raises(ResultUnwrapError, match='\'failure\''):
        err.unwrap()
    with pytest.raises(ResultUnwrapError, match='Something went wrong: \'failure\''):
        err.unwrap('Something went wrong')
    with pytest.raises(ValueError, match='failure'):
        err.unwrap(abort)
    with pytest.raises(ValueError, match='\'failure\''):
        err.unwrap(ValueError)

    assert err.unwrap_err() == 'failure'
    with pytest.raises(ResultUnwrapError, match='1'):
        ok.unwrap_err()
    with pytest.raises(ResultUnwrapError, match='Something went wrong: 1'):
        ok.unwrap_err('Something went wrong')
    with pytest.raises(ValueError, match='1'):
        ok.unwrap_err(abort)
    with pytest.raises(ValueError, match='1'):
        ok.unwrap_err(ValueError)
