from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Стандартный пагинатор с определением c
    возможностью вывода определенного количества страниц.
    """

    page_size_query_param = "limit"
