from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from store.models import Customer


#here we are receiving and handling a signal that is sent or fired from the User class(the custom user) through its serializer(specifically the UserCreateSerializer since it is a post save signal w/h is a signal sent after a user is created)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)              #post_save is the signal we are receiving                                                                          #this reciever listens to the post_save signal of the user model
def create_customer_for_new_user(sender, **kwargs):     #signal handler method
    if kwargs['created']:
        Customer.objects.create(user = kwargs['instance'])




#sender is the class that sends or fires the signal(through its serializer actually)
#sender is a class