from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Truck, Location
from .serializers import TruckSerializer, LocationModelSerializer
from django.core.cache import cache

@receiver(post_save, sender=Truck)
def update_truck_cache(sender, instance, **kwargs):
    cache.set(f'truck_{instance.number}', TruckSerializer(instance).data)

@receiver(post_delete, sender=Truck)
def delete_truck_cache(sender, instance, **kwargs):
    cache.delete(f'truck_{instance.number}')


@receiver(post_save, sender=Location)
def update_location_cache(sender, instance, **kwargs):
    cache.set(f'location_{instance.zip}', LocationModelSerializer(instance).data)

@receiver(post_delete, sender=Location)
def delete_location_cache(sender, instance, **kwargs):
    cache.delete(f'location_{instance.zip}')
