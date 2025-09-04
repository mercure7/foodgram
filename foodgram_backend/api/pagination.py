from rest_framework import pagination

from constants import DEFAULT_PAGE_SIZE_PAGINATOR


class PageLimitPagination(pagination.PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE_PAGINATOR
