Could not determine whether object for '__builtins__' is repeated; skipping (unhashable type: 'dict')
Object for __package__ is already bound to __name__ and will be documented as such
Could not determine whether object for '__path__' is repeated; skipping (unhashable type: 'list')
Could not determine whether object for '__spec__' is repeated; skipping (unhashable type: 'ModuleSpec')
Final targets: ALIASES_KEY, ALIASES_KEY_RAW, ATTR_KEYS, AliasError, AliasedYacAttMap, DEFAULT_RO, DEFAULT_WAIT_TIME, FILEPATH_KEY, FileFormatError, IK, Iterable, LOCK_PREFIX, Mapping, ORI_STATE_KEY, RO_KEY, SCHEMA_KEY, USE_LOCKS_KEY, UndefinedAliasError, ValidationError, WAIT_MAX_KEY, WRITE_VALIDATE_KEY, YacAttMap, __cached__, __doc__, __file__, __loader__, __name__, __version__, _version, alias, attmap, const, create_lock, exceptions, expandpath, get_first_env_var, getfullargspec, is_aliases_mapping_valid, is_url, load_yaml, logging, make_lock_path, mkabs, my_construct_mapping, my_construct_pairs, os, remove_lock, select_config, warn, warnings, yacman, yaml
<script>
document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('h3 code').forEach((block) => {
    hljs.highlightBlock(block);
  });
});
</script>

<style>
h3 .content { 
    padding-left: 22px;
    text-indent: -15px;
 }
h3 .hljs .content {
    padding-left: 20px;
    margin-left: 0px;
    text-indent: -15px;
    martin-bottom: 0px;
}
h4 .content, table .content, p .content, li .content { margin-left: 30px; }
h4 .content { 
    font-style: italic;
    font-size: 1em;
    margin-bottom: 0px;
}

</style>


# Package `yacman` Documentation

## <a name="AliasError"></a> Class `AliasError`
Alias related error.


## <a name="AliasedYacAttMap"></a> Class `AliasedYacAttMap`
A class that extends YacAttMap to provide alias feature.

The items in the object can be accessed using the original key or an alias,
if defined in the aliases Mapping.


```python
def __init__(self, entries=None, filepath=None, yamldata=None, writable=False, wait_max=60, skip_read_lock=False, aliases=None, exact=False, aliases_strict=None)
```

Object constructor
#### Parameters:

- `entries` (`Iterable[(str, object)] | Mapping[str, object]`):  YAMLcollection of key-value pairs.
- `filepath` (`str`):  YAML filepath to the config file.
- `yamldata` (`str`):  YAML-formatted string
- `writable` (`bool`):  whether to create the object with writecapabilities
- `wait_max` (`int`):  how long to wait for creating an object when thefile that data will be read from is locked
- `skip_read_lock` (`bool`):  whether the file should not be locked forreading when object is created in read only mode
- `aliases` (`Mapping | callable(self) -> Mapping`):  aliases mapping touse or a callable that produces such a mapping out of the object to set the aliases for
- `aliases_strict` (`bool`):  how to handle aliases mapping issues;None for warning, True for AliasError, False to disregard
- `exact` (`bool`):  whether aliases should not be used, even if defined




```python
def alias_dict(self)
```

Get the alias mapping bound to the object
#### Returns:

- `dict`:  alias-key mapping (one to one)




```python
def file_path(self)
```

Return the path to the config file or None if not set
#### Returns:

- `str | None`:  path to the file the object will would to




```python
def get_aliases(self, key)
```

Get the alias for key in the object
#### Parameters:

- `key` (`str`):  key to find an alias for


#### Returns:

- `list[str]`:  aliases matched by the key


#### Raises:

- `GenomeConfigFormatError`:  if aliases mapping has not been definedfor this object
- `UndefinedAliasError`:  if no alias has been defined for therequested key




```python
def get_key(self, alias)
```

Get the key for alias in the object
#### Parameters:

- `alias` (`str`):  alias to find a key for


#### Returns:

- `str`:  key match by the alias


#### Raises:

- `GenomeConfigFormatError`:  if aliases mapping has not been definedfor this object
- `UndefinedAliasError`:  if a no key has been defined for therequested alias




```python
def remove_aliases(self, key, aliases=None)
```

Remove an alias from the object.
#### Parameters:

- `key` (`str`):  name of the key to remove
- `aliases` (`str`):  list of aliases to remove


