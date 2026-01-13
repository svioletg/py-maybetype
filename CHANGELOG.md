# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added method `Maybe.unwrap_or()`

### Changed

- `Maybe.__init__()` parameter `just_condition` renamed to `predicate`
- Replaced uses of `NoReturn` with `Never`
- `Maybe.get()` now directly checks for the `__getitem__` method on the wrapped value instead of
  checking `Sequence | Mapping`

### Fixed

- `Maybe.attr_or()` no longer has a default argument of `None` for its `default` parameter, as the
  docstring describes

## [0.4.0]

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
