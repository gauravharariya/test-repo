from app import db
from app.common.db_utils import upsert_by_id
from app.models import (
    Domain,
    DataAsset,
    DataProvider,
    DataIngest,
    FileFormat,
    SFTPSource,
    DataAssetInstance,
    Client,
    SchemaColumn,
    Schema,
)


def upsert_schema(data):
    schema_cols = data.pop("columns", [])
    schema = upsert_by_id(Schema, data)
    for col_data in schema_cols:
        col_data["schema"] = schema
        upsert_by_id(SchemaColumn, col_data)

    return schema


def upsert_data_asset(data):
    data["domain"] = upsert_by_id(Domain, data["domain"])
    if data.get("schema"):
        data["schema"] = upsert_schema(data["schema"])
    return upsert_by_id(DataAsset, data)


def upsert_data_asset_instance(data):
    # Insert Data Asset
    data["data_asset"] = upsert_data_asset(data["data_asset"])

    # Upsert Data Asset Instance
    data["client"] = upsert_by_id(Client, data["client"])

    data["data_provider"] = upsert_by_id(DataProvider, data["data_provider"])

    if data.get("file_format"):
        data["file_format"] = upsert_by_id(FileFormat, data["file_format"])

    if data.get("data_ingest"):
        data["data_ingest"] = upsert_by_id(DataIngest, data["data_ingest"])

    if data.get("schema"):
        data["schema"] = upsert_schema(data["schema"])

    # upsert sftp source
    if data.get("source"):
        data["source"] = upsert_by_id(SFTPSource, data["source"])
        data["source_id"] = data["source"].id

    data_asset_instance = upsert_by_id(DataAssetInstance, data)
    db.session.commit()
    return data_asset_instance
