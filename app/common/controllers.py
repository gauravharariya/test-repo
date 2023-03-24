from typing import List, Union, Iterable, Any

from flask.views import MethodView
from flask_smorest.pagination import PaginationParameters
from six import string_types

from app.common.auth import auth_required


class BaseMethodView(MethodView):
    """Reusable components added to BaseMethodView"""

    decorators = [auth_required]


class ListMethodView(BaseMethodView):
    """Reusable List Method View"""

    ordering: Union[List, Any] = None

    def get_query(self):
        raise NotImplementedError

    def list(self, pagination_parameters: PaginationParameters):
        """List View"""
        query = self.apply_order_by(self.get_query())
        pagination_parameters.item_count = query.count()
        res = query.paginate(
            page=pagination_parameters.page,
            per_page=pagination_parameters.page_size,
        )
        return res.items

    def apply_order_by(self, query):
        if self.ordering is not None:
            if isinstance(self.ordering, Iterable) and not isinstance(
                self.ordering, string_types
            ):
                for order_field in self.ordering:
                    query = query.order_by(order_field)
            else:
                query = query.order_by(self.ordering)

        return query
