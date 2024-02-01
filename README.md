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
Yacman v1 provides 2 feature upgrades:

1. Constructors take the form of `yacman.YAMLConfigManager.from_x(...)` functions, to make it clearer how to 
create a new `ym` object.
2. It separates locks into read locks and write locks, to allow mutliple simultaneous readers.

The v0.9.3 transition release would has versions, really: 
- attmap-based version (YacAttMap)
- non-attmap-but-mostly-compatible (YAMLConfigManager)
- new future object (FutureYAMLConfigManager...), which is not-backwards-compatible.

In v1.0.0, FutureYAMLConfigManager will be renamed to YAMLConfigManager and the old stuff will be removed.
Here's how to transition your code:

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



More examples:

```

from yacman import FutureYAMLConfigManager as YAMLConfigManager


data = {"my_list": [1,2,3], "my_int": 8, "my_str": "hello world!", "my_dict": {"nested_val": 15}}

ym = YAMLConfigManager(data)

ym["my_list"]
ym["my_int"]
ym["my_dict"]

# Use in a context manager to write to the file

ym["new_var"] = 15

with write(ym) as locked_ym:
    locked_ym.rebase()
	locked_ym.write()

with read(ym) as locked_ym:
	locked_ym.rebase()

```




3. Update any constructors to use the `from_{x}` functions

You can no longer just create a `YAMLConfigManager` object directly; now you need to use the constructor helpers.

Examples:

```
from yacman import FutureYAMLConfigManager as YAMLConfigManager

data = {"my_list": [1,2,3], "my_int": 8, "my_str": "hello world!", "my_dict": {"nested_val": 15}}
file_path = "tests/data/full.yaml"
yaml_data = "myvar: myval"

yacman.YAMLConfigManager.from_yaml_file(file_path)
yacman.YAMLConfigManager.from_yaml_data(yaml_data)
yacman.YAMLConfigManager.from_obj(data)

```

In the past, you could load from a file and overwrite some attributes with a dict of variables, all from the constructor.
Now it would is more explicit:

```
ym = yacman.YacMan.from_yaml_file(file_path)
ym.update_from_obj(data)
```

To exppand environment variables in values, use `.exp`.

```
ym.exp["text_expand_home_dir"]
```

## From v0.9.3 (using future) to v1.X.X:

Switch back to: 

```
from yacman import YAMLConfigManager
```





## Demos

Some interactive demos

```
from yacman import FutureYAMLConfigManager as YAMLConfigManager
ym = yacman.YAMLConfigManager(entries=["a", "b", "c"])
ym.to_dict()
ym

print(ym.to_yaml())

ym = YAMLConfigManager(entries={"top": {"bottom": ["a", "b"], "bottom2": "a"}, "b": "c"})
ym
print(ym.to_yaml())

ym = YAMLConfigManager(filepath="tests/data/conf_schema.yaml")
print(ym.to_yaml())
ym

ym = YAMLConfigManager(filepath="tests/data/empty.yaml")
print(ym.to_yaml())

ym = YAMLConfigManager(filepath="tests/data/list.yaml")
print(ym.to_yaml())

ym = YAMLConfigManager(YAMLConfigManager(filepath="tests/data/full.yaml").exp)
print(ym.to_yaml())

ym = YAMLConfigManager(filepath="tests/data/full.yaml")
print(ym.to_yaml(expand=True))

```