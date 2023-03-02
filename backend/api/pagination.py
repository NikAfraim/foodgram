from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    """Кастомный пагинатор"""

    page_size_query_param = 'limit'
