from rest_framework import pagination


class MyCustomPagination(pagination.PageNumberPagination):
    """Кастомный пагинатор"""

    page_size_query_param = 'limit'