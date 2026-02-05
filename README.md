# py-maybetype

![Linting & testing](https://github.com/svioletg/py-maybetype/actions/workflows/lint-test.yml/badge.svg)

Documentation: <https://py-maybetype.readthedocs.io/en/latest/>

PyPI: <https://pypi.org/project/py-maybetype/>

A basic implementation of a maybe/option type in Python, largely inspired by Rust's `Option`.
This was created as part of a separate project I had been working on, but I decided to make it into
its own package as I wanted to use it elsewhere and its scope grew. This is not meant to be a 1:1
replication or replacement for Rust's `Option` or Haskell's `Maybe`, but rather just an
interperetation of the idea that I feel works for Python.

> [!WARNING]
> Breaking changes are likely each update in the 0.x phase. Please check the changelog for these
> changes before updating to a new version.

## Usage

Install with `pip`:

```bash
pip install py-maybetype
```

Call the `maybe()` function with a `T | None` value to return a `Maybe[T]`—either a `Some` instance
containing the wrapped value, or the `Nothing` singleton.

```python
from maybetype import Maybe, maybe

# Only the maybe() function should be used,
# the Maybe class is only imported here for type annotations

def try_int(x: str) -> int | None:
    """Attempts to convert a string of digits into an `int`, returning `None` if not possible."""
    try:
        return int(x)
    except ValueError:
        return None

num1: Maybe[int] = maybe(try_int('5'))
num2: Maybe[int] = maybe(try_int('five'))

print(num1.unwrap()) # 5
print(num2.unwrap()) # (raises ValueError)

# Some() instances are always truthy, Nothing is falsy

assert bool(num1) is True
assert bool(num2) is False
```

This example in particular can also be done with the `Maybe.try_int()` class method:

```python
num1: Maybe[int] = Maybe.try_int('5')
num2: Maybe[int] = Maybe.try_int('five')
```

The `maybe` constructor can be given an optional predicate argument to specify a custom condition
for which `Some(value)` is returned. This argument must be a `Callable` that returns `bool`,
where returning `False` causes the constructor to return `Nothing`.

> [!NOTE]
> `maybe(None)` will always returning `Nothing`, even if `predicate(None)` would return `True`

```python
import re
import uuid

from maybetype import maybe

def is_valid_uuid(s: str) -> bool:
    return re.match(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}|[0-9a-f]{32}", s) is not None

assert maybe('3b1bcc3a-41d5-49a5-8273-10cc605e31f9', is_valid_uuid)
assert maybe('3b1bcc3a41d549a5827310cc605e31f9', is_valid_uuid)
assert not maybe('qwertyuiopasdfghjklzxcvbnm', is_valid_uuid)
assert not maybe('nf0cmmdq-l0gt-rq5a-upry-706trht3ocv9', is_valid_uuid)
```

`Maybe` instances can also be used in `match`/`case` pattern matching to access the wrapped value,
like so:

```python
from maybetype import maybe, Some

match maybe(1):
    case Some(val):
        print('Value: ', val)
    case _: # "case Nothing:" also works, but just matching else in this case will be identical
        print('No value')
```

## Other examples

Converting a `str | None` timestamp into a `datetime` object if not `None`, otherwise returning
`None`:

```python
from datetime import datetime
from maybetype import maybe

assert maybe('2025-09-06T030000').then(datetime.fromisoformat) == datetime(2025, 9, 6, 3, 0)

assert maybe(None).then(datetime.fromisoformat) is None

assert maybe('' or None).then(datetime.fromisoformat) is None
# Maybe does not treat falsy values as None, only strictly x-is-None values
# Without `or None` here, datetime.fromisoformat would have raised a ValueError
```

Converting a `str | None` timestamp into a `datetime` object if not `None`, then ensuring that date
meets certain criteria:

```python
from datetime import datetime
from maybetype import maybe

assert maybe('2025-09-06T030000').and_then(datetime.fromisoformat).test(lambda dt: dt.year > 2024)

assert not maybe('2024-09-06T030000').and_then(datetime.fromisoformat).test(lambda dt: dt.year > 2024)

match maybe('2025-09-06T030000').and_then(datetime.fromisoformat).test(lambda dt: dt.year > 2024):
    case Some(date):
        ... # Do something with the date
    case _:
        ... # Do something else
```
