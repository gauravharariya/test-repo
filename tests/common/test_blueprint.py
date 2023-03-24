from collections import OrderedDict

from flask_smorest.pagination import PaginationParameters

from app.common.blueprint import EnhancedBlueprint


def test_set_pagination_metadata():
    blueprint = EnhancedBlueprint("test", "test", url_prefix="/test")
    page_params = PaginationParameters(page=1, page_size=10)
    page_params.item_count = 20
    result = [{"id": 1, "name": "Test 1"}, {"id": 2, "name": "Test 2"}]
    headers = {"X-Total-Count": 20}
    expected_result = {
        "pagination": OrderedDict(
            [
                ("total", 20),
                ("total_pages", 2),
                ("first_page", 1),
                ("last_page", 2),
                ("page", 1),
                ("next_page", 2),
            ]
        ),
        "results": result,
    }
    assert blueprint._set_pagination_metadata(page_params, result, headers) == (
        expected_result,
        headers,
    )


def test_document_pagination_metadata():
    blueprint = EnhancedBlueprint("test", "test", url_prefix="/test")
    spec = {
        "components": {
            "schemas": {
                "TestSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                }
            }
        }
    }
    resp_doc = {
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/TestSchema"}}
        }
    }
    expected_result = resp_doc.copy()
    blueprint._document_pagination_metadata(spec, resp_doc)
    assert resp_doc == expected_result
