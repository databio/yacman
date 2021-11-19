# `yacman` features and usage

This short tutorial show you the features of `yacman` package in action.

First, let's prepare some data to work with


```python
import yaml
yaml_dict = {'cfg_version': 0.1, 'lvl1': {'lvl2': {'lvl3': {'entry': ['val1', 'val2']}}}}
yaml_str = """\
cfg_version: 0.1
lvl1:
  lvl2:
    lvl3:
      entry: ["val1","val2"]
"""
filepath = "test.yaml"

with open(filepath, 'w') as f:
    data = yaml.dump(yaml_dict, f)

import yacman
```

##  `YacAttMap` object creation

There are multiple ways to initialize an object of `YacAttMap` class:

1. **Read data from a YAML-formatted file**


```python
yacmap = yacman.YacAttMap(filepath=filepath)
yacmap
```




    cfg_version: 0.1
    lvl1:
      lvl2:
        lvl3:
          entry:
           - val1
           - val2



2. **Read data from an `entries` mapping**


```python
yacmap = yacman.YacAttMap(entries=yaml_dict)
yacmap
```




    cfg_version: 0.1
    lvl1:
      lvl2:
        lvl3:
          entry:
           - val1
           - val2



3. **Read data from a YAML-formatted string**


```python
yacmap = yacman.YacAttMap(yamldata=yaml_str)
yacmap
```




    cfg_version: 0.1
    lvl1:
      lvl2:
        lvl3:
          entry:
           - val1
           - val2



## File locks; race-free writing
Instances of `YacAttMap` class support race-free writing and file locking, so that **it's safe to use them in multi-user contexts**

They can be created with or without write capabilities. Writable objects create a file lock, which prevents other processes managed by `yacman` from updating the source config file.

`writable` argument in the object constructor can be used to toggle writable mode. The source config file can be updated on disk (using `write` method) only if the `YacAttMap` instance is in writable mode


```python
yacmap = yacman.YacAttMap(filepath=filepath, writable=False)


try:
    yacmap.write()
except OSError as e:
    print("Error caught: {}".format(e))
```

    Error caught: You can't call write on an object that was created in read-only mode.


The write capabilities can be granted to an object:


```python
yacmap = yacman.YacAttMap(filepath=filepath, writable=False)
yacmap.make_writable()
yacmap.write()
```




    '/Users/mstolarczyk/code/yacman/docs/test.yaml'



Or withheld:


```python
yacmap.make_readonly()
```




    True



If a file is currently locked by other `YacAttMap` object. The object will not be made writable/created with write capabilities until the lock is gone. If the lock persists, the action will fail (with a `RuntimeError`) after a selected `wait_time`, which is 10s by default:


```python
yacmap = yacman.YacAttMap(filepath=filepath, writable=True)

try:
    yacmap1 = yacman.YacAttMap(filepath=filepath, writable=True, wait_max=1)
except RuntimeError as e:
    print("\nError caught: {}".format(e))
yacmap.make_readonly()
```

    Waiting for file lock: lock.test.yaml ....
    Error caught: The maximum wait time (1) has been reached and the lock file still exists.





    True



Lastly, the `YacAttMap` class instances **can be used in a context manager**. This way the source config file will be locked, possibly updated (depending on what the user chooses to do), safely written to and unlocked with a single line of code:


```python
yacmap = yacman.YacAttMap(filepath=filepath)

with yacmap as y:
    y.test = "test"

yacmap1 = yacman.YacAttMap(filepath=filepath)
yacmap1
```




    cfg_version: 0.1
    lvl1:
      lvl2:
        lvl3:
          entry:
           - val1
           - val2
    test: test



## Key aliases in `AliasedYacAttMap`

`AliasedYacAttMap` is a child class of `YacAttMap` that supports top-level key aliases.

### Defining the aliases

There are two ways the aliases can be defined at the object construction stage:

1. By passing a literal aliases dictionary
2. By passing a function to be executed on the object itself that returns the dictionary

In any case, the resulting aliases mapping has to follow the format presented below:


```python
aliases = {
    "key_1": ["first_key", "key_one"],
    "key_2": ["second_key", "key_two", "fav_key"],
    "key_3": ["third_key", "key_three"]
}
```

#### Literal aliases dictionary
The `aliases` argument in the `AliasedYacAttmap` below is a Python `dict` with that maps the object keys to collection of aliases (Python `list`s of `str`). This format is strictly enforced.


