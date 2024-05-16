from django.db import IntegrityError
from django.forms import ValidationError
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, CharField, Serializer, IntegerField, StringRelatedField
from rest_framework import serializers
from .models import Location, Truck, Cargo



class LocationModelSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'



# class TruckModelSerializer(ModelSerializer):
#     class Meta:
#         model = Truck
#         fields = '__all__'
class TruckSerializer(Serializer):
    id = IntegerField(read_only=True)
    number = CharField(max_length=10)
    current_location = CharField(max_length=250)
    capacity = IntegerField()

    def update(self, instance, validated_data):
        try:
            # Получаю объект Location по zip коду.
            # Я знаю, что не обязательно прибегать к таким вот 
            # манипуляциям, просто для наглядности, что можно так.
            # Но лучше сделать это используя методы валидаторы с префиксом validate_          
            zip_code = validated_data.get('current_location', instance.current_location)
            location = Location.objects.get(zip=str(zip_code))
            full_address = f"{location.city}, {location.region} {location.zip}"
        except Location.DoesNotExist:
            full_address = instance.current_location
            raise ValidationError(f'Локации по данному zop code {zip_code} не имеется в базе Location.')

        instance.current_location = full_address
        instance.number = validated_data.get('number', instance.number)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.save()
        return instance
    
    def validate_number(self, value):
        # проверяю есть ли такой номер в базе, за исключением той записи у оторого 
        # первичный ключ равен нашему интсансу, т.е. записи которую мы хотим изменить
        if Truck.objects.filter(number=value).exclude(pk=self.instance.pk).exists():
            raise ValidationError(f'Данный номер {value} не является уникальным и уже имеется в базе.')
        return value
    
    def to_representation(self, instance):
        """по дефолту в поле current_location будет показан только индекс, а не весь адрес"""
        data = super().to_representation(instance)
        data['current_location'] = instance.current_location.split()[-1]
        return data


class CargoModelSerializer(ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'


                

        