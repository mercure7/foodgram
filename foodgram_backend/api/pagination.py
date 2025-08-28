from rest_framework import pagination
from rest_framework.response import Response





class PageLimitPagination(pagination.PageNumberPagination):
    # Кастомные имена параметров
    page_query_param = 'page'      # ?page=1
    page_size_query_param = 'limit' # ?limit=10
    
    # Значения по умолчанию
    page_size = 6
    # max_page_size = 100
    
    # def get_paginated_response(self, data):
    #     return Response({
    #         'pagination': {
    #             'count': self.page.paginator.count,
    #             'next': self.page.next_page_number() if self.page.has_next() else None,
    #             'previous': self.page.previous_page_number() if self.page.has_previous() else None,
    #         },
    #         'results': data
    #     })