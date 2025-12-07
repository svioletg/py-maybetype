# py-maybetype

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
```

This example in particular can also be done with `Maybe`'s built-in `int()` class method:

```python
from maybetype import Maybe

num1: Maybe[int] = Maybe.int('5')
num2: Maybe[int] = Maybe.int('five')
```
