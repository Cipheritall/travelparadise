# Generated by Django 3.1.2 on 2022-10-13 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0007_remove_flight_depart_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='business_fare',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='economy_fare',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='first_fare',
        ),
    ]
