#!/bin/bash

# Загрузить фикстуру locations.json
python manage.py loaddata locations.json

# Создать 1000 грузовиков
python manage.py create_trucks 1000

# создать грузы
python manage.py create_cargo