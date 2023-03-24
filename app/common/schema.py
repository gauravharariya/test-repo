import marshmallow as ma
from flask_smorest.pagination import PaginationMetadataSchema


def paginated_schema_factory(schema: ma.Schema):
    """Generate a schema with pagination"""
    return ma.Schema.from_dict(
        {
            "pagination": ma.fields.Nested(PaginationMetadataSchema()),
            "results": ma.fields.Nested(schema),
        },
        name=f"{schema.Meta.model.__name__}List"
        if hasattr(schema.Meta, "model")
        else f"{schema.__class__.__name__}List",
    )
