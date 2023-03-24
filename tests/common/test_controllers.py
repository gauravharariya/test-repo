from unittest.mock import MagicMock

from flask_smorest.pagination import PaginationParameters

from app.common.auth import auth_required
from app.common.controllers import BaseMethodView, ListMethodView


def test_base_method_view_auth_required_decorator():
    assert auth_required in BaseMethodView.decorators


def test_list_method_view_get_query_raises_not_implemented():
    lm = ListMethodView()
    try:
        lm.get_query()
    except NotImplementedError:
        pass
    else:
        assert False


def test_list_method_view_apply_order_by_no_ordering():
    lm = ListMethodView()
    query = MagicMock()
    result = lm.apply_order_by(query)
    assert result == query


def test_list_method_view_apply_order_by_list_ordering():
    lm = ListMethodView()
    lm.ordering = ["field1", "field2"]
    query = MagicMock()
    lm.apply_order_by(query)
    query.order_by.assert_any_call("field1")


def test_list_method_view_apply_order_by_single_ordering():
    lm = ListMethodView()
    lm.ordering = "field1"
    query = MagicMock()
    lm.apply_order_by(query)
    query.order_by.assert_called_once_with("field1")


def test_list_method_view_list():
    lm = ListMethodView()
    query = MagicMock()
    lm.get_query = MagicMock(return_value=query)
    lm.apply_order_by = MagicMock(return_value=query)
    lm.ordering = "field1"
    pagination_parameters = PaginationParameters(page=1, page_size=10)
    query.count = MagicMock(return_value=100)
    res = lm.list(pagination_parameters)
    lm.apply_order_by.assert_called_once_with(query)
    lm.get_query.assert_called_once()
    query.count.assert_called_once()
    assert pagination_parameters.item_count == 100
    assert res == query.paginate.return_value.items


def test_list_method_view_list_no_ordering():
    lm = ListMethodView()
    query = MagicMock()
    lm.get_query = MagicMock(return_value=query)
    lm.ordering = None
    pagination_parameters = PaginationParameters(page=1, page_size=10)
    res = lm.list(pagination_parameters)
    lm.get_query.assert_called_once()
    assert pagination_parameters.item_count == query.count.return_value
    assert res == query.paginate.return_value.items
