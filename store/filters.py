from django_filters.rest_framework import FilterSet
from .models import Product


#this is for custom filtering of the unit_price case using django-filter
class ProductFilter(FilterSet):  #this is a custom filter class
    class Meta:
        model = Product
        fields = {    #specify the fields and how filtering is done on them
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }
