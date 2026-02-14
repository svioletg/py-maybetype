# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Generally, more significant breaking changes will be put near the top of each category.

## [Unreleased]

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

## [0.7.0]

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
