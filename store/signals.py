
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import *

@receiver(pre_save, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    oquantity = 0
    if instance.pk: # check if the instance is being updated
        old_instance = OrderItem.objects.get(pk=instance.pk)
        product = old_instance.product
        oquantity = old_instance.quantity
        product.quantity += old_instance.quantity # add back the old quantity
    product = instance.product
    print("quantity of product and OrderItem before:", product.name, product.quantity, instance.quantity)
    if oquantity > instance.quantity: #
        product.quantity += 1
    elif oquantity < instance.quantity:
        product.quantity -= 1
    product.save()
    print("quantity of product and OrderItem after:", product.name, product.quantity, instance.quantity)