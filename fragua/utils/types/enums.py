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
    STYLE = "style"
    PARAMS = "params"


AGENT = ComponentType.AGENT
FUNCTION = ComponentType.FUNCTION
STYLE = ComponentType.STYLE
PARAMS = ComponentType.PARAMS


class AgentType(str, Enum):
    """Agent types class."""

    EXTRACTOR = "extractor"
    TRANSFORMER = "transformer"
    LOADER = "loader"


EXTRACTOR = AgentType.EXTRACTOR
TRANSFORMER = AgentType.TRANSFORMER
LOADER = AgentType.LOADER


class StorageType(str, Enum):
    """Storage types class."""

    BOX = "box"
    CONTAINER = "container"
    ALL = "all"


BOX = StorageType.BOX
CONTAINER = StorageType.CONTAINER


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
    FIELDS = "fields"
    PARAMS_TYPE = "params_type"
    FUNCTION = "function"

    FUNC_KEY = "function_key"

    DESTINATION = "destination"
    FILE_NAME = "file_name"
    INDEX = "index"
    ENGINE = "engine"
    SEPARATOR = "separator"
    HEADER = "header"
    ENCODING = "encoding"
    TABLE_NAME = "table_name"
    IF_EXISTS = "if_exists"
    CHUNKSIZE = "chunksize"
    ENDPOINT = "endpoint"


class AttrType(str, Enum):
    """Attribute types class."""

    NAME = "name"
    TYPE = "type"
    CLASS = "class"
    REQUIRED = "required"
    DESCRIPTION = "description"
    NORMALIZE = "normalize"
    DEFAULT = "default"


# -------------------
# INTERNAL FUNCTIONS
# -------------------


class FillMissing(str, Enum):
    """
    Fill missing function config keys.
        - numeric_fill:
        Strategy for numeric columns ("mean" | "zero"). Default: "mean".
        - categorical_fill:
        Fill value for categorical columns. Default: "unknown".
    """

    NUMERIC_FILL = "numeric_fill"
    CATEGORICAL_FILL = "categorical_fill"


class TreatOutliers(str, Enum):
    """
    Treat outliers function config keys.
        - outlier_threshold:
            IQR multiplier used for clipping. Default: 1.5."""

    OUTLIERS_THRESHOLD = "outlier_threshold"


class AddDerivedColumns(str, Enum):
    """
    Add derived columns function config keys.
        - derived_columns:
            Mapping of column names to pandas evaluation expressions.
            If no derived columns are provided and both 'quantity' and 'price'
            columns exist, a default 'total' column is computed.
    """

    DERIVED_COLUMNS = "derived_columns"


class FormatNumeric(str, Enum):
    """
    Format numeric function config keys.
        - rounding_precision:
            Number of decimal places to apply. Default: 2.
    """

    ROUNDING_PRECISION = "rounding_precision"


class GroupAndAggregate(str, Enum):
    """
    Group and aggregate function config keys.
        - groupby_cols:
            List of columns used for grouping.
        - agg_functions:
            Mapping of column names to aggregation functions.
            If omitted, a default 'sum' aggregation is applied.
    """

    GROUP_BY = "group_by_cols"
    AGG_FUNCTIONS = "agg_functions"


class SortBy(str, Enum):
    """
    Sort function config keys.
        - sort_by:
            List of columns to sort by (ascending order).
    """

    SORT_BY = "sort_by"
