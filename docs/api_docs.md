Final targets: PipestatManager
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


# Package `pipestat` Documentation

## <a name="PipestatManager"></a> Class `PipestatManager`
Pipestat standardizes reporting of pipeline results and pipeline status management. It formalizes a way for pipeline developers and downstream tools developers to communicate -- results produced by a pipeline can easily and reliably become an input for downstream analyses. The object exposes API for interacting with the results and pipeline status and can be backed by either a YAML-formatted file or a PostgreSQL database.


```python
def __init__(self, namespace=None, record_identifier=None, schema_path=None, results_file_path=None, database_only=False, config=None, status_schema_path=None, flag_file_dir=None)
```

Initialize the object
#### Parameters:

- `namespace` (`str`):  namespace to report into. This will be the DBtable name if using DB as the object back-end
- `record_identifier` (`str`):  record identifier to report for. Thiscreates a weak bound to the record, which can be overriden in this object method calls
- `schema_path` (`str`):  path to the output schema that formalizesthe results structure
- `results_file_path` (`str`):  YAML file to report into, if file isused as the object back-end
- `database_only` (`bool`):  whether the reported data should not bestored in the memory, but only in the database
- `config` (`str | dict`):  path to the configuration file or a mappingwith the config file content
- `status_schema_path` (`str`):  path to the status schema that formalizesthe status flags structure




```python
def assert_results_defined(self, results)
```

Assert provided list of results is defined in the schema
#### Parameters:

- `results` (`list[str]`):  list of results tocheck for existence in the schema


#### Raises:

- `SchemaError`:  if any of the results is not defined in the schema




```python
def check_connection(self)
```

Check whether a PostgreSQL connection has been established
#### Returns:

- `bool`:  whether the connection has been established




```python
def check_record_exists(self, record_identifier=None)
```

Check if the record exists
#### Parameters:

- `record_identifier` (`str`):  unique identifier of the record


#### Returns:

- `bool`:  whether the record exists




```python
def check_result_exists(self, result_identifier, record_identifier=None)
```

Check if the result has been reported
#### Parameters:

- `record_identifier` (`str`):  unique identifier of the record
- `result_identifier` (`str`):  name of the result to check


#### Returns:

- `bool`:  whether the specified result has been reported for theindicated record in current namespace




```python
def clear_status(self, record_identifier=None, flag_names=None)
```

Remove status flags
#### Parameters:

- `record_identifier` (`str`):  name of the record to remove flags for
- `flag_names` (`Iterable[str]`):  Names of flags to remove, optional; ifunspecified, all schema-defined flag names will be used.


#### Returns:

- `list[str]`:  Collection of names of flags removed




```python
def close_postgres_connection(self)
```

Close connection and remove client bound



```python
def config_path(self)
```

Config path. None if the config was not provided or if provided as a mapping of the config contents
#### Returns:

- `str`:  path to the provided config




```python
def data(self)
```

Data object
#### Returns:

- `yacman.YacAttMap`:  the object that stores the reported data




```python
def db_cursor(self)
```

Establish connection and get a PostgreSQL database cursor, commit and close the connection afterwards
#### Returns:

- `LoggingCursor`:  Database cursor object




```python
def establish_postgres_connection(self, suppress=False)
```

Establish PostgreSQL connection using the config data
#### Parameters:

- `suppress` (`bool`):  whether to suppress any connection errors


#### Returns:

- `bool`:  whether the connection has been established successfully




```python
def file(self)
```

File path that the object is reporting the results into
#### Returns:

- `str`:  file path that the object is reporting the results into




```python
def get_status(self, record_identifier=None)
```

Get the current pipeline status
#### Returns:

- `str`:  status identifier, like 'running'




```python
def get_status_flag_path(self, status_identifier, record_identifier=None)
```

Get the path to the status file flag
#### Parameters:

- `status_identifier` (`str`):  one of the defined status IDs in schema
- `record_identifier` (`str`):  unique record ID, optional ifspecified in the object constructor


#### Returns:

