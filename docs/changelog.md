# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. 

## [0.6.2] -- 2019-10-10

### Changed

- in `select_config` always use default config file path when no valid path is determined 


## [0.6.1] -- 2019-10-08

### Added
- `strict_env` argument to the `select_config` function

### Changed
- in `select_config` use the `default_config_filepath` even if no `config_env_vars` were specified 

## [0.6.0] -- 2019-10-02

### Added
- add support for multi-user context operation
- `writable` argument to create the object in a read-only or writable mode
- `wait_max` argument to specify the wait time for the lock before raising a `RuntimeError`
- `unlock` method
- `make_writable` method

### Changed
- entries argument accepting a file path becomes deprecated and throws a `DeprecationWarning` and will be removed altogether in the future release

## [0.5.2] -- 2019-08-20

### Changed
- Force all indexes to be strings (not floats or ints).

## [0.5.1] -- 2019-08-02

### Added
- Allow providing a yaml string to constructor.

## [0.5.0] -- 2019-06-18

### Added
- Improve constructor to allow either a dict or a filepath
- Make printing prettier

## [0.4.2] -- 2019-06-18

### Changed
- Parameterize existence check for `select_config`.

## [0.4.1] -- 2019-06-14

### Changed
- Parameterize behavior when `select_config` filepath argument does not exist.

## [0.4.0] -- 2019-06-07

### Fixed
- Fix bug when building a `YacAttMap` with a filepath in Python 2.7: [Issue 6](https://github.com/databio/yacman/issues/6)

### CHanged
- Defer exception handling from `load_yaml` to client code.

## [0.3.0] -- 2019-06-04

### Added
- Allow a YacAttMap to remember its own path so it can use `write` without an argument.

## [0.2.0] -- 2019-05-21

### Changed
- Changed `select_load` to just `select` so you load on your own.

### Fixed
- Fixed packaging bug

## [0.1.0] -- 2019-05-15
- First functional public release of `yacman`.
