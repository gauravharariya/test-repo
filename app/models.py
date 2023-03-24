from sqlalchemy import func, Sequence, String
from sqlalchemy.orm import declared_attr
from sqlalchemy_utils import generic_relationship, ScalarListType, JSONType

from app import db
from app.constants import (
    SchemaType,
    FileFormatType,
    CompressionAlgorithm,
    FIELD_DELIMITER,
    ROW_DELIMITER,
    NULL_IF,
    ESCAPE_UNENCLOSED_FIELD,
    DEFAULT_DATE_TIMESTAMP_FORMAT,
    ScheduleType,
    CodeLanguage,
    DEFAULT_HEADER_LINES,
    INSTANCE_PATH_PREFIX,
    PipelineTaskState,
    CONFIGURATION_SCHEMA,
    METADATA_SCHEMA,
    PipelineTaskStatus,
    PipelineTaskType,
)


# Base Model that defines primary key and audit field standards
# TODO: enhancement to query to filter out soft delete records
class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {"schema": None}

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    @declared_attr
    def id(self):  # noqa
        return db.Column(
            db.Integer,
            Sequence(
                f"{self.__tablename__}_id_seq", schema=self.__table_args__["schema"]
            ),
            primary_key=True,
        )

    created_at = db.Column(
        db.DateTime(timezone=True), server_default=func.current_timestamp()
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


# Soft Deletable base model
class BaseSoftDeleteModel(BaseModel):
    __abstract__ = True
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


# Schema base models
class ConfigurationSchemaBaseModel(BaseSoftDeleteModel):
    __abstract__ = True
    __table_args__ = {"schema": CONFIGURATION_SCHEMA}


class MetadataSchemaBaseModel(BaseSoftDeleteModel):
    __abstract__ = True
    __table_args__ = {"schema": METADATA_SCHEMA}


# Client & Data Provider Models
class Domain(ConfigurationSchemaBaseModel):
    name = db.Column(db.String(length=256), nullable=False, unique=True)
    database = db.Column(db.String(length=256), nullable=False)
    db_schema = db.Column(db.String(length=256), nullable=False)


class DataProvider(ConfigurationSchemaBaseModel):
    name = db.Column(db.String(length=256), nullable=False)
    type = db.Column(db.String(length=256), nullable=True)
    contact_name = db.Column(db.String(length=256), nullable=True)
    contact_email = db.Column(db.String(length=256), nullable=True)


class Client(ConfigurationSchemaBaseModel):
    name = db.Column(db.String(length=256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


# External Data Source Models
class SFTPSource(ConfigurationSchemaBaseModel):
    host = db.Column(db.String(length=256), nullable=False)
    port = db.Column(db.Integer, default=22, nullable=False)
    user = db.Column(db.String(length=256), nullable=False)
    passphrase = db.Column(String(length=256), nullable=False)
    source_path = db.Column(db.String(length=256), nullable=False)
    backup_dir = db.Column(db.String(length=256), nullable=True)


# Schema models
class Schema(ConfigurationSchemaBaseModel):
    type = db.Column(db.Enum(SchemaType), nullable=False)


class SchemaColumn(ConfigurationSchemaBaseModel):
    schema_id = db.Column(db.Integer, db.ForeignKey(Schema.id), nullable=False)
    schema = db.relationship("Schema", backref=db.backref("columns", lazy="joined"))
    column_number = db.Column(db.Integer, nullable=True)
    column_name = db.Column(db.String(length=256), nullable=False)
    # cannot use ARRAY -> https://github.com/snowflakedb/snowflake-sqlalchemy/issues/299
    tags = db.Column(ScalarListType(str), nullable=True, default=list)
    data_type = db.Column(db.String(length=256), nullable=False)
    is_custom_column = db.Column(db.Boolean, default=False)
    is_nullable = db.Column(db.Boolean, default=True)
    is_foreign_key = db.Column(db.Boolean, default=False)
    is_primary_key = db.Column(db.Boolean, default=False)


# Data Ingest Models
class FileFormat(ConfigurationSchemaBaseModel):
    name = db.Column(db.String(length=256), nullable=False)
    format_type = db.Column(db.Enum(FileFormatType), nullable=False)
    compression = db.Column(
        db.Enum(CompressionAlgorithm), nullable=True, default=CompressionAlgorithm.AUTO
    )
    column_separator = db.Column(
        db.String(length=32), default=FIELD_DELIMITER, nullable=True
    )
    row_separator = db.Column(
        db.String(length=32), default=ROW_DELIMITER, nullable=True
    )
    null_string = db.Column(db.String(length=32), default=NULL_IF, nullable=False)
    is_trimmed = db.Column(db.Boolean, default=False)
    skip_header_lines = db.Column(db.Integer, default=DEFAULT_HEADER_LINES)
    is_column_mismatch_error_raised = db.Column(db.Boolean, default=True)
    escape_character = db.Column(db.String(length=128), nullable=True)
    escape_unenclosed_field = db.Column(
        db.String(length=128), default=ESCAPE_UNENCLOSED_FIELD, nullable=True
    )
    date_format = db.Column(
        db.String(length=256), default=DEFAULT_DATE_TIMESTAMP_FORMAT, nullable=False
    )
    timestamp_format = db.Column(
        db.String(length=256), default=DEFAULT_DATE_TIMESTAMP_FORMAT, nullable=False
    )
    # metadata fields
    is_active = db.Column(db.Boolean, default=True)
    # to mark few global file formats
    is_global = db.Column(db.Boolean, default=False)


class DataIngest(ConfigurationSchemaBaseModel):
    name = db.Column(db.String(length=256), nullable=False)
    source_name = db.Column(db.String(length=256), nullable=False)
    auto_ingest = db.Column(db.Boolean, default=False)
    aws_sns_topic = db.Column(db.String(length=256), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    error_integration = db.Column(db.Text, nullable=True)


# Data Asset Models
class DataAsset(ConfigurationSchemaBaseModel):
    domain_id = db.Column(db.Integer, db.ForeignKey(Domain.id), nullable=False)
    domain = db.relationship("Domain", backref=db.backref("data_assets", lazy="joined"))
    schema_id = db.Column(db.Integer, db.ForeignKey(Schema.id), nullable=False)
    schema = db.relationship("Schema", backref=db.backref("data_assets", lazy="joined"))
    name = db.Column(db.String(length=256), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    s3_bucket = db.Column(db.String(length=256), nullable=False)
    s3_path_prefix = db.Column(
        db.String(length=1025), server_default=INSTANCE_PATH_PREFIX, nullable=False
    )
    s3_partition_path = db.Column(db.String(length=1025), nullable=False)
    instance_default_database = db.Column(db.String(length=256), nullable=False)
    instance_default_db_schema = db.Column(db.String(length=256), nullable=False)


class DataAssetInstance(ConfigurationSchemaBaseModel):
    data_asset_id = db.Column(db.Integer, db.ForeignKey(DataAsset.id), nullable=False)
    data_asset = db.relationship(
        "DataAsset", backref=db.backref("instances", lazy="joined")
    )
    file_format_id = db.Column(db.Integer, db.ForeignKey(FileFormat.id), nullable=False)
    file_format = db.relationship(
        "FileFormat", backref=db.backref("instances", lazy="joined")
    )
    schema_id = db.Column(db.Integer, db.ForeignKey(Schema.id), nullable=False)
    schema = db.relationship("Schema", backref=db.backref("instances", lazy="joined"))
    client_id = db.Column(db.Integer, db.ForeignKey(Client.id), nullable=False)
    client = db.relationship("Client", backref=db.backref("instances", lazy="joined"))
    data_provider_id = db.Column(
        db.Integer, db.ForeignKey(DataProvider.id), nullable=False
    )
    data_provider = db.relationship(
        "DataProvider", backref=db.backref("instances", lazy="joined")
    )
    data_ingest_id = db.Column(db.Integer, db.ForeignKey(DataIngest.id), nullable=True)
    data_ingest = db.relationship(
        "DataIngest", backref=db.backref("instances", lazy="joined")
    )
    source_type = db.Column(db.Unicode(length=255), nullable=False)
    source_id = db.Column(db.Integer)
    source = generic_relationship(source_type, source_id)
    name = db.Column(db.String(length=256), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    database = db.Column(db.String(length=256), nullable=True)
    db_schema = db.Column(db.String(length=256), nullable=True)
    materialization_type = db.Column(db.String(length=256), nullable=False)
    tags = db.Column(ScalarListType(str), nullable=True, default=list)
    stage_name = db.Column(db.String(length=256), nullable=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=True)
    expires = db.Column(db.DateTime(timezone=True), nullable=True)
    one_off = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    schedule_type = db.Column(db.Enum(ScheduleType), nullable=False)
    schedule_cron = db.Column(db.String(length=256), nullable=True)


# Functions & Function Mapping models
class Function(ConfigurationSchemaBaseModel):
    name = db.Column(db.String(length=1024), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    code = db.Column(db.Text(), nullable=False)
    code_language = db.Column(
        db.Enum(CodeLanguage), default=CodeLanguage.SQL, nullable=False
    )


class FunctionArgument(ConfigurationSchemaBaseModel):
    function_id = db.Column(db.Integer, db.ForeignKey(Function.id), nullable=False)
    function = db.relationship(
        "Function", backref=db.backref("arguments", lazy="joined")
    )
    name = db.Column(db.String(length=256), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    default_value = db.Column(db.String(length=256), nullable=True)
    data_type = db.Column(db.String(length=256), nullable=False)


class FunctionMapping(ConfigurationSchemaBaseModel):
    data_asset_instance_id = db.Column(
        db.Integer, db.ForeignKey(DataAssetInstance.id), nullable=False
    )
    data_asset_instance = db.relationship(
        "DataAssetInstance", backref=db.backref("function_mappings", lazy="select")
    )
    function_id = db.Column(db.Integer, db.ForeignKey(Function.id), nullable=False)
    function = db.relationship(
        "Function", backref=db.backref("function_mappings", lazy="joined")
    )
    argument_value = db.Column(JSONType, nullable=True)
    alias_name = db.Column(db.String(length=256), nullable=True)
    seq_num = db.Column(db.Integer, nullable=False)


# Metadata Tables
class PipelineTask(MetadataSchemaBaseModel):
    data_asset_instance_id = db.Column(
        db.Integer, db.ForeignKey(DataAssetInstance.id), nullable=True
    )
    data_asset_instance = db.relationship(
        "DataAssetInstance", backref=db.backref("pipeline_tasks", lazy="select")
    )
    data_asset_id = db.Column(db.Integer, db.ForeignKey(DataAsset.id), nullable=True)
    data_asset = db.relationship(
        "DataAsset", backref=db.backref("pipeline_tasks", lazy="joined")
    )
    external_id = db.Column(db.String(length=256), nullable=True)
    service_name = db.Column(db.String(length=256), nullable=False)
    # task type performed by service
    task_type = db.Column(db.Enum(PipelineTaskType), nullable=False)
    # state of the pipeline task, running, completed etc.
    state = db.Column(
        db.Enum(PipelineTaskState), default=PipelineTaskState.QUEUED, nullable=False
    )
    # status of task, success, failed etc.
    status = db.Column(db.Enum(PipelineTaskStatus), nullable=True)
    extra_info = db.Column(JSONType, nullable=True)
    started_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    # if status is done, then ended_at needs to be populated
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
