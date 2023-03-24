# encoding: utf-8
"""
Blueprint adapter
"""

from flask_smorest import Blueprint


class EnhancedBlueprint(Blueprint):
    def _set_pagination_metadata(self, page_params, result, headers):
        """Add pagination metadata to response"""
        result = {
            "pagination": self._make_pagination_metadata(
                page_params.page, page_params.page_size, page_params.item_count
            ),
            "results": result,
        }
        return result, headers

    def _document_pagination_metadata(self, spec, resp_doc):
        """Document pagination metadata"""
        # This will already taken cared by paginated_schema_factory
        return
