from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):   #this is custom pagination class
    page_size = 10