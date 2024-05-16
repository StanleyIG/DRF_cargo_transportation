from django.db import IntegrityError
from django.forms import ValidationError
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, CharField, Serializer, IntegerField, StringRelatedField
from rest_framework import serializers
from .models import Location, Truck, Cargo


class LocationModelSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class TruckModelSerializer(ModelSerializer):
    class Meta:
        model = Truck
        fields = '__all__'

    def update(self, instance, validated_data):
        try:
            zip_code = validated_data.get(
                'current_location', instance.current_location)
            location = Location.objects.get(zip=str(zip_code))
            full_address = f"{location.city}, {location.region} {location.zip}"
        except Location.DoesNotExist:
            full_address = instance.current_location
            raise ValidationError(f'Локации по данному zip code {zip_code} не имеется в базе Location.')

        instance.current_location = full_address
        instance.number = validated_data.get('number', instance.number)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.save()
        return instance

    # def validate_number(self, value):
    #     # проверяю есть ли такой номер в базе, за исключением той записи у оторого
    #     # первичный ключ равен нашему интсансу, т.е. записи которую мы хотим изменить
    #     if Truck.objects.filter(number=value).exclude(pk=self.instance.pk).exists():
    #         raise ValidationError(f'Данный номер {value} не является уникальным и уже имеется в базе.')
    #     return value

    def to_representation(self, instance):
        """по дефолту в поле current_location будет показан только индекс, а не весь адрес"""
        data = super().to_representation(instance)
        data['current_location'] = instance.current_location.split()[-1]
        return data


class CargoModelSerializer(ModelSerializer):

    class Meta:
        model = Cargo
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.pick_up = validated_data.get('pick_up', instance.pick_up)
        instance.delivery = validated_data.get('delivery', instance.delivery)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()
        return instance
        
    # def validate_pick_up(self, value):
    #     location = Location.objects.get(zip=str(value))
    #     if Cargo.objects.filter(pick_up=value).exclude(pk=self.instance.pk).exists():
    #         raise ValidationError(f'Локации по данному zip code {location.pick_up} не имеется в базе Location.')
    #     return value
    
    # def validate_delivery(self, value):
    #     if Cargo.objects.filter(delivery=value).exclude(pk=self.instance.pk).exists():
    #         raise ValidationError(f'Локации по данному zip code не имеется в базе Location.')
    #     return value
    

    # def to_representation(self, instance):
    #     """по дефолту в поле current_location будет показан только индекс, а не весь адрес"""
    #     data = super().to_representation(instance)
    #     data['pick_up'] = instance.delivery.split()[-1]
    #     data['delivery'] = instance.delivery.split()[-1]
    #     return data

                
                
