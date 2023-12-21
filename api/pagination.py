from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Default API response pagination"""

    page_size = 1000
    page_size_query_param = "per_page"
    max_page_size = 1000
