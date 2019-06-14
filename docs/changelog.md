# Changelog

## [0.4.1] -- 2019-06-14
- Parameterize behavior when `select_config` filepath argument does not exist.

## [0.4.0] -- 2019-06-07
- Fix bug when building a `YacAttMap` with a filepath in Python 2.7: [Issue 6](https://github.com/databio/yacman/issues/6)
- Defer exception handling from `load_yaml` to client code.

## [0.3.0] -- 2019-06-04
- Allow a YacAttMap to remember its own path so it can use `write` without an argument.

## [0.2.0] -- 2019-05-21
- Fixed packaging bug
- Changed `select_load` to just `select` so you load on your own.

## [0.1.0] -- 2019-05-15
- First functional public release of `yacman`.
