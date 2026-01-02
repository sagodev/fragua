"""Enums classes type."""

from enum import Enum


# -------------------
# ARCHITECTURE
# -------------------


class ActionType(str, Enum):
    """Fragua actions type class."""

    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"


EXTRACT = ActionType.EXTRACT
TRANSFORM = ActionType.TRANSFORM
LOAD = ActionType.LOAD


class ComponentType(str, Enum):
    """Fragua components kind class."""

    AGENT = "agent"
    FUNCTION = "function"
    INTERNAL_TRANSFORM_FUNCTION = "internal_transform_functions"
    INTERNAL_LOAD_FUNCTION = "internal_load_functions"
    ENVIRONMENT = "environment"
    REGISTRY = "registry"
    SET = "set"
    WAREHOUSE = "warehouse"
    ACTIONS = "actions"
    STORAGE = "storage"


AGENT = ComponentType.AGENT
FUNCTION = ComponentType.FUNCTION
INTERNAL_TRANSFORM_FUNCTION = ComponentType.INTERNAL_TRANSFORM_FUNCTION
INTERNAL_LOAD_FUNCTION = ComponentType.INTERNAL_LOAD_FUNCTION


class TargetType(str, Enum):
    """Target types class."""

    EXCEL = "excel"
    CSV = "csv"
    API = "api"
    SQL = "sql"
    ML = "ml"
    REPORT = "report"
    ANALYSIS = "analysis"


EXCEL = TargetType.EXCEL
CSV = TargetType.CSV
API = TargetType.API
SQL = TargetType.SQL
ML = TargetType.ML
REPORT = TargetType.REPORT
ANALYSIS = TargetType.ANALYSIS


class OperationType(str, Enum):
    """Operation types class."""

    GET = "get"
    POST = "post"
    DELETE = "delete"
    UPDATE = "update"
    ADD = "add"
    CREATE = "create"

    READ = "read"
    WRITE = "write"
    COPY = "copy"

    UNDO = "undo"
    RENAME = "rename"


GET = OperationType.GET
POST = OperationType.POST
DELETE = OperationType.DELETE
UPDATE = OperationType.UPDATE
ADD = OperationType.ADD
CREATE = OperationType.CREATE


class FieldType(str, Enum):
    """Field params types class."""

    PATH = "path"
    SHEET_NAME = "sheet_name"
    CONNECTION_STRING = "connection_string"
    QUERY = "query"
    URL = "url"
    METHOD = "method"
    HEADERS = "headers"
    PARAMS = "params"
    DATA = "data"
    AUTH = "auth"
    PROXY = "proxy"
    TIMEOUT = "timeout"

    ACTION = "action"
    PURPOSE = "purpose"
    STEPS = "steps"
    STORAGE_TYPE = "storage_type"
    FUNCTION = "function"
    FUNC_KEY = "function_key"

    DIRECTORY = "directory"
    FILE_NAME = "file_name"
    INDEX = "index"
    ENGINE = "engine"
    SEPARATOR = "separator"
    HEADER = "header"
    ENCODING = "encoding"
    TABLE_NAME = "table_name"
    IF_EXISTS = "if_exists"
    DELIMITER = "delimiter"
    CHUNKSIZE = "chunksize"
    ENDPOINT = "endpoint"

    BACKUP = "backup"


class AttrType(str, Enum):
    """Attribute types class."""

    NAME = "name"
    TYPE = "type"
    CLASS = "class"
    REQUIRED = "required"
    DESCRIPTION = "description"
    NORMALIZE = "normalize"
    DEFAULT = "default"


class MetadataType(str, Enum):
    """Metadata types class."""

    BASE = "base"
    SAVE = "save"

    TIMESTAMP = "timestamp"
    OPERATION = "operation"
    TOKEN_ID = "token_id"
    OPERATIONS_COUNT = "operations_count"
    OPERATIONS_DONE = "operations_done"
    STORAGE_COUNT = "storage_count"
    STORAGES = "storages"
    LOG_ENTRIES = "log_entries"
    ROWS = "rows"
    COLS = "cols"
    METADATA_TYPE = "metadata_type"
    LOCA_TIME = "local_time"
    TIMEZONE_OFFSET = "timezone_offset"
