from django.urls import path, include
from . import views
#from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers

from pprint import pprint

# URLConf

#register or create a route(normal, endpoint or nested route) for a normal or nested resource


router = routers.DefaultRouter()   #parent router
router.register('products', views.ProductViewSet, basename='products')    #registering our viewsets and resources to the router
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

# router.urls - for generating the name of url patterns  and to see the generated urlpatterns, use 'pprint(router.urls)'
# here our url has 1 parameter: /products/{pk}



products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')    #child router      
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
# basename is a prefix for generating the name of url patterns... To see that in action, use: 'pprint(products_router.urls)'
# /products/{product_pk}/reviews/{pk}
# here our url has 2 paramers: product_pk and pk


carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')




urlpatterns = [
    path('', include(router.urls)),       #'include' to import routes from somewhere else
    path('', include(products_router.urls)),
    path('', include(carts_router.urls))
    #...other url patterns for specific purposes

]

#urlpatterns = router.urls + products_router.urls












# urlpatterns = [
#     # path('products/', views.ProductList.as_view()),
#     # path('products/<int:id>/', views.ProductDetail.as_view()),
#     # path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection-detail')
# ]


















