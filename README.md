<img src="https://raw.githubusercontent.com/databio/yacman/master/docs/img/yacman_logo.svg?sanitize=true" alt="yacman" height="70"/><br>
![Run pytests](https://github.com/databio/yacman/workflows/Run%20pytests/badge.svg)
![Test locking parallel](https://github.com/databio/yacman/workflows/Test%20locking%20parallel/badge.svg)
[![codecov](https://codecov.io/gh/databio/yacman/branch/master/graph/badge.svg)](https://codecov.io/gh/databio/yacman)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/yacman/badges/version.svg)](https://anaconda.org/conda-forge/yacman)

Yacman is a YAML configuration manager. It provides some convenience tools for dealing with YAML configuration files.

Please see [this](docs/usage.md) Python notebook for features and usage instructions and [this](docs/api_docs.md) document for API documentation.

## Upgrading guide

How to upgrade to yacman v1.0.0.

There are some transition objects in the 0.9.3 to help with transition.

### Use the FutureYAMLConfigManager in 0.9.3

1. Import the FutureYAMLConfigManager

Change from:

```
from yacman import YAMLConfigManager
```

to 

```
from yacman import FutureYAMLConfigManager as YAMLConfigManager
```

Once we switch from `v0.9.3` to `v1.X.X`, you will need to switch back.

2. Update any context managers to use `write_lock` or `read_lock`

```
from yacman import write_lock, read_lock
```

Change

```
with ym as locked_ym:
	locked_ym.write()

```	

to


```
with write_lock(ym) as locked_ym:
	locked_ym.write()
```

3. Update any constructors to use the `from_{x}` functions

You can no longer just create a `YAMLConfigManager` object directly; now you need to use the constructor helpers.


## From v0.9.3 (using future) to v1.X.X:

Switch back to: 

```
from yacman import YAMLConfigManager
```