#### Returns:

- `list[str]`:  list of removed aliases




```python
def set_aliases(self, key, aliases, overwrite=False, reset_key=False)
```

Assign an alias to a key in the object.
#### Parameters:

- `key` (`str`):  name of the key to assign to an alias for
- `aliases` (`str | list[str]`):  alias to use
- `overwrite` (`bool`):  whether to force overwrite the key for analready defined alias
- `reset_key` (`bool`):  whether to force remove existing aliasesfor a key


#### Returns:

- `list[str]`:  list of set aliases




```python
def writable(self)
```

Return writability flag or None if not set
#### Returns:

- `bool | None`:  whether the object is writable now




## <a name="FileFormatError"></a> Class `FileFormatError`
Exception for invalid file format.


## <a name="Iterable"></a> Class `Iterable`
## <a name="Mapping"></a> Class `Mapping`
```python
def get(self, key, default=None)
```

D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.



```python
def items(self)
```

D.items() -> a set-like object providing a view on D's items



```python
def keys(self)
```

D.keys() -> a set-like object providing a view on D's keys



```python
def values(self)
```

D.values() -> an object providing a view on D's values



## <a name="UndefinedAliasError"></a> Class `UndefinedAliasError`
Alias is is not defined.


## <a name="ValidationError"></a> Class `ValidationError`
An instance was invalid under a provided schema.


```python
def absolute_path(self)
```



```python
def absolute_schema_path(self)
```



```python
def create_from(cls, other)
```



## <a name="YacAttMap"></a> Class `YacAttMap`
A class that extends AttMap to provide yaml reading and race-free writing in multi-user contexts.

The YacAttMap class is a YAML Configuration Attribute Map. Think of it as a
Python representation of your YAML configuration file, that can do a lot of cool
stuff. You can access the hierarchical YAML attributes with dot notation or dict
notation. You can read and write YAML config files with easy functions. It also
retains memory of the its source filepath. If both a filepath and an entries
dict are provided, it will first load the file and then updated it with
values from the dict. Moreover, the config contents can be validated against a
jsonschema schema, if a path to one is provided.


```python
def __init__(self, entries=None, filepath=None, yamldata=None, writable=False, wait_max=60, skip_read_lock=False, schema_source=None, write_validate=False)
```

Object constructor
#### Parameters:

- `entries` (`Iterable[(str, object)] | Mapping[str, object]`):  YAML collectionof key-value pairs.
- `filepath` (`str`):  YAML filepath to the config file.
- `yamldata` (`str`):  YAML-formatted string
- `writable` (`bool`):  whether to create the object with write capabilities
- `wait_max` (`int`):  how long to wait for creating an object when the filethat data will be read from is locked
- `skip_read_lock` (`bool`):  whether the file should not be locked for readingwhen object is created in read only mode
- `schema_source` (`str`):  path or a URL to a jsonschema in YAML format to usefor optional config validation. If this argument is provided the object is always validated at least once, at the object creation stage.
- `write_validate` (`bool`):  a boolean indicating whether the object should bevalidated every time the `write` method is executed, which is a way of preventing invalid config writing




```python
def file_path(self)
```

Return the path to the config file or None if not set
#### Returns:

- `str | None`:  path to the file the object will would to




```python
def make_readonly(self)
```

Remove lock and make the object read only.
#### Returns:

- `bool`:  a logical indicating whether any locks were removed




```python
def make_writable(self, filepath=None)
```

Grant write capabilities to the object and re-read the file.

Any changes made to the attributes are overwritten so that the object
reflects the contents of the specified config file
#### Parameters:

- `filepath` (`str`):  path to the file that the contents will be written to


#### Returns:

- `YacAttMap`:  updated object




```python
def validate(self, schema=None, exclude_case=False)
```

Validate the object against a schema
#### Parameters:

- `schema` (`dict`):  a schema object to use to validate, it overrides the onethat has been provided at object construction stage
- `exclude_case` (`bool`):  whether to exclude validated objectsfrom the error. Useful when used with large configs




```python
def writable(self)
```

Return writability flag or None if not set
#### Returns:

- `bool | None`:  whether the object is writable now




```python
def write(self, filepath=None, schema=None, exclude_case=False)
```

Write the contents to a file.

Make sure that the object has been created with write capabilities
#### Parameters:

- `filepath` (`str`):  a file path to write to
- `schema` (`dict`):  a schema object to use to validate, it overrides the onethat has been provided at object construction stage