- `str`:  absolute path to the flag file or None if object isbacked by a DB




```python
def highlighted_results(self)
```

Highlighted results
#### Returns:

- `list[str]`:  a collection of highlighted results




```python
def namespace(self)
```

Namespace the object writes the results to
#### Returns:

- `str`:  namespace the object writes the results to




```python
def record_count(self)
```

Number of records reported
#### Returns:

- `int`:  number of records reported




```python
def record_identifier(self)
```

Unique identifier of the record
#### Returns:

- `str`:  unique identifier of the record




```python
def remove(self, record_identifier=None, result_identifier=None)
```

Remove a result.

If no result ID specified or last result is removed, the entire record
will be removed.
#### Parameters:

- `record_identifier` (`str`):  unique identifier of the record
- `result_identifier` (`str`):  name of the result to be removed or Noneif the record should be removed.


#### Returns:

- `bool`:  whether the result has been removed




```python
def report(self, values, record_identifier=None, force_overwrite=False, strict_type=True, return_id=False)
```

Report a result.
#### Parameters:

- `values` (`dict[str, any]`):  dictionary of result-value pairs
- `record_identifier` (`str`):  unique identifier of the record, valuein 'record_identifier' column to look for to determine if the record already exists
- `force_overwrite` (`bool`):  whether to overwrite the existing record
- `strict_type` (`bool`):  whether the type of the reported values shouldremain as is. Pipestat would attempt to convert to the schema-defined one otherwise
- `return_id` (`bool`):  PostgreSQL IDs of the records that have beenupdated. Not available with results file as backend


#### Returns:

- `bool | int`:  whether the result has been reported or the ID ofthe updated record in the table, if requested




```python
def result_schemas(self)
```

Result schema mappings
#### Returns:

- `dict`:  schemas that formalize the structure of each resultin a canonical jsonschema way




```python
def retrieve(self, record_identifier=None, result_identifier=None)
```

Retrieve a result for a record.

If no result ID specified, results for the entire record will
be returned.
#### Parameters:

- `record_identifier` (`str`):  unique identifier of the record
- `result_identifier` (`str`):  name of the result to be retrieved


#### Returns:

- `any | dict[str, any]`:  a single result or a mapping with all theresults reported for the record




```python
def schema(self)
```

Schema mapping
#### Returns:

- `dict`:  schema that formalizes the results structure




```python
def schema_path(self)
```

Schema path
#### Returns:

- `str`:  path to the provided schema




```python
def select(self, columns=None, condition=None, condition_val=None, offset=None, limit=None)
```

Get all the contents from the selected table, possibly restricted by the provided condition.
#### Parameters:

- `columns` (`str | list[str]`):  columns to select
- `condition` (`str`):  condition to restrict the resultswith, will be appended to the end of the SELECT statement and safely populated with 'condition_val', for example: `"id=%s"`
- `condition_val` (`list`):  values to fill the placeholderin 'condition' with
- `offset` (`int`):  number of records to be skipped
- `limit` (`int`):  max number of records to be returned


#### Returns:

- `list[psycopg2.extras.DictRow]`:  all table contents




```python
def set_status(self, status_identifier, record_identifier=None)
```

Set pipeline run status.

The status identifier needs to match one of identifiers specified in
the status schema. A basic, ready to use, status schema is shipped with
 this package.
#### Parameters:

- `status_identifier` (`str`):  status to set, one of statuses definedin the status schema
- `record_identifier` (`str`):  record identifier to set thepipeline status for




```python
def status_schema(self)
```

Status schema mapping
#### Returns:

- `dict`:  schema that formalizes the pipeline status structure




```python
def status_schema_source(self)
```

Status schema source
#### Returns:

- `dict`:  source of the schema that formalizesthe pipeline status structure




```python
def validate_schema(self)
```

Check schema for any possible issues
#### Raises:

- `SchemaError`:  if any schema format issue is detected







*Version Information: `pipestat` v0.0.2, generated by `lucidoc` v0.4.3*
