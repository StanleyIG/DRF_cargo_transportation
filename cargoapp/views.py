from django.forms import ValidationError
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .serializers import LocationModelSerializer, TruckModelSerializer, CargoModelSerializer
from .models import Location, Truck, Cargo
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from geopy.distance import distance
import re
from django.db.utils import IntegrityError
from django.core.cache import cache


"""
Сервис должен поддерживать следующие базовые функции:

Уровень 1

- Создание нового груза (характеристики локаций pick-up, delivery определяются по введенному zip-коду); реализованно
- Получение списка грузов (локации pick-up, delivery, количество ближайших машин до груза ( =< 450 миль)); реализованно
- Получение информации о конкретном грузе по ID (локации pick-up, delivery, вес, описание, список номеров ВСЕХ машин с расстоянием до выбранного груза); реализованно
- Редактирование машины по ID (локация (определяется по введенному zip-коду)); реализованно
- Редактирование груза по ID (вес, описание); реализованно
- Удаление груза по ID. реализованно

Уровень 2

Все что в уровне 1 + дополнительные функции:

- Фильтр списка грузов (вес, км ближайших машин до грузов); реализованно 
- Автоматическое обновление локаций всех машин раз в 3 минуты (локация меняется на другую случайную).
"""


class LocationModelViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationModelSerializer


class TruckModelViewSet(ModelViewSet):
    queryset = Truck.objects.all()
    serializer_class = TruckModelSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.validated_data.pop('id', None)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class CargoModelViewSet(ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoModelSerializer

    def create(self, request, *args, **kwargs):
        pick_up_zip = request.data.get('pick_up')
        delivery_zip = request.data.get('delivery')
        weight = request.data.get('weight')
        description = request.data.get('description')

        # Получаю локации по zip-коду
        pick_up_location = get_object_or_404(Location, zip=str(pick_up_zip))
        delivery_location = get_object_or_404(Location, zip=str(delivery_zip))

        # Создаю груз
        cargo = Cargo.objects.create(
            pick_up=pick_up_location,
            delivery=delivery_location,
            weight=weight,
            description=description
        )

        serializer = self.get_serializer(cargo)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        pick_up_str = data['pick_up']
        pick_up_zip = re.search(r'\d{6}', pick_up_str).group(0).strip()
        pick_up_location = get_object_or_404(Location, zip=str(pick_up_zip))

        trucks = Truck.objects.all()
        nearby_trucks = []
        for truck in trucks:
            current_location_str = truck.current_location
            current_location_zip = re.search(
                r'\d{6}', current_location_str).group(0).strip()
            try:
                current_location = Location.objects.get(
                    zip=str(current_location_zip))
            except Location.DoesNotExist:
                continue
            cargo_distance = distance((pick_up_location.latitude,
                                       pick_up_location.longitude),
                                      (current_location.latitude,
                                       current_location.longitude)).km
            if cargo_distance <= 3000:
                nearby_trucks.append((truck.number, cargo_distance))

        data['count_trucks'] = len(nearby_trucks)
        data['nearby_trucks'] = nearby_trucks

        return Response(data)
    

    def list(self, request, *args, **kwargs):
        cache_data = cache.get('data_ready')
        if cache_data:
            print('Есть данные')
            if cache.get(f'truck') or cache.get(f'location'):
                print('Есть бновления')
                # Обнулить кэш
                print('Обнулить кэш')
                cache.clear()
            print('Возвращаю кэш')
            return Response(cache_data)
                
        queryset = self.filter_queryset(self.get_queryset())
        # запрос списка грузов по конкретному расстоянию груза от трака
        distance_request = request.query_params.get('distance')
        weight = self.request.query_params.get('weight')
        # print(distance_request, weight)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        trucks = Truck.objects.all()
        for i in range(len(data)):
            pick_up_str = data[i]['pick_up']
            pick_up_zip = re.search(r'\d{6}', pick_up_str).group(0).strip()
            pick_up_location = Location.objects.filter(
                zip=str(pick_up_zip)).first()

            if pick_up_location is not None:
                nearby_trucks = []
                for truck in trucks:
                    current_location_str = truck.current_location
                    current_location_zip = re.search(
                        r'\d{6}', current_location_str).group(0).strip()
                    capacity = truck.capacity
                    try:
                        current_location = Location.objects.get(
                            zip=str(current_location_zip))
                    except Location.DoesNotExist:
                        data[i]['count_trucks'] = 0
                        continue
                    cargo_distance = distance((pick_up_location.latitude,
                                               pick_up_location.longitude),
                                              (current_location.latitude,
                                               current_location.longitude)).km
                    if cargo_distance <= 2000 and not distance_request:
                        nearby_trucks.append((truck.number, cargo_distance))
                    elif distance_request and weight:
                        if cargo_distance <= int(distance_request) and int(weight) <= capacity:
                            nearby_trucks.append(
                                (truck.number, cargo_distance))
                    elif distance_request:
                        if cargo_distance <= int(distance_request):
                            nearby_trucks.append(
                                (truck.number, cargo_distance))

                if distance_request:
                    data[i]['count_trucks'] = nearby_trucks
                elif distance_request and weight:
                    data[i]['count_trucks'] = nearby_trucks
                else:
                    data[i]['count_trucks'] = len(nearby_trucks)
                    
        # ключи кэша простые без уникальности, только для проверки.
        # способов обновд\ления даных кэша через Django signals
        cache.set('data_ready', data, timeout=60 * 60) 
            
        return Response(data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
    
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('id', None)
        self.perform_update(serializer)
        return Response(serializer.data)
        

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     data = {
    #         'weight': request.data.get('weight', instance.weight),
    #         'description': request.data.get('description', instance.description),
    #     }
    #     serializer = self.get_serializer(instance, data=data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)

    # Фильтр списка грузов (вес)

    def get_queryset(self):
        queryset = Cargo.objects.all()
        weight = self.request.query_params.get('weight')
        # print(weight)
        if weight:
            return Cargo.objects.filter(weight=weight)
        return queryset


# def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         data = serializer.data
#         trucks = Truck.objects.all()
#         for i in range(len(data)):
#             pick_up_str = data[i]['pick_up']
#             pick_up_zip = re.search(r'\d{6}', pick_up_str).group(0).strip()
#             pick_up_location = Location.objects.filter(zip=str(pick_up_zip)).first()

#             if pick_up_location is not None:
#                 nearby_trucks = []
#                 for truck in trucks:
#                     current_location_str = truck.current_location
#                     current_location_zip = re.search(r'\d{6}', current_location_str).group(0).strip()
#                     try:
#                         current_location = Location.objects.get(zip=str(current_location_zip))
#                     except Location.DoesNotExist:
#                         data[i]['count_trucks'] = 0
#                         continue
#                     cargo_distance = distance((pick_up_location.latitude, pick_up_location.longitude), (current_location.latitude, current_location.longitude)).km
#                     if cargo_distance <= 1200:
#                         nearby_trucks.append((truck.number, cargo_distance))

#                 data[i]['count_trucks'] = len(nearby_trucks)


#         return Response(data)
