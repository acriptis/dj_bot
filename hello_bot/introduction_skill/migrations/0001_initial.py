# Generated by Django 2.1.2 on 2019-02-28 12:40

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interactions', '0007_slottyforminteraction'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntroductionInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction',),
        ),
    ]
