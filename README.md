# py-maybetype

Documentation: <https://py-maybetype.readthedocs.io/en/latest/>

A basic implementation of a maybe/option type in Python, largely inspired by Rust's `Option`.
This was created as part of a separate project I had been working on, but I decided to make it into
its own package as I wanted to use it elsewhere and its scope grew. This is not meant to be a 1:1
replication or replacement for Rust's `Option` or Haskell's `Maybe`, as it does not implement an
additional `Some`/`Just` type, but rather just an interperetation of the idea that I feel works for
Python.

## Usage

Install the package with `pip` using the repository link:

```bash
pip install git+https://github.com/svioletg/py-maybetype
```

Call the `Maybe` constructor with a `T | None` value to create a `Maybe[T]`.

```python
from maybetype import Maybe

def try_int(x: str) -> int | None:
    """Attempts to convert a string of digits into an `int`, returning `None` if not possible."""
    try:
        return int(x)
    except ValueError:
        return None

num1: Maybe[int] = Maybe(try_int('5'))
num2: Maybe[int] = Maybe(try_int('five'))

print(num1.unwrap()) # 5
print(num2.unwrap()) # (raises ValueError)

# Maybe instances are falsy if Maybe(None), truthy otherwise

assert bool(num1) is True
assert bool(num2) is False
```

This example in particular can also be done with `Maybe`'s built-in `int()` class method:

```python
num1: Maybe[int] = Maybe.int('5')
num2: Maybe[int] = Maybe.int('five')
```

The `Maybe` constructor can be given an additional optional argument to specify a condition
in which `Maybe(None)` is returned regardless of if the value in question is truly `None`. This
argument must be a `Callable` that returns `bool`, where returning `False` causes the constructor
to return `Maybe(None)`.

```python
import re
import uuid

from maybetype import Maybe

def is_valid_uuid(s: str) -> bool:
    return re.match(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}|[0-9a-f]{32}", s) is not None

assert Maybe('3b1bcc3a-41d5-49a5-8273-10cc605e31f9', is_valid_uuid)
assert Maybe('3b1bcc3a41d549a5827310cc605e31f9', is_valid_uuid)
assert not Maybe('qwertyuiopasdfghjklzxcvbnm', is_valid_uuid)
assert not Maybe('nf0cmmdq-l0gt-rq5a-upry-706trht3ocv9', is_valid_uuid)
```

## Other examples

Converting a `str | None` timestamp into a `datetime` object if not `None`, otherwise returning `None`:

```python
from datetime import datetime
from maybetype import Maybe

date_str = '2025-09-06T030000'
date = Maybe('2025-09-06T030000').then(datetime.fromisoformat)
# date == datetime.datetime(2025, 9, 6, 3, 0)

date_str = None
date = Maybe(date_str).then(datetime.fromisoformat)
# date == None

date_str = ''
date = Maybe(date_str or None).then(datetime.fromisoformat)
# date == None
# Maybe does not treat falsy values as None, only strictly x-is-None values
# Without `or None` here, datetime.fromisoformat would have raised a ValueError
```
