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


class CargoModelSerializer(ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'

        