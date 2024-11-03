from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import CartItem, OrderItem, Product, Collection, Review, Cart, Customer, Order
from .signals import order_created









class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255) 
    
    products_count = serializers.IntegerField(read_only = True)



    # The product count can also be done like this 
    # products_count = serializers.SerializerMethodField(method_name='count_product')

    # def count_product(self, collection: Collection):
    #     return collection.product_set.count()













class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'inventory', 'unit_price', 'price_with_tax', 'collection']
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    #price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset = Collection.objects.all(),
    #     view_name = 'collection-detail' #used to generate the hyperline..it is the name of the mapping
    # )

    
    # collection = serializers.PrimaryKeyRelatedField(
    #     queryset = collection.objects.all()
    # )


    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.3)
    


    #uses djangoORM   and below is used when deserialize and the methods are defined in ModelSerializer class

    # def create(self, validated_data):   for creating a product
    #     product = Product(**validated_data)   #unpack
    #     product.save()
    #     return product


    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance
    
    










class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']




    def create(self, validated_data):   #override for creating a review
        product_id = self.context['product_id']    #accessing the context object data sent from the ReviewViewSet
        return Review.objects.create(product_id = product_id, **validated_data)
        
        #in the serializers, we don't have access to url parameters











class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


        

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cartitem: CartItem):
        return cartitem.quantity * cartitem.product.unit_price
    






class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
    
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    





class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    product_id = serializers.IntegerField()


    #custom serializer validation for prooduct_id (happens when deserializing, serializer.is_valid() )
    def validate_product_id (self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given id in the db')
        return value    #this value is returned to the validated data


    def save(self, **kwargs):    #the save methods lets us able to do both create and update

        product_id = self.validated_data['product_id']     
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']

        try:
            cart_item = CartItem.objects.get(cart_id = cart_id, product_id = product_id)
            cart_item.quantity += quantity   #update
            self.instance = cart_item.save()  #assign it to self.instance to match with the default implementation of save method(check it in ModelSerializer)

        except CartItem.DoesNotExist:
            self.instance =  CartItem.objects.create(cart_id = cart_id, **self.validated_data)    #create

        return self.instance
        #the create and update methods are in the save method implementation and the creation and updation to the db is done in their implementation and then they return a product w/h is created or updated and that product is set to the self.instance of the save method





class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']










class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

    #user_id = serializers.IntegerField(read_only = True)

    #when creating a profile the user_id is dynamically set at run time(registration idea...calling the backend 2 times)







class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price' ]

    product = SimpleProductSerializer()





class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']

    items = OrderItemSerializer(many=True)






#inside a serializer, we don't have access to a request object(self.request) so we get it using a context object from the ModelViewSet
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()


    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id = cart_id).exists():
            raise serializers.ValidationError('no cart with the given id is in the db')
        # if CartItem.objects.filter(cart_id = cart_id).count() == 0:
        #     raise serializers.ValidationError('the cart does not have items')
        return cart_id       #this returned data is gonna be passed to the 'save' method as validated_data
        



    def save(self, **kwargs):
        # print(self.validated_data)
        # print(self.context['user_id'])

        with transaction.atomic():     #we put it in a transaction b/c we've got three operations like creating an order in this 'save' function

            customer = Customer.objects.get(user_id = self.context['user_id'])
            order = Order.objects.create(customer = customer)     #here to just create an order without its items

            
            cart_items = CartItem.objects.select_related('product').filter(cart_id = self.validated_data['cart_id'])   #returns queryset

            order_items = [ OrderItem(    #converting cart items to orderitems storing them in a list
                order = order,
                product = item.product,
                quantity = item.quantity,
                unit_price = item.product.unit_price
            ) for item in cart_items ]    #to iterate over and evaluate      #this is list comprehension


            OrderItem.objects.bulk_create(order_items)    #save the orderitems to db

            Cart.objects.filter(id = self.validated_data['cart_id']).delete()   #to delete the cart

            order_created.send_robust(self.__class__, order=order)     #this is to fire the 'order_created' signal              # self.__class__ is the class of the current object(w/h is the class of the current serializer w/h is Order)         # order=order is the actual order created(w/h is one of the kwargs used in the receivers)


            return order  #returning the order object to be used in the viewset 'create' method

            #the idea is first we get a cart and we grap its cart items and then convert them to order items and save the order items to the order item table and then delete the cart



class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']