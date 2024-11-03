from django.dispatch import receiver
from store.signals import order_created     #here the store_custom app is being dependent on the store(its okay but the other way around is not okay)


#this receiver receives and handles an order_created signal that is sent from the Order class through its CreateOrderSerializer
@receiver(order_created)
def on_order_created(sender, **kwargs):
    print(kwargs['order'])




#when we receive a custom signal, we don't need to specify the sender class as an argument in the receiver decorator otherwise we don't get the expected result