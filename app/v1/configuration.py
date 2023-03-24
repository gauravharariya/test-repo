import json

from flask import request, abort
from flask_smorest.pagination import PaginationParameters

from app.common.blueprint import EnhancedBlueprint
from app.common.controllers import ListMethodView, BaseMethodView
from app.common.schema import paginated_schema_factory
from app.models import (
    Domain,
    DataProvider,
    Client,
    DataAsset,
    DataAssetInstance,
    FunctionMapping,
)
from app.schema import (
    domains_schema,
    domain_schema,
    data_providers_schema,
    data_provider_schema,
    client_schema,
    clients_schema,
    data_assets_schema,
    data_asset_schema,
    data_asset_instance_schema,
    data_asset_instances_schema,
    function_mappings_schema,
    sftp_source_schema,
    DataAssetInstanceUpsertRequestSchema,
)
from app.service import upsert_data_asset_instance

blp = EnhancedBlueprint("v1", __name__)


@blp.route("/")
def default():
    return "Welcome to the frickin' Galactic Core."


@blp.route("/domains/", tags=["domain"])
class DomainList(ListMethodView):
    ordering = Domain.created_at.desc()

    def get_query(self):
        return Domain.query

    @blp.response(200, schema=paginated_schema_factory(domains_schema))
    @blp.paginate()
    def get(self, pagination_parameters: PaginationParameters):
        """List Domains"""
        return self.list(pagination_parameters)


@blp.route("/domains/<int:domain_id>", tags=["domain"])
class DomainGet(BaseMethodView):
    @blp.response(200, domain_schema)
    def get(self, domain_id):
        """Get Domain by Id"""
        return Domain.query.get_or_404(domain_id)


@blp.route("/data-providers/", tags=["data-provider"])
class DataProviderList(ListMethodView):
    ordering = DataProvider.created_at.desc()

    def get_query(self):
        return DataProvider.query

    @blp.response(200, schema=paginated_schema_factory(data_providers_schema))
    @blp.paginate()
    def get(self, pagination_parameters: PaginationParameters):
        """List data providers"""
        return self.list(pagination_parameters)


@blp.route("/data-providers/<int:data_provider_id>", tags=["data-provider"])
class DataProviderGet(BaseMethodView):
    @blp.response(200, data_provider_schema)
    def get(self, data_provider_id):
        """Get Data Provider by Id"""
        return DataProvider.query.get_or_404(data_provider_id)


@blp.route("/clients/", tags=["client"])
class ClientList(ListMethodView):
    ordering = Client.created_at.desc()

    def get_query(self):
        return Client.query

    @blp.response(200, schema=paginated_schema_factory(clients_schema))
    @blp.paginate()
    def get(self, pagination_parameters: PaginationParameters):
        """List clients"""
        return self.list(pagination_parameters)


@blp.route("/clients/<int:client_id>", tags=["client"])
class ClientGet(BaseMethodView):
    @blp.response(200, client_schema)
    def get(self, client_id):
        """Get Client by Id"""
        return Client.query.get_or_404(client_id)


@blp.route("/data-assets/", tags=["data-asset"])
class DataAssetList(ListMethodView):
    ordering = DataAsset.created_at.desc()

    def get_query(self):
        return DataAsset.query

    @blp.response(200, schema=paginated_schema_factory(data_assets_schema))
    @blp.paginate()
    def get(self, pagination_parameters: PaginationParameters):
        """List Data Assets"""
        return self.list(pagination_parameters)


@blp.route("/data-assets/<int:data_asset_id>", tags=["data-asset"])
class DataAssetGet(BaseMethodView):
    @blp.response(200, data_asset_schema)
    def get(self, data_asset_id):
        """Get Data Asset by Id"""
        return DataAsset.query.get_or_404(data_asset_id)


@blp.route("/data-assets/instances/", tags=["data-asset"])
class DataAssetInstanceList(ListMethodView):
    ordering = DataAssetInstance.created_at.desc()

    def get_query(self):
        return DataAssetInstance.query

    @blp.response(200, schema=paginated_schema_factory(data_asset_instances_schema))
    @blp.paginate()
    def get(self, pagination_parameters: PaginationParameters):
        """List Data Asset Instances"""
        return self.list(pagination_parameters)


@blp.route("/data-assets/instances/<int:data_asset_instance_id>", tags=["data-asset"])
class DataAssetInstanceGet(BaseMethodView):
    @blp.response(200, data_asset_instance_schema)
    def get(self, data_asset_instance_id):
        """Get Data Asset Instance by id"""
        return DataAssetInstance.query.get_or_404(data_asset_instance_id)


@blp.route(
    "/data-assets/instances/<int:data_asset_instance_id>/source", tags=["data-asset"]
)
class DataAssetInstanceSourceGet(BaseMethodView):
    # TODO add enhancement to handle all source serialization
    @blp.response(200, sftp_source_schema)
    def get(self, data_asset_instance_id):
        """Get Data Asset Instance by id"""
        data_asset_instance = DataAssetInstance.query.get_or_404(data_asset_instance_id)
        return data_asset_instance.source


# Function mapping routes
@blp.route(
    "/data-assets/instances/<int:data_asset_instance_id>/functions", tags=["data-asset"]
)
class DataAssetInstanceFunctionMappingList(ListMethodView):
    ordering = FunctionMapping.seq_num.asc()

    def get_query(self):
        # apply data asset instance id filter
        data_asset_instance_id = request.view_args.get("data_asset_instance_id")
        return FunctionMapping.query.filter(
            DataAssetInstance.id == data_asset_instance_id  # noqa
        )

    @blp.response(200, schema=paginated_schema_factory(function_mappings_schema))
    @blp.paginate()
    def get(self, data_asset_instance_id, pagination_parameters: PaginationParameters):
        """List Data Asset Instance Function Mappings Ordered By Seq Num"""
        # raise error if it does not exist
        DataAssetInstance.query.get_or_404(data_asset_instance_id)
        return self.list(pagination_parameters)


@blp.route("/data-assets/instances/upsert", tags=["data-asset"])
class DataAssetInstanceUpsert(BaseMethodView):
    @blp.arguments(DataAssetInstanceUpsertRequestSchema, location="files")
    @blp.response(200, data_asset_instance_schema)
    def post(self, data):
        file = data["file"]
        try:
            data = json.load(file)
            return upsert_data_asset_instance(data)
        except UnicodeDecodeError:
            return abort(400, "Please provide valid json file")
