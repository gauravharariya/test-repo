import enum

# Schema names
CONFIGURATION_SCHEMA = "CONFIGURATION"
METADATA_SCHEMA = "METADATA"
# Data asset constants
INSTANCE_PATH_PREFIX = "{data_provider}/{data_asset}/{client_name}/"

# file format defaults
# Add enums in future for config UI to showcase common options
FIELD_DELIMITER = ","
ROW_DELIMITER = r"\n"
NULL_IF = r"\\N"
DEFAULT_HEADER_LINES = 1
ESCAPE_UNENCLOSED_FIELD = r"\\"
DEFAULT_DATE_TIMESTAMP_FORMAT = "AUTO"


class SchemaType(enum.Enum):
    ASSET = "asset"
    INSTANCE = "instance"


# File format related constants
class FileFormatType(enum.Enum):
    CSV = "CSV"
    JSON = "JSON"
    AVRO = "AVRO"
    ORC = "ORC"
    PARQUET = "PARQUET"
    XML = "XML"


class CompressionAlgorithm(enum.Enum):
    AUTO = "AUTO"
    GZIP = "GZIP"
    BZ2 = "BZ2"
    BROTLI = "BROTLI"
    ZSTD = "ZSTD"
    DEFLATE = "DEFLATE"
    RAW_DEFLATE = "RAW_DEFLATE"
    NONE = "NONE"


# Data asset instance schedule types
class ScheduleType(enum.Enum):
    EVENT = "EVENT"
    CRON = "CRON"


# Function constants
# Code language to be used for functions
class CodeLanguage(enum.Enum):
    SQL = "SQL"


# Metadata
class PipelineTaskType(enum.Enum):
    """
    List of tasks that could be performed by services
    """

    TRANSFER = "TRANSFER"
    DATA_INGEST = "DATA_INGEST"
    TRANSFORM = "TRANSFORM"
    # snowflake specific
    CREATE_FILE_FORMAT = "CREATE_FILE_FORMAT"
    CREATE_STAGE = "CREATE_STAGE"
    CREATE_SNOWPIPE = "CREATE_SNOWPIPE"
    CREATE_TABLE = "CREATE_TABLE"
    ALTER_FILE_FORMAT = "ALTER_FILE_FORMAT"
    ALTER_STAGE = "ALTER_STAGE"
    ALTER_SNOWPIPE = "ALTER_SNOWPIPE"
    ALTER_TABLE = "ALTER_TABLE"


class PipelineTaskState(enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class PipelineTaskStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
