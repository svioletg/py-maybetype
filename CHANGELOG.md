# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0]

### Added

- Added the `is_none_if` argument to `Maybe`'s constructor, a function that
  takes the to-be-wrapped value as an argument, which allows defining a custom
  condition in which `Maybe(None)` will be returned if the function returns `False`
  - e.g. `Maybe(0) == Maybe(0)`, however `Maybe(0, lambda x: x > 0) == Maybe(None)`

## [0.2.0] - 2025-12-08

### Added

- Added test module `tests/test_maybe.py`

## [0.1.0] - 2025-12-07
