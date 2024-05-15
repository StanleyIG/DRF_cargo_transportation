from django.core.management.base import BaseCommand
from random import randint
from cargoapp.models import Truck, Location
from django.db.utils import IntegrityError
import random

# команды
# python manage.py create_trucks создаст 20 уникальных траков по умолчанию
# python manage.py create_trucks 100 создаст 100 уникальных траков 

class Command(BaseCommand):
    help = 'создать любое колличество рандомных грузовиков'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, default=20, help='количество грузовиков для создания')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        for i in range(count):
            # location = Location.objects.order_by('?').first()
            location = random.choice(Location.objects.all())

            capacity = randint(1, 1000)
            # добавлен цикл, который будет создавать новый объект модели до тех пор, пока 
            # не создасться нужное колличество уникальных траков.
            while True:
                try:
                    truck = Truck(current_location=location, capacity=capacity)
                    truck.save()
                    self.stdout.write(self.style.SUCCESS(f'Грузовик создан {truck.number}'))
                    break
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(f'Ошибка создания грузовика: дубликат номера'))

            