```python
aliased_yacmap = yacman.AliasedYacAttMap(entries={'key_1': 'val_1', 'key_2': 'val_2', 'key_3': 'val_3'},
                                         aliases=aliases)
print(aliased_yacmap)
```

    AliasedYacAttMap
    key_1: val_1
    key_2: val_2
    key_3: val_3


Having set the aliases we can key the object either with the literal key or the aliases:


```python
aliased_yacmap["key_1"] == aliased_yacmap["first_key"]
```




    True




```python
aliased_yacmap["key_two"] == aliased_yacmap["fav_key"]
```




    True



#### Aliases returning function

The `aliases` argument in the `AliasedYacAttmap` below is a Python `callable` that takes the obejcect itself as an argument and returns the desired aliases mapping. This is especially useful when the object itself contains the aliases definition, for example:


```python
entries={
    'key_1': {'value': 'val_1', 'aliases': ['first_key']},
    'key_2': {'value': 'val_2', 'aliases': ['second_key']},
    'key_3': {'value': 'val_3', 'aliases': ['third_key']}
}
```


```python
aliased_yacmap = yacman.AliasedYacAttMap(entries=entries,
                                         aliases=lambda x: {k: v.__getitem__("aliases", expand=False) for k, v in x.items()})
print(aliased_yacmap)
```

    AliasedYacAttMap
    key_1:
      value: val_1
      aliases:
       - first_key
    key_2:
      value: val_2
      aliases:
       - second_key
    key_3:
      value: val_3
      aliases:
       - third_key



```python
aliased_yacmap["key_1"] == aliased_yacmap["first_key"]
```




    True



# `YacAttMap` contents validation

Another very useful feature of `YacAttMap` object is the embedded [jsonschema](https://json-schema.org/) validation.

## Setup

The validation is setup at the `YacAttMap` object creation stage, using `schema_source` and `write_validate` arguments:

- `schema_soruce` takes a path or URL of the YAML-formatted jsonschema file reads it in to a Python `dict`. If this argument is provided the object is always validated at least once, at the object creation stage.
- `write_validate` takes a boolean indicating whether the object should be validated every time the `YacAttMap.write` method is executed, which is a way of preventing invalid config writing

## Validation demonstration

Let's get a path to a YAML-formatted jsonschema and look at the contents:


```python
from attmap import AttMap # disregard, this class can be used to print mappings nicely
schema_path = "../tests/data/conf_schema.yaml"
AttMap(yacman.load_yaml(schema_path))
```




    AttMap
    description: test yacman config file schema
    properties:
      newattr:
        type: string
        pattern: ^\\S*$
        description: string with no whitespace
      testattr:
        type: string
        description: simply a string
      anotherattr:
        type:
         - string
         - integer
        description: string or integer



The schema presented above restrits just 3 top level keys in the `YacAttMap` object to be validated: `newattr`, `testattr` and `anotherattr`. Each of these has to adhere to different requirements, defined in the respective sections.

### At construction validation

Let's pass the path to the schema to the object constructor:


```python
entries = {
    "newattr": "test_string"
}

yacmap = yacman.YacAttMap(entries=entries, schema_source=schema_path)
```

No exceptions were raised, which means that the object passed the validation (`newattr` is a string with no whitespaces).

But what if we added an attribute that is *does not* adhere to the schema requirements?


```python
entries.update({"testattr": 1})
yacmap = yacman.YacAttMap(entries=entries, schema_source=schema_path)
```

    YacAttMap object did not pass schema validation



    ---------------------------------------------------------------------------

    ValidationError                           Traceback (most recent call last)

    <ipython-input-19-d687b0549d77> in <module>
          1 entries.update({"testattr": 1})
    ----> 2 yacmap = yacman.YacAttMap(entries=entries, schema_source=schema_path)


    /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/yacman/yacman.py in __init__(self, entries, filepath, yamldata, writable, wait_max, skip_read_lock, schema_source, write_validate)
        136             # validate config
        137             setattr(self, SCHEMA_KEY, load_yaml(sp))
    --> 138             self.validate()
        139
        140     def __del__(self):


    /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/yacman/yacman.py in validate(self, schema, exclude_case)
        194         """
        195         try:
    --> 196             _validate(self.to_dict(expand=True), schema or getattr(self, SCHEMA_KEY))
        197         except ValidationError as e:
        198             _LOGGER.error(


    ~/Library/Python/3.6/lib/python/site-packages/jsonschema/validators.py in validate(instance, schema, cls, *args, **kwargs)
        897     error = exceptions.best_match(validator.iter_errors(instance))
        898     if error is not None:
    --> 899         raise error
        900
        901


    ValidationError: 1 is not of type 'string'

    Failed validating 'type' in schema['properties']['testattr']:
        {'description': 'simply a string', 'type': 'string'}

    On instance['testattr']:
        1


As expected, the object did not pass the validation and an informative exception is raised.

### At `write` validation

As mentioned above, the object can be validated when `write` method is called. Let's use the previously created file to demonstrate this feature:


```python
yacmap = yacman.YacAttMap(filepath=filepath, schema_source=schema_path, writable=True, write_validate=True)
yacmap["newattr"] = "test_string"
yacmap.write()
del yacmap
yacmap = yacman.YacAttMap(filepath=filepath, schema_source=schema_path, writable=True, write_validate=True)
yacmap
del yacmap
```

As expected, we were able to add a new attribure to the object and write it to the file, with no issues since the new attribute's value adheres to the schema requirements.

But, if it doesn't, we are not able to write to the file:


```python
yacmap = yacman.YacAttMap(filepath=filepath, schema_source=schema_path, writable=True, write_validate=True)
yacmap["newattr"] = 1
yacmap.write(exclude_case=True)
```

    YacAttMap object did not pass schema validation



    ---------------------------------------------------------------------------

    ValidationError                           Traceback (most recent call last)

    <ipython-input-21-950e3de9fe88> in <module>
          1 yacmap = yacman.YacAttMap(filepath=filepath, schema_source=schema_path, writable=True, write_validate=True)
          2 yacmap["newattr"] = 1
    ----> 3 yacmap.write(exclude_case=True)


    /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/yacman/yacman.py in write(self, filepath, schema, exclude_case)
        233             )
        234         if schema is not None or getattr(self, WRITE_VALIDATE_KEY):
    --> 235             self.validate(schema=schema, exclude_case=exclude_case)
        236         filepath = _check_filepath(filepath or getattr(self, FILEPATH_KEY, None))
        237         lock = make_lock_path(filepath)


    /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/yacman/yacman.py in validate(self, schema, exclude_case)
        206                 raise
        207             raise ValidationError(
    --> 208                 f"{self.__class__.__name__} object did not pass schema validation: "
        209                 f"{e.message}"
        210             )


    ValidationError: YacAttMap object did not pass schema validation: 1 is not of type 'string'


This feature is also available when using `YacAttMap` object in context manager:


```python
del yacmap
```


```python
yacmap = yacman.YacAttMap(filepath=filepath, schema_source=schema_path, writable=True, write_validate=True)

with yacmap as y:
    y['newattr'] = 1
```

    YacAttMap object did not pass schema validation



    ---------------------------------------------------------------------------

    ValidationError                           Traceback (most recent call last)

    <ipython-input-23-9e72f3657d91> in <module>
          2
          3 with yacmap as y:
    ----> 4     y['newattr'] = 1


    /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/yacman/yacman.py in __exit__(self, exc_type, exc_val, exc_tb)
        161     def __exit__(self, exc_type, exc_val, exc_tb):
        162
    --> 163         self.write()
        164         if getattr(self, ORI_STATE_KEY, False):
        165             self.make_readonly()


    /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/yacman/yacman.py in write(self, filepath, schema, exclude_case)
        233             )
        234         if schema is not None or getattr(self, WRITE_VALIDATE_KEY):
    --> 235             self.validate(schema=schema, exclude_case=exclude_case)
        236         filepath = _check_filepath(filepath or getattr(self, FILEPATH_KEY, None))
        237         lock = make_lock_path(filepath)


    /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/yacman/yacman.py in validate(self, schema, exclude_case)
        194         """
        195         try:
    --> 196             _validate(self.to_dict(expand=True), schema or getattr(self, SCHEMA_KEY))
        197         except ValidationError as e:
        198             _LOGGER.error(


    ~/Library/Python/3.6/lib/python/site-packages/jsonschema/validators.py in validate(instance, schema, cls, *args, **kwargs)
        897     error = exceptions.best_match(validator.iter_errors(instance))
        898     if error is not None:
    --> 899         raise error
        900
        901


    ValidationError: 1 is not of type 'string'

    Failed validating 'type' in schema['properties']['newattr']:
        {'description': 'string with no whitespace',
         'pattern': '^\\S*$',
         'type': 'string'}

    On instance['newattr']:
        1
