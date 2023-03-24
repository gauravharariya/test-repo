"""Schema that will be used to Dump as well as Load Data from Controllers
   for DB models we will use SQLAlchemySchema,
   the fields will be auto derived from models.
   Only if it's a Nested field or Enum field ,
   we will have to define it on schema.
"""
import marshmallow as ma
from flask_smorest.fields import Upload
from marshmallow import validates_schema, ValidationError
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import SQLAlchemySchema, fields

from app.constants import (
    SchemaType,
    FileFormatType,
    CompressionAlgorithm,
    ScheduleType,
    CodeLanguage,
    PipelineTaskState,
    PipelineTaskStatus,
    PipelineTaskType,
)
from app.models import (
    Domain,
    DataProvider,
    Client,
    Schema,
    SchemaColumn,
    FileFormat,
    SFTPSource,
    DataAssetInstance,
    DataAsset,
    DataIngest,
    FunctionArgument,
    Function,
    FunctionMapping,
    PipelineTask,
)


class BaseModelSchema(SQLAlchemySchema):
    created_at = ma.fields.DateTime(dump_only=True)
    updated_at = ma.fields.DateTime(dump_only=True)


class DomainSchema(BaseModelSchema):
    class Meta:
        model = Domain
        ordered = True
        fields = ["id", "name", "database", "db_schema", "created_at", "updated_at"]


class DataProviderSchema(BaseModelSchema):
    class Meta:
        model = DataProvider
        ordered = True
        fields = [
            "id",
            "name",
            "type",
            "contact_name",
            "contact_email",
            "created_at",
            "updated_at",
        ]


class ClientSchema(BaseModelSchema):
    class Meta:
        model = Client
        ordered = True
        fields = ["id", "name", "is_active", "created_at", "updated_at"]


class DataAssetSchemaColumnSchema(BaseModelSchema):
    class Meta:
        model = SchemaColumn
        ordered = True
        fields = [
            "id",
            "column_number",
            "column_name",
            "tags",
            "data_type",
            "is_custom_column",
            "is_nullable",
            "is_foreign_key",
            "is_primary_key",
            "created_at",
            "updated_at",
        ]


class DataAssetSchemaSchema(BaseModelSchema):
    type = EnumField(SchemaType)
    columns = fields.Nested(DataAssetSchemaColumnSchema(), many=True)

    class Meta:
        ordered = True
        model = Schema
        fields = ["id", "type", "columns", "created_at", "updated_at"]


class FileFormatSchema(BaseModelSchema):
    format_type = EnumField(FileFormatType)
    compression = EnumField(CompressionAlgorithm)

    class Meta:
        model = FileFormat
        ordered = True
        fields = [
            "id",
            "name",
            "format_type",
            "compression",
            "column_separator",
            "row_separator",
            "null_string",
            "is_trimmed",
            "skip_header_lines",
            "is_column_mismatch_error_raised",
            "escape_character",
            "escape_unenclosed_field",
            "date_format",
            "timestamp_format",
            "is_active",
            "is_global",
            "created_at",
            "updated_at",
        ]


class SFTPSourceSchema(BaseModelSchema):
    class Meta:
        model = SFTPSource
        ordered = True
        fields = [
            "id",
            "host",
            "port",
            "user",
            "passphrase",
            "source_path",
            "backup_dir",
            "created_at",
            "updated_at",
        ]


class DataIngestSchema(BaseModelSchema):
    class Meta:
        ordered = True
        model = DataIngest
        fields = [
            "id",
            "name",
            "source_name",
            "auto_ingest",
            "aws_sns_topic",
            "comment",
            "error_integration",
            "created_at",
            "updated_at",
        ]


class DataAssetSchema(BaseModelSchema):
    # restricted domain dump for nested
    domain = fields.Nested(DomainSchema(only=["id", "name"]))
    schema = fields.Nested(DataAssetSchemaSchema())

    class Meta:
        model = DataAsset
        ordered = True
        fields = [
            "id",
            "domain",
            "schema",
            "name",
            "description",
            "s3_bucket",
            "s3_path_prefix",
            "s3_partition_path",
            "instance_default_database",
            "instance_default_db_schema",
            "created_at",
            "updated_at",
        ]


class DataAssetInstanceSchema(BaseModelSchema):
    # restricted data_asset asset, data_ingest, client & data_provider dump for nested
    data_asset = fields.Nested(
        DataAssetSchema(
            only=[
                "id",
                "domain",
                "name",
                "s3_bucket",
                "s3_path_prefix",
                "s3_partition_path",
                "instance_default_database",
                "instance_default_db_schema",
            ]
        )
    )
    data_ingest = fields.Nested(
        DataIngestSchema(only=["id", "name", "source_name", "auto_ingest"])
    )
    file_format = fields.Nested(FileFormatSchema())
    schema = fields.Nested(DataAssetSchemaSchema())
    client = fields.Nested(ClientSchema(only=["id", "name"]))
    data_provider = fields.Nested(DataProviderSchema(only=["id", "name"]))
    schedule_type = EnumField(ScheduleType)

    class Meta:
        model = DataAssetInstance
        ordered = True
        fields = [
            "id",
            "data_asset",
            "data_ingest",
            "file_format",
            "schema",
            "client",
            "data_provider",
            "source_type",
            "source_id",
            "name",
            "description",
            "db_schema",
            "materialization_type",
            "tags",
            "stage_name",
            "start_time",
            "expires",
            "one_off",
            "enabled",
            "schedule_type",
            "schedule_cron",
            "created_at",
            "updated_at",
        ]


# function schema
class FunctionArgumentSchema(BaseModelSchema):
    class Meta:
        model = FunctionArgument
        ordered = True
        fields = [
            "id",
            "name",
            "description",
            "default_value",
            "data_type",
            "created_at",
            "updated_at",
        ]


class FunctionSchema(BaseModelSchema):
    arguments = fields.Nested(FunctionArgumentSchema(many=True))
    code_language = EnumField(CodeLanguage)

    class Meta:
        model = Function
        ordered = True
        fields = [
            "id",
            "name",
            "description",
            "code",
            "code_language",
            "arguments",
            "created_at",
            "updated_at",
        ]


class FunctionMappingSchema(BaseModelSchema):
    function = fields.Nested(FunctionSchema())

    class Meta:
        model = FunctionMapping
        ordered = True
        fields = [
            "id",
            "function",
            "argument_value",
            "alias_name",
            "seq_num",
            "created_at",
            "updated_at",
        ]


class DataAssetInstanceUpsertRequestSchema(ma.Schema):
    file = Upload(allow_none=False, required=True)


# Metadata Schema
class PipelineTaskSchema(BaseModelSchema):
    state = EnumField(PipelineTaskState)
    status = EnumField(PipelineTaskStatus)
    task_type = EnumField(PipelineTaskType, required=True)
    service_name = ma.fields.String(required=True)
    extra_info = ma.fields.Dict(required=False)

    @validates_schema
    def validate(self, data, *, session=None, **kwargs):
        # only enforce during create
        if not self.partial:
            data_asset_instance_id = data.get("data_asset_instance_id")
            data_asset_id = data.get("data_asset_id")
            if not any([data_asset_id, data_asset_instance_id]):
                raise ValidationError(
                    "Either data asset instance or data asset is required",
                    field_name="data_asset_instance_id",
                )
        return data

    class Meta:
        model = PipelineTask
        ordered = True
        fields = [
            "id",
            "data_asset_instance_id",
            "data_asset_id",
            "external_id",
            "service_name",
            "task_type",
            "state",
            "status",
            "extra_info",
            "started_at",
            "ended_at",
            "created_at",
            "updated_at",
        ]


# List Schemas (used to load/dump many records, List APIs)
domains_schema = DomainSchema(many=True)
data_providers_schema = DataProviderSchema(many=True)
clients_schema = ClientSchema(many=True)
data_assets_schema = DataAssetSchema(many=True, exclude=["schema"])
data_asset_instances_schema = DataAssetInstanceSchema(
    many=True, exclude=["file_format", "schema", "data_ingest"]
)
function_mappings_schema = FunctionMappingSchema(many=True)

# Get Schemas ( used to load/dump single record)
domain_schema = DomainSchema()
data_provider_schema = DataProviderSchema()
client_schema = ClientSchema()
data_asset_schema = DataAssetSchema()
data_asset_instance_schema = DataAssetInstanceSchema()
sftp_source_schema = SFTPSourceSchema()
pipeline_task_schema = PipelineTaskSchema()
