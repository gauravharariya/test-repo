import marshmallow as ma

from app.common.schema import paginated_schema_factory


def test_paginated_schema_factory():
    class TestSchema(ma.Schema):
        id = ma.fields.Int()
        name = ma.fields.String()

        class Meta:
            ordered = True

    schema = paginated_schema_factory(TestSchema())()
    assert isinstance(schema, ma.Schema)
    assert "pagination" in schema.fields
    assert "results" in schema.fields
    assert isinstance(schema.fields["pagination"], ma.fields.Nested)
    assert isinstance(schema.fields["results"], ma.fields.Nested)
