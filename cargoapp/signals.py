from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Truck, Location
from .serializers import TruckModelSerializer, LocationModelSerializer
from django.core.cache import cache


@receiver(post_save, sender=Truck)
def update_truck_cache(sender, instance, **kwargs):
    print('сигнал сработал')
    cache.set(f'truck', True)
    print(cache.get(f'truck'))

# @receiver(post_save, sender=Truck)
# def update_truck_cache(sender, instance, *kwargs):
#     if kwargs.get('created', False):
#         # Событие создания, пропускаем
#         return
#     cache.set(f'truck_{instance.number}', True)


@receiver(post_delete, sender=Truck)
def delete_truck_cache(sender, instance, **kwargs):
    print('сигнал удаления')
    cache.clear()


@receiver(post_save, sender=Location)
def update_location_cache(sender, instance, **kwargs):
    cache.set(f'location', True)


@receiver(post_delete, sender=Location)
def delete_location_cache(sender, instance, **kwargs):
    print('сигнал удаления')
    cache.clear()
