from datetime import datetime

import pytest
from sqlalchemy import Integer

from app.constants import (
    SchemaType,
    FileFormatType,
    CompressionAlgorithm,
    FIELD_DELIMITER,
    ROW_DELIMITER,
    NULL_IF,
    DEFAULT_HEADER_LINES,
    ESCAPE_UNENCLOSED_FIELD,
    DEFAULT_DATE_TIMESTAMP_FORMAT,
    ScheduleType,
    PipelineTaskState,
    PipelineTaskType,
    PipelineTaskStatus,
)
from app.models import (
    BaseModel,
    Domain,
    FileFormat,
    Client,
    SFTPSource,
    SchemaColumn,
    Schema,
    DataIngest,
    DataAsset,
    DataAssetInstance,
    DataProvider,
    Function,
    FunctionArgument,
    FunctionMapping,
    PipelineTask,
)


@pytest.fixture(scope="session")
def domain_data():
    return {
        "name": "example",
        "database": "example",
        "db_schema": "public",
    }


@pytest.fixture(scope="session")
def domain(db_session, domain_data):
    """Fixture to create a domain instance."""
    domain = Domain(**domain_data)
    db_session.add(domain)
    db_session.commit()
    return domain


@pytest.fixture(scope="session")
def data_provider_data():
    return {
        "name": "Sample Data Provider",
        "type": "Sample Type",
        "contact_name": "Sample Contact",
        "contact_email": "sample@contact.com",
    }


@pytest.fixture(scope="session")
def data_provider(db_session, data_provider_data):
    """Fixture to create a data provider instance."""
    data_provider = DataProvider(**data_provider_data)
    db_session.add(data_provider)
    db_session.commit()
    return data_provider


@pytest.fixture(scope="session")
def client_data():
    return {
        "name": "test_client",
        "is_active": True,
    }


@pytest.fixture(scope="session")
def client(db_session, client_data):
    """Fixture to create a client instance."""
    client = Client(**client_data)
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture(scope="session")
def sftp_data():
    return {
        "host": "test_host",
        "port": 22,
        "user": "test_user",
        "passphrase": "test_passphrase",
        "source_path": "/test/path",
        "backup_dir": None,
    }


@pytest.fixture(scope="session")
def sftp_source(db_session, sftp_data):
    """Fixture to create an SFTP source instance."""
    sftp_source = SFTPSource(**sftp_data)
    db_session.add(sftp_source)
    db_session.commit()
    return sftp_source


@pytest.fixture(scope="session")
def schema_data():
    return {"type": SchemaType.ASSET}


@pytest.fixture(scope="session")
def schema(db_session, schema_data):
    """Fixture to create a schema instance."""
    schema = Schema(**schema_data)
    db_session.add(schema)
    db_session.commit()
    return schema


@pytest.fixture(scope="session")
def schema_column_data(schema):
    return {
        "schema_id": schema.id,
        "column_number": 1,
        "column_name": "column1",
        "tags": ["tag1", "tag2"],
        "data_type": "VARCHAR",
        "is_custom_column": False,
        "is_nullable": True,
        "is_foreign_key": False,
        "is_primary_key": False,
    }


@pytest.fixture(scope="session")
def schema_column(db_session, schema_column_data):
    """Fixture to create a schema column instance."""
    schema_column = SchemaColumn(**schema_column_data)
    db_session.add(schema_column)
    db_session.commit()
    return schema_column


@pytest.fixture(scope="session")
def file_format_data():
    return {
        "name": "My File Format",
        "format_type": FileFormatType.CSV,
        "compression": CompressionAlgorithm.GZIP,
    }


@pytest.fixture(scope="session")
def file_format(db_session, file_format_data):
    """Fixture to create a file format instance."""
    file_format = FileFormat(**file_format_data)
    db_session.add(file_format)
    db_session.commit()
    return file_format


@pytest.fixture(scope="session")
def data_ingest_data():
    return {
        "name": "My Data Ingest",
        "source_name": "My Source",
        "auto_ingest": True,
        "aws_sns_topic": "my-topic",
        "comment": "This is a comment",
        "error_integration": "This is an error integration",
    }


@pytest.fixture(scope="session")
def data_asset_data(domain, schema):
    return {
        "domain": domain,
        "schema": schema,
        "name": "Sample Data Asset",
        "description": "Sample description",
        "s3_bucket": "sample-bucket",
        "s3_partition_path": "sample/path",
        "instance_default_database": "default-db",
        "instance_default_db_schema": "default-schema",
    }


@pytest.fixture(scope="session")
def data_ingest(db_session, data_ingest_data):
    """Fixture to create a data ingest instance."""
    data_ingest = DataIngest(**data_ingest_data)
    db_session.add(data_ingest)
    db_session.commit()
    return data_ingest


@pytest.fixture(scope="session")
def data_asset(db_session, data_asset_data):
    data_asset = DataAsset(**data_asset_data)
    db_session.add(data_asset)
    db_session.commit()
    return data_asset


