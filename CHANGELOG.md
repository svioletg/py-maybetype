# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Generally, more significant breaking changes will be put near the top of each category.

Documentation here: <https://py-maybetype.readthedocs.io/en/latest/reference/>

## Unreleased

### Added

- Added classes `Result`, `Ok`, and `Err` to mimic the behavior of Rust's `Result` type
  - See docs for all introduced methods: <https://py-maybetype.readthedocs.io/en/latest/reference/index.html#maybetype.Result>
- Added the `errors` module
  - Added exception `ResultUnwrapError`
- Added test module `test_result`

### Changed

- Changed docstring of function `maybe` to describe the `predicate` parameter more succinctly
- Updated test `test_maybe.test_maybe_with_predicate_and_filter` to ensure
  `maybe(val).filter(predicate)` is equivalent to `maybe(val, predicate)`
- Instancing `NothingType` more than once now emits a warning suggesting the use of the `Nothing`
  singleton

## [0.10.1] - 2026-03-22

### Fixed

- Fixed `.gitignore` rule mistakenly excluding `maybetype/__init__.py`, thus rendering the package
  effectively empty

## [0.10.0] - 2026-03-21

### Added

- Added method `Maybe.cast`
  - Casts the type of the wrapped value: `maybe(...).cast(int)` → `Maybe[int]`
- Added method `Maybe.flatten`
  - Replicates Rust's [`Option::flatten`](https://doc.rust-lang.org/std/option/enum.Option.html#method.flatten)
- Added method `Maybe.inspect`
  - Replicates Rust's [`Option::inspect`](https://doc.rust-lang.org/std/option/enum.Option.html#method.inspect)
- Added method `Maybe.reduce`
  - Replicates Rust's [`Option::reduce`](https://doc.rust-lang.org/std/option/enum.Option.html#method.reduce)
- Added method `Maybe.replace`
  - Replicates Rust's [`Option::replace`](https://doc.rust-lang.org/std/option/enum.Option.html#method.replace)
- Added method `Maybe.unwrap_or_else`
  - Replicates Rust's [`Option::unwrap_or_else`](https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or_else)
- Added method `Maybe.unzip`
  - Replicates Rust's [`Option::unzip`](https://doc.rust-lang.org/std/option/enum.Option.html#method.unzip)
- Added method `Maybe.xor`
  - Replicates Rust's [`Option::xor`](https://doc.rust-lang.org/std/option/enum.Option.html#method.xor)
- Added method `Maybe.zip`
  - Replicates Rust's [`Option::zip`](https://doc.rust-lang.org/std/option/enum.Option.html#method.zip)
- Added test `test_maybe.test_maybe_cast`
- Added test `test_maybe.test_maybe_flatten`
- Added test `test_maybe.test_maybe_inspect`
- Added test `test_maybe.test_maybe_reduce`
- Added test `test_maybe.test_maybe_replace`
- Added test `test_maybe.test_maybe_unwrap_or_else`
- Added test `test_maybe.test_maybe_unzip`
- Added test `test_maybe.test_maybe_xor`
- Added test `test_maybe.test_maybe_zip`

### Changed

