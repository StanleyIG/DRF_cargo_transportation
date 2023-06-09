# Generated by Django 4.2.1 on 2023-05-25 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pick_up', models.CharField(default='', max_length=10)),
                ('delivery', models.CharField(default='', max_length=10)),
                ('weight', models.DecimalField(decimal_places=1, max_digits=4)),
                ('description', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
                ('zip', models.CharField(max_length=10)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=5, unique=True)),
                ('current_location', models.CharField(default='', max_length=10)),
                ('capacity', models.IntegerField()),
            ],
        ),
    ]
