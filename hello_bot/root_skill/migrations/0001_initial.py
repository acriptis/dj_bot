# Generated by Django 2.1.2 on 2018-12-12 15:27

from django.db import migrations
import interactions.models.interactions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interactions', '0003_delete_slotfield'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowAgendaInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='ShowMemoryInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
    ]
