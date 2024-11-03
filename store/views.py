from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend       
#from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly
#from rest_framework.pagination import PageNumberPagination
#from rest_framework.decorators import api_view
#from rest_framework.views import APIView
#from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
#from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import CartItem, Customer, Order, Product, Collection, OrderItem, Review, Cart
from .serializers import AddCartItemSerializer, CartItemSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, UpdateCartItemSerializer, UpdateOrderSerializer
from .filters import ProductFilter
from .paginations import DefaultPagination 
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewCustomerHistoryPermission

# Create your views here.


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count = Count('product') ).all() 
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]


    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id = kwargs['pk']).count() > 0:   #we use this b/c not to retrieve the collection from the db again b/c we've already retrieved it in the destroy method in the ModelViewSet class
            return Response({'error': 'The collection can not be deleted because it includes one or more products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

    






class ProductViewSet(ModelViewSet):   #u can also use ReadOnlyViewSet
    queryset = Product.objects.all()
    serializer_class  = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter 
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]   #only 'get' operation is available for the authenticated or anonymous users but all the operations are available for the admin user
    search_fields = ['title', 'description']    #text based fields are used for searching
    Ordering_fields = ['unit_price']
    #filterset_fields = ['collection_id', 'inventory']

    # def get_queryset(self):    #this below is a filtering logic
    #     queryset = Product.objects.all()

    #     collection_id = self.request.query_params.get('collection_id')    #to check if there is a query string parameter named 'collectio_id'
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id = self.request.query_params['collection_id'])

    #     return queryset 



    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
            if OrderItem.objects.filter(product_id = kwargs['pk']).count() > 0:   #we use this b/c not to retrieve the product from the db again
                return Response({'error': 'The product can not be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
            return super().destroy(request, *args, **kwargs)

            #kwargs(keyword arguments) is a dictionary that contains our url parameters(products/product_id)




  




class ReviewViewSet(ModelViewSet):
     #queryset = Review.objects.filter(product_id = )
     serializer_class = ReviewSerializer

     def get_queryset(self):
         return Review.objects.filter(product_id = self.kwargs['product_pk'])  #based on this logic, its hard to figure out the basename

     def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}       #passing data in a context object to ReviewSerializer


    #here in this class we have access to the 'product_pk' url parameter of the url: 'http://127.0.0.1:8000/store/products/product_pk/reviews/pk' using kwargs... and using the context object, we can pass it to the serializer





#possible operations are create cart, rertriev cart, delete cart
class CartViewSet(GenericViewSet, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin):   #ListModelMixin is not allowed b/c it is not wanted for anonymous users to see the list of carts and get their ids
    queryset = Cart.objects.prefetch_related('items__product').all()  #preloading a cart with its items and then preloading each items with their product they reference
    serializer_class = CartSerializer








#all operations are possible here
class CartItemViewSet(ModelViewSet):
    #serializer_class = CartItemSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']


    def get_queryset(self):
        return CartItem.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')
    
    def get_serializer_class(self):  #the serializer class is set dynamically based on request method
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}     #passing data in a context object to AddCartItemSerializer







class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    #DjangoModelPermissions class needs user authentication first

    #using DjangoModelPermissions, we apply the normal model permissions to our normal endpoint(custromers/) so that only a user with those model permissions can access the endpoint

    # def get_permissions(self):                                                                                                          #to apply permissions on specific operations like 'GET', 'POST'
    #     if self.request.method == 'GET':
    #         return [AllowAny()]                                                                                                         #return list of permission objects not class
    #     return [IsAuthenticated()]


    @action(detail=False, methods=['GET', 'PUT'], permission_classes = [IsAuthenticated])     #the 'me/' action is not available on the detail view(store/customers/1/), it is only available in the list view(store/customers/)
    def me(self, request):                                                                                                       #this is a custom 'action' like product_list and product_detail
        customer = Customer.objects.get(user_id = request.user.id)     

        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data = request.data)    #to deserialize
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
    

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])                                                           #this action is available on the detail view(store/customers/1)
    def history(self, request, pk):
        return Response('hi')
    #first create the custom model permission(like view histroy) then create the endpoint(for viewing a particular customer's histroy) and then apply the custom model permission to the endpoint








class OrderViewSet(ModelViewSet):
    #queryset = Order.objects.all()
    #serializer_class = OrderSerializer
    #permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']    #available methods at this endpoint


    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    


    def create(self, request, *args, **kwargs):   #in the createModelMixin        #create resembles 'POST' method in the old way
        serializer = CreateOrderSerializer( data = request.data, context = {'user_id' : self.request.user.id} )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()    #here when we call the save method of the serializer, the validated datas(cart_id in our eg) are also passed to the save method of the serializer
        serializer = OrderSerializer(order)
        return Response(serializer.data)



    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id = self.request.user.id)   #else
        return Order.objects.filter(customer_id = customer_id)


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    
    # def get_serializer_context(self):     #this doesn't work b/c we overriden the create method and so we have to pass the context object manually to the serializer
    #     return {'user_id' : self.request.user.id}



    #(customer, created) = Customer.objects.get(user_id = request.user.id)     #get_or_create returns a tuple   #created is a boolean value
    #get_or_create method defies the command query principle








#the authentication middleware looks if there is any info about a user in the request obj and if there is, it uses it to retrieve a user from db and sets it to the user attribute of the request object otherwise the user attrib in the request obj is set to an instance of anonymous user




#########################################################################################################################################################






                                        #class based view using generic view(concrete class) to make it 'concise' for product endpoint    --before ProductViewSet


# class ProductList(ListCreateAPIView):

#     queryset = Product.objects.all()
#     serializer_class  = ProductSerializer

#     # def get_queryset(self):
#     #     return Product.objects.all()
#     # def get_serializer_class(self):
#     #     return ProductSerializer
#     def get_serializer_context(self):
#         return {'request': self.request}   #request from the current object

    

# class ProductDetail(RetrieveUpdateDestroyAPIView):

#     queryset = Product.objects.all()     #in this case get the whole resource here first
#     serializer_class = ProductSerializer
#     #lookup_field = 'id'
    
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitem_set.count() > 0:
#             Response({'error': 'The product can not be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
  








                                        #class based view using generic view(concrete class) to make it 'concise' for collection endpoint


# class CollectionList(ListCreateAPIView):

#     queryset = Collection.objects.annotate(products_count = Count('product') ).all()    # product is instead of 'product_set'
#     serializer_class = CollectionSerializer

#     # def get_queryset(self):
#     #     return Collection.objects.annotate(products_count = Count('product') ).all()    # product is instead of 'product_set'
    
#     # def get_serializer_class(self):
#     #     return CollectionSerializer
    


# class CollectionDetail(RetrieveUpdateDestroyAPIView):

#     queryset =  Collection.objects.annotate(products_count = Count('product') ).all()         #in this case get the whole resource here first
#     serializer_class = CollectionSerializer
    
#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection, pk=pk)        
#         if collection.product_set.count() > 0:
#             return Response({'error': 'The collection can not be deleted because it includes one or more products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)











                                # basic 'class based view' for product endpoint and this one is to make it 'cleaner'


# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(queryset, many=True, context={'request': request})    #to serialize
#         return Response(serializer.data)
    
#     def post(self, request):                                                                                              @@@
#         serializer = ProductSerializer(data = request.data)    #to deserialize
#         serializer.is_valid(raise_exception=True)
#         print(serializer.validated_data)
#         serializer.save()     #the validated data is passed to the save method of a serializer
#         return Response(serializer.data, status=status.HTTP_201_CREATED)    #and the save method returns the created or updated instance w/h in turn get serialized and returned to the client in this line

   
    
# class ProductDetail(APIView):
#     def get(self, request, id):
#         product = get_object_or_404(Product, pk=id) 
#         serializer = ProductSerializer(product)  #to serialize
#         return Response(serializer.data)
    
#     def put(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data = request.data)    #to deserialize
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data) 
    
#     def delete(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         if product.orderitem_set.count() > 0:
#             Response({'error': 'The product can not be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
  



                                
                                
                                
                                
                                
                                
                                
                                # basic 'class based view' for collectiondetail endpoint 


# class CollectionDetail(APIview):
    
#     def get(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count = Count('product') ), pk=pk)      #Collection.objects.get(pk=pk)   #Collection.objects.annotate(products_count = Count('product_set')).objects.get(pk=pk)
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count = Count('product') ), pk=pk)      #Collection.objects.get(pk=pk)   #Collection.objects.annotate(products_count = Count('product_set')).objects.get(pk=pk)
#         serializer = CollectionSerializer(collection, data = request.data)    #to deserialize
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count = Count('product') ), pk=pk)      #Collection.objects.get(pk=pk)   #Collection.objects.annotate(products_count = Count('product_set')).objects.get(pk=pk)
#         if collection.product_set.count() > 0:
#             return Response({'error': 'The collection can not be deleted because it includes one or more products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)






    























                                                # function based view for a product endpoint

# @api_view(['GET', 'POST'])
# def product_list(request):
#     if request.method == 'GET':
#         queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(queryset, many=True, context={'request': request})    #to serialize
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data = request.data)    #to deserialize
#         serializer.is_valid(raise_exception=True)
#         print(serializer.validated_data)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#         # else:
#         #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
        





# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail(request, id):
#     product = get_object_or_404(Product, pk=id)    #Product.objects.get(pk=id)
#     if request.method == 'GET':
#         serializer = ProductSerializer(product)  #to serialize
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data = request.data)    #to deserialize
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if product.orderitem_set.count() > 0:
#             Response({'error': 'The product can not be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)





