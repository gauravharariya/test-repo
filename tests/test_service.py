from app.constants import FileFormatType, SchemaType
from app.models import (
    DataAssetInstance,
)
from app.service import upsert_data_asset_instance


def test_upsert_data_asset_instance(db_session):
    # Create test data
    domain_data = {"name": "claims_110", "database": "CURATED", "db_schema": "test"}

    schema_data = {
        "type": SchemaType.ASSET,
        "columns": [
            {"column_number": 1, "column_name": "col1", "data_type": "string"},
            {"column_number": 2, "column_name": "col2", "data_type": "integer"},
        ],
    }

    data_asset_data = {
        "name": "test_asset",
        "domain": domain_data,
        "schema": schema_data,
        "s3_bucket": "test",
        "s3_partition_path": "test",
        "instance_default_database": "test",
        "instance_default_db_schema": "test",
    }

    client_data = {"name": "test_client"}

    data_provider_data = {"name": "test_provider"}

    file_format_data = {"name": "test_file_format", "format_type": FileFormatType.CSV}

    data_ingest_data = {"name": "test_ingest", "source_name": "test"}
    source_data = {
        "host": "localhost",
        "port": 22,
        "user": "root",
        "passphrase": "Test@123",
        "source_path": "/heath_plan",
    }

    data_asset_instance_data = {
        "data_asset": data_asset_data,
        "client": client_data,
        "data_provider": data_provider_data,
        "file_format": file_format_data,
        "data_ingest": data_ingest_data,
        "schema": schema_data,
        "source": source_data,
        "name": "braze_cargo_health_plan_quality",
        "materialization_type": "table",
        "tags": ["weekday1", "weekday2"],
        "stage_name": "BRAZE_CARGO_HEALTH_PLAN_QUALITY_STAGE",
        "schedule_type": "CRON",
        "schedule_cron": "*/5 * * * *",
    }

    # Upsert Data Asset Instance
    data_asset_instance = upsert_data_asset_instance(data_asset_instance_data)

    # Verify that the object is created or updated
    assert (
        db_session.query(DataAssetInstance).filter_by(id=data_asset_instance.id).one()
        is not None
    )