- Renamed attribute `Maybe.val` to `Maybe._val`, should now be treated as a private attribute
- Method `Maybe.and_then` parameter ``func`` now must return ``Maybe``, making it more like
  [`Option::and_then`](https://doc.rust-lang.org/std/option/enum.Option.html#method.and_then)
- Method `Maybe.map` is no longer a static method and is now more in line with
  [`Option::map`](https://doc.rust-lang.org/std/option/enum.Option.html#method.map) in
  functionality
  - The previous behavior of `Maybe.map` is largely unnecessary as it would produce the exact same
    result as calling `Maybe.cat` with a regular `map()` object
- Method `Maybe.attr` now optionally takes a `default` parameter
- Method `Maybe.unwrap` parameter `exc` now defaults to a string instead of `None`, and no longer
  accepts `None`
- Renamed class `_Nothing` to `NothingType`
  - The class was marked as private to encourage use of the `Nothing` singleton instead, but since
    one could want to use the class for type annotations, and the singleton can't be used for
    annotations, it was renamed to both make it no longer private and clarify that it is the type
- Renamed method `Maybe.test` to `Maybe.filter`
  - The docstring for `Maybe.filter` has also been rewritten a bit to be more concise
- A number of tests changed in `test_maybe`:
  - `test_maybe_and_then` rewritten to test for its new functionality
  - `test_maybe_map` rewritten to test for its new functionality
  - `test_maybe_then` rewritten to be less verbose
  - Renamed `test_maybe_with_predicate_and_test` to `test_maybe_with_predicate_and_filter`

### Removed

- Removed method `Maybe.attr_or`
- Removed parameter `err` from method `Maybe.attr`

## [0.9.0] - 2026-03-15

### Added

- Added method `Maybe.bind`
  - Largely the same as Haskell's `>>=`, `x.bind(f)` is essentially the same as `x >>= f`
- Added test `test_maybe.test_bind`

### Changed

- Added `from __future__ import annotations` import to `maybetype/__init__.py` for unquoted forward
  references
- Added type annotation to `Maybe.val` in `Maybe.__init__` to give more specificity for `ty`
- Removed type variable from signature of `_Nothing` class as it's never used
- Replaced `# type: ignore` directive in test `test_maybe.test_nothing_instance_always_wraps_none`
  with more specific `# ty:ignore[invalid-argument-type]` directive
- Expanded test `test_maybe.test_equality` slightly

### Fixed

- Fixed incorrectly written test `test_maybe.test_maybe_or`

## [0.8.0] - 2026-02-16

### Added

- Added test `test_maybe.test_unwrap_nothing_callback`

### Changed

- Updated a number of docstrings to fix errors or improve clarity
- Changed `Maybe.unwrap()` default error message to a more succinct "unwrapped Nothing"
- Method `Maybe.unwrap()` argument `exc` can now also be a string, in which case `ValueError` is
  raised with that string as its sole argument if the instance was `Nothing`
- Renamed multiple tests in module `test_maybe`:
  - `test_maybe_none_unwrap_error` → `test_unwrap_nothing`
  - `test_maybe_unwrap_or` → `test_unwrap_or`
  - `test_maybe_pattern_matching` → `test_pattern_matching`
- Renamed type variable `R` to `U` in signature of `Maybe.and_then()`
- `exc` argument of method `Maybe.unwrap()` now expects a function that takes no arguments

## [0.7.0] - 2026-02-05

### Added

- Added static method `Maybe.sequence()`
- Added methods to `Maybe`:
  - `and_then()`: Similar to `Maybe.then()`, but returns a `Maybe` instance
  - `test()`: Returns `Some` if the instance is `Some` and the test function returns `True` when
    called with the wrapped value, otherwise returns `Nothing`

### Changed

- Renamed static method `Maybe.int()` to `Maybe.try_int()`
- `Maybe.__hash__()` now returns `hash()` called with the wrapped value instead of accessing its
  `__hash__()` method
- Most type signatures now use the more standard type variable naming of `T`, `U`, `V`...
  - The only exception currently is the static method `Maybe.map()`, which uses `A` and `B` since
    `T` already belongs the `Maybe` class' scope and the method operates on unrelated types

### Removed

- Removed method `Maybe.this_or()`
  - Redundant, `maybe(x).this_or(y)` is exactly the same as `maybe(x) or Some(y)`

## [0.6.0] - 2026-01-21

### Changed

- Project string has been changed from `"maybetype"` to `"py-maybetype"` for getting metadata in
  `const`

## [0.5.0] - 2026-01-18

### Added

- Added `__match_args__` attribute to `Maybe` to allow using its value in `match`/`case` pattern matching
- Added method `Maybe.unwrap_or()`
- Added classes `Some` and `_Nothing`
  - `_Nothing` is intended to be used through the `Nothing` singleton instance, rather than
    constructing new instances of it, since effectively all `_Nothing` instances should behave the
    same
  - Instances of `Some` are **always truthy**, and `Nothing` is **always falsy**
- Added function `maybe()`
  - Returns either a `Some` instance or the `Nothing` singleton depending on the given value and
    predicate, similar to the previous functionality of `Maybe.__init__()`
  - Usage should now replace direct instancing of `Maybe`

### Changed

- `Maybe.__init__()` body moved to `maybe()` function, now simply assigns the passed `val` to its
  `val` attribute
  - A warning is now issued if `Maybe`'s constructor is called directly
- Replaced uses of `NoReturn` with `Never`
- `Maybe.get()` now directly checks for the `__getitem__` method on the wrapped value instead of
  checking `Sequence | Mapping`
- Anywhere `Maybe(None)` would have been returned now returns the `Nothing` singleton

### Fixed

- `Maybe.attr_or()` no longer has a default argument of `None` for its `default` parameter, as the
  docstring describes

## [0.4.0] - 2026-01-02

### Added

- Added module `const`

### Changed

- Updated all docstrings to use reStructuredText markup for Sphinx docs generation

### Fixed

- Fixed the example in `Maybe.cat`'s docstring incorrectly attempting to use `.cat()` on the list
  of `Maybe` objects, now correctly shows usage of `Maybe.cat(vals)`

## [0.3.1] - 2025-12-31

### Fixed

- Corrected the docstring of `Maybe.__init__()`'s description of the `just_condition` parameter,
  which incorrectly stated `just_condition` must return `True` for the constructor to return
  `Maybe(None)`—the opposite is true, `Maybe(None)` is returned if `just_condition` returns `False`

## [0.3.0] - 2025-12-27

### Added

- Added the `just_condition` argument to `Maybe`'s constructor, a function that takes the
  to-be-wrapped value as an argument, which allows defining a custom condition in which
  `Maybe(None)` will be returned if the function returns `False`
  - e.g. `Maybe(0) == Maybe(0)`, however `Maybe(0, lambda x: x > 0) == Maybe(None)`

## [0.2.0] - 2025-12-08

### Added

- Added test module `tests/test_maybe.py`

## [0.1.0] - 2025-12-07
