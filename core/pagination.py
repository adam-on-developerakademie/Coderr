from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Shared pagination class: default 6, max 6, configurable via ?page_size=."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 6
