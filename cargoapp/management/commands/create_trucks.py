from django.core.management.base import BaseCommand
from random import randint
from cargoapp.models import Truck, Location


class Command(BaseCommand):
    help = 'создание 20-ти рандомных грузовиков'

    def handle(self, *args, **kwargs):
        for i in range(20):
            location = Location.objects.order_by('?').first()
            capacity = randint(1, 1000)
            truck = Truck(current_location=location, capacity=capacity)
            truck.save()
            self.stdout.write(self.style.SUCCESS(f'Грузовик создан{truck.number}'))