@pytest.fixture(scope="session")
def data_asset_instance_data(
    data_asset, file_format, schema, client, data_provider, data_ingest, sftp_source
):
    return {
        "data_asset": data_asset,
        "file_format": file_format,
        "schema": schema,
        "client": client,
        "data_provider": data_provider,
        "data_ingest": data_ingest,
        "source": sftp_source,
        "source_id": sftp_source.id,
        "name": "Sample Data Asset Instance",
        "description": "Sample description",
        "database": "sample_db",
        "db_schema": "sample_schema",
        "materialization_type": "table",
        "tags": ["tag1", "tag2"],
        "stage_name": "dev",
        "one_off": False,
        "enabled": True,
        "schedule_type": ScheduleType.EVENT,
        "schedule_cron": None,
    }


@pytest.fixture(scope="session")
def data_asset_instance(db_session, data_asset_instance_data):
    data_asset_instance = DataAssetInstance(**data_asset_instance_data)
    db_session.add(data_asset_instance)
    db_session.commit()
    return data_asset_instance


@pytest.fixture
def function_data():
    return {
        "name": "Sample Function",
        "description": "Sample function description",
        "code": "SELECT * FROM my_table",
        "code_language": "SQL",
    }


@pytest.fixture
def function(db_session, function_data):
    function = Function(**function_data)
    db_session.add(function)
    db_session.commit()
    return function


@pytest.fixture
def function_argument_data(function):
    return {
        "function": function,
        "name": "arg1",
        "description": "Argument 1",
        "default_value": "default",
        "data_type": "string",
    }


@pytest.fixture
def function_argument(db_session, function_argument_data):
    function_argument = FunctionArgument(**function_argument_data)
    db_session.add(function_argument)
    db_session.commit()
    return function_argument


@pytest.fixture
def function_mapping_data(data_asset_instance, function):
    return {
        "data_asset_instance": data_asset_instance,
        "function": function,
        "argument_value": {"arg1": "value1"},
        "alias_name": "alias",
        "seq_num": 1,
    }


@pytest.fixture
def function_mapping(db_session, function_mapping_data):
    function_mapping = FunctionMapping(**function_mapping_data)
    db_session.add(function_mapping)
    db_session.commit()
    return function_mapping


@pytest.fixture
def pipeline_task_data(data_asset_instance):
    return {
        "data_asset_instance": data_asset_instance,
        "external_id": "test123",
        "service_name": "bifrost",
        "task_type": "DATA_INGEST",
        "state": "QUEUED",
        "extra_info": {"next_begin_mark": "123"},
    }


@pytest.fixture
def pipeline_task(db_session, pipeline_task_data):
    instance = PipelineTask(**pipeline_task_data)
    db_session.add(instance)
    db_session.commit()
    return instance


def test_base_model_id_type():
    # Ensure that the ID column is an Integer
    base_model = BaseModel()
    assert isinstance(base_model.id.type, Integer)


def test_table_name():
    # Ensure that the table name is the lower-cased version of the class name
    base_model = FileFormat()
    assert base_model.__tablename__ == "fileformat"


def test_create_domain(domain, domain_data):
    """Test creating a domain."""
    assert domain.id is not None
    assert domain.name == domain_data["name"]
    assert domain.database == domain_data["database"]
    assert domain.db_schema == domain_data["db_schema"]
    assert domain.created_at is not None
    assert domain.updated_at is not None
    assert domain.deleted_at is None
    assert isinstance(domain.created_at, datetime)


def test_data_provider_creation(data_provider, data_provider_data):
    assert data_provider.id is not None
    assert data_provider.name == data_provider_data["name"]
    assert data_provider.type == data_provider_data["type"]
    assert data_provider.contact_name == data_provider_data["contact_name"]
    assert data_provider.contact_email == data_provider_data["contact_email"]


def test_client_creation(client):
    assert client is not None
    assert client.name == "test_client"
    assert client.is_active


def test_create_sftp_source(sftp_data, sftp_source):
    assert sftp_source.host == sftp_data["host"]
    assert sftp_source.port == sftp_data["port"]
    assert sftp_source.user == sftp_data["user"]
    assert sftp_source.passphrase == sftp_data["passphrase"]
    assert sftp_source.source_path == sftp_data["source_path"]
    assert sftp_source.backup_dir == sftp_data["backup_dir"]


def test_create_schema(schema, schema_data, domain):
    """Test creating a schema."""
    assert schema.id is not None
    assert schema.type == schema_data["type"]


def test_create_schema_column(schema_column, schema_column_data, schema):
    """Test creating a schema column."""
    assert schema_column.id is not None
    assert schema_column.column_number == schema_column_data["column_number"]
    assert schema_column.column_name == schema_column_data["column_name"]
    assert schema_column.tags == schema_column_data["tags"]
    assert schema_column.data_type == schema_column_data["data_type"]
    assert schema_column.is_custom_column == schema_column_data["is_custom_column"]
    assert schema_column.is_nullable == schema_column_data["is_nullable"]
    assert schema_column.is_foreign_key == schema_column_data["is_foreign_key"]
    assert schema_column.is_primary_key == schema_column_data["is_primary_key"]
    assert schema_column.schema == schema


def test_file_format_and_data_ingest(file_format, data_ingest):
    assert file_format.name == "My File Format"
    assert file_format.format_type == FileFormatType.CSV
    assert file_format.compression == CompressionAlgorithm.GZIP
    assert file_format.column_separator == FIELD_DELIMITER
    assert file_format.row_separator == ROW_DELIMITER
    assert file_format.null_string == NULL_IF
    assert not file_format.is_trimmed
    assert file_format.skip_header_lines == DEFAULT_HEADER_LINES
    assert file_format.is_column_mismatch_error_raised
    assert file_format.escape_character is None
    assert file_format.escape_unenclosed_field == ESCAPE_UNENCLOSED_FIELD
    assert file_format.date_format == DEFAULT_DATE_TIMESTAMP_FORMAT
    assert file_format.timestamp_format == DEFAULT_DATE_TIMESTAMP_FORMAT
    assert file_format.is_active
    assert not file_format.is_global
    # add other assertions as needed

    assert data_ingest.name == "My Data Ingest"
    assert data_ingest.source_name == "My Source"
    assert data_ingest.auto_ingest is True
    assert data_ingest.aws_sns_topic == "my-topic"
    assert data_ingest.comment == "This is a comment"
    assert data_ingest.error_integration == "This is an error integration"


def test_data_asset_creation(data_asset, domain, schema):
    assert data_asset.id is not None
    assert data_asset.domain == domain
    assert data_asset.schema == schema
    assert data_asset.name == "Sample Data Asset"
    assert data_asset.description == "Sample description"
    assert data_asset.s3_bucket == "sample-bucket"
    assert data_asset.s3_partition_path == "sample/path"
    assert data_asset.instance_default_database == "default-db"
    assert data_asset.instance_default_db_schema == "default-schema"


def test_create_data_asset_instance(data_asset_instance, data_asset_instance_data):
    assert data_asset_instance.id is not None
    assert (
        data_asset_instance.data_asset.id == data_asset_instance_data["data_asset"].id
    )
    assert (
        data_asset_instance.file_format.id == data_asset_instance_data["file_format"].id
    )
    assert data_asset_instance.schema.id == data_asset_instance_data["schema"].id
    assert (
        data_asset_instance.data_provider.id
        == data_asset_instance_data["data_provider"].id
    )
    assert (
        data_asset_instance.data_ingest.id == data_asset_instance_data["data_ingest"].id
    )
    assert data_asset_instance.source_type == SFTPSource.__name__
    assert data_asset_instance.source_id == data_asset_instance_data["source_id"]
    assert data_asset_instance.name == data_asset_instance_data["name"]
    assert data_asset_instance.description == data_asset_instance_data["description"]
    assert data_asset_instance.database == data_asset_instance_data["database"]
    assert data_asset_instance.db_schema == data_asset_instance_data["db_schema"]
    assert (
        data_asset_instance.materialization_type
        == data_asset_instance_data["materialization_type"]
    )
    assert data_asset_instance.tags == data_asset_instance_data["tags"]
    assert data_asset_instance.stage_name == data_asset_instance_data["stage_name"]


def test_function_creation(function, function_data):
    assert function.id is not None
    assert function.name == function_data["name"]
    assert function.code == function_data["code"]


def test_function_argument_creation(
    function_argument, function_argument_data, function
):
    assert function_argument.id is not None
    assert function_argument.function == function
    assert function_argument.default_value == function_argument_data["default_value"]


def test_function_mapping_creation(
    function_mapping, function_mapping_data, function, data_asset_instance
):
    assert function_mapping.id is not None
    assert function_mapping.function == function
    assert function_mapping.data_asset_instance == data_asset_instance
    assert function_mapping.argument_value == function_mapping_data["argument_value"]
    assert function_mapping.seq_num == function_mapping_data["seq_num"]


def test_pipeline_creation(pipeline_task, pipeline_task_data, data_asset_instance):
    assert pipeline_task.id is not None
    assert pipeline_task.data_asset_instance == data_asset_instance
    assert pipeline_task.state == PipelineTaskState.QUEUED
    assert pipeline_task.status is None
    assert pipeline_task.task_type == PipelineTaskType.DATA_INGEST
    assert pipeline_task.extra_info["next_begin_mark"] == "123"


def test_pipeline_update(pipeline_task, db_session):
    pipeline_task.status = PipelineTaskStatus.SUCCESS
    db_session.add(pipeline_task)
    db_session.commit()

    db_instance = PipelineTask.query.get(pipeline_task.id)
    assert db_instance.status == PipelineTaskStatus.SUCCESS
