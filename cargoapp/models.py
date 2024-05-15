from django.db import models
import random
import string

"""
- БД по умолчанию должна быть заполнена 20 машинами.
- Груз обязательно должен содержать следующие характеристики:
    - локация pick-up;
    - локация delivery;
    - вес (1-1000);
    - описание.
- Машина обязательно должна в себя включать следующие характеристики:
    - уникальный номер (цифра от 1000 до 9999 + случайная заглавная буква английского алфавита в конце, пример: "1234A", "2534B", "9999Z")
    - текущая локация;
    - грузоподъемность (1-1000).
- Локация должна содержать в себе следующие характеристики:
    - город;
    - штат;
    - почтовый индекс (zip);
    - широта;
    - долгота.
"""
class Location(models.Model):
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    zip = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"{self.city}, {self.region} {self.zip}"


class Truck(models.Model):
    number = models.CharField(max_length=5, unique=True)
    #current_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    current_location = models.CharField(max_length=250, null=False)
    capacity = models.IntegerField()


    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"{random.randint(1000, 9999)}{random.choice(string.ascii_uppercase)}"
        super(Truck, self).save(*args, **kwargs)

    def __str__(self):
        return self.number


class Cargo(models.Model):
    pick_up = models.CharField(max_length=250, null=False)
    delivery = models.CharField(max_length=250, null=False)
    weight = models.DecimalField(max_digits=4, decimal_places=1)
    description = models.CharField(max_length=250)

    def pick_up_location(self):
        return Location.objects.get(zip=self.pick_up)

    def delivery_location(self):
        return Location.objects.get(zip=self.delivery)

    def __str__(self):
        return f"Cargo ({self.weight} kg): {self.pick_up} -> {self.delivery}"



#pick_up = models.ForeignKey(Location, related_name='pick_up_locations', on_delete=models.CASCADE)
#delivery = models.ForeignKey(Location, related_name='delivery_locations', on_delete=models.CASCADE)