from django.core.management.base import BaseCommand
from random import randint
from cargoapp.models import Cargo, Truck, Location
from django.db.utils import IntegrityError
import random

products = [
    "Телевизор",
    "Холодильник",
    "Стиральная машина",
    "Сушильная машина",
    "Посудомоечная машина",
    "Плита",
    "Микроволновая печь",
    "Кофемашина",
    "Тостер",
    "Соковыжималка",
    "Блендер",
    "Пищевой процессор",
    "Фритюрница",
    "Вафельница",
    "Бутербродница",
    "Гриль",
    "Пароварка",
    "Мультиварка",
    "Воздухоочиститель",
    "Осушитель воздуха",
    "Увлажнитель воздуха",
    "Робот-пылесос",
    "Умная колонка",
    "Умный замок",
    "Фитнес-трекер",
    "Смартфон",
    "Планшет",
    "Ноутбук",
    "Настольный компьютер",
    "Игровая консоль"
]




# команды
# python manage.py create_cargo создаст 30 уникальных грузов
class Command(BaseCommand):
    help = 'создать любое колличество рандомных грузовиков'

    def add_arguments(self, parser):
        parser.add_argument("-n", "--number", dest="number", type=int, default=30, help="Количество создаваемых грузов")

    def handle(self, *args, **kwargs):
        for i in range(len(products)):
            # location = Location.objects.order_by('?').first()
            pick_up = random.choice(Location.objects.all())
            delivery = random.choice(Location.objects.all())
            while True:
                try:
                    cargo = Cargo(pick_up=pick_up, delivery=delivery, 
                                  weight=randint(100, 999), description=products[i])
                    cargo.save()
                    self.stdout.write(self.style.SUCCESS(f'Груз создан {cargo.description}'))
                    break
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(f'Ошибка создания груза'))

            