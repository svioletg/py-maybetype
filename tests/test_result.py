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

def test_unwrap() -> None:
    assert Ok(1).unwrap() == 1
    with pytest.raises(ResultUnwrapError, match='failure'):
        Err('failure').unwrap()