#### Returns:

- `str`:  the path to the created files


#### Raises:

- `OSError`:  when the object has been created in a read only mode or otherprocess has locked the file
- `TypeError`:  when the filepath cannot be determined. This takes place onlyif YacAttMap initialized with a Mapping as an input, not read from file.
- `OSError`:  when the write is called on an object with no write capabilitiesor when writing to a file that is locked by a different object




```python
def create_lock(filepath, wait_max=10)
```

Securely create a lock file
#### Parameters:

- `filepath` (`str`):  path to a file to lock
- `wait_max` (`int`):  max wait time if the file in question is already locked




```python
def expandpath(path)
```

Expand a filesystem path that may or may not contain user/env vars.
#### Parameters:

- `path` (`str`):  path to expand


#### Returns:

- `str`:  expanded version of input path




```python
def get_first_env_var(ev)
```

Get the name and value of the first set environment variable
#### Parameters:

- `ev` (`str | Iterable[str]`):  a list of the environment variable names


#### Returns:

- `(str, str)`:  name and the value of the environment variable




```python
def getfullargspec(func)
```

Get the names and default values of a callable object's parameters.

A tuple of seven things is returned:
(args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations).
'args' is a list of the parameter names.
'varargs' and 'varkw' are the names of the * and ** parameters or None.
'defaults' is an n-tuple of the default values of the last n parameters.
'kwonlyargs' is a list of keyword-only parameter names.
'kwonlydefaults' is a dictionary mapping names from kwonlyargs to defaults.
'annotations' is a dictionary mapping parameter names to annotations.
Notable differences from inspect.signature():
  - the "self" parameter is always reported, even for bound methods
  - wrapper chains defined by __wrapped__ *not* unwrapped automatically



```python
def is_aliases_mapping_valid(aliases, strictness=None)
```

Determine if the aliases mapping is formatted properly, e.g. {"k": ["v"]}
#### Parameters:

- `aliases` (`Mapping[list]`):  mapping to verify
- `strictness` (`bool`):  how to handle format issues


#### Returns:

- `bool`:  whether the mapping adheres to the correct format




```python
def is_url(maybe_url)
```

Determine whether a path is a URL.
#### Parameters:

- `maybe_url` (`str`):  path to investigate as URL


#### Returns:

- `bool`:  whether path appears to be a URL




```python
def load_yaml(filepath)
```

Load a yaml file into a python dict



```python
def make_lock_path(lock_name_base)
```

Create a collection of path to locks file with given name as bases.
#### Parameters:

- `lock_name_base` (`str | list[str]`):  Lock file names


#### Returns:

- `str | list[str]`:  Path to the lock files.




```python
def mkabs(path, reldir=None)
```

Makes sure a path is absolute; if not already absolute, it's made absolute relative to a given directory. Also expands ~ and environment variables for kicks.
#### Parameters:

- `path` (`str`):  Path to make absolute
- `reldir` (`str`):  Relative directory to make path absolute from if it'snot already absolute




```python
def my_construct_mapping(self, node, deep=False)
```



```python
def my_construct_pairs(self, node, deep=False)
```



```python
def remove_lock(filepath)
```

Remove lock
#### Parameters:

- `filepath` (`str`):  path to the file to remove the lock for.Not the path to the lock!


#### Returns:

- `bool`:  whether the lock was found and removed




```python
def select_config(config_filepath=None, config_env_vars=None, default_config_filepath=None, check_exist=True, on_missing=<function <lambda> at 0x7fd91a43f730>, strict_env=False)
```

Selects the config file to load.

This uses a priority ordering to first choose a config filepath if it's given,
but if not, then look in a priority list of environment variables and choose
the first available filepath to return.
#### Parameters:

- `config_filepath` (`str | NoneType`):  direct filepath specification
- `config_env_vars` (`Iterable[str] | NoneType`):  names of environmentvariables to try for config filepaths
- `default_config_filepath` (`str`):  default value if no other alternativeresolution succeeds
- `check_exist` (`bool`):  whether to check for path existence as file
- `on_missing` (`function(str) -> object`):  what to do with a filepath if itdoesn't exist
- `strict_env` (`bool`):  whether to raise an exception if no file path providedand environment variables do not point to any files raise: OSError: when strict environment variables validation is not passed







*Version Information: `yacman` v0.8.0-dev, generated by `lucidoc` v0.4.3*
