# Generated by Django 2.1.2 on 2018-12-12 15:27

from django.db import migrations, models
import django.db.models.deletion
import interactions.models.interactions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interactions', '0003_delete_slotfield'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessOfferingInteraction',
            fields=[
                ('interaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='interactions.Interaction')),
            ],
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='DocumentsListSupplyInteraction',
            fields=[
                ('interaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='interactions.Interaction')),
            ],
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='GreetingInteraction',
            fields=[
                ('interaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='interactions.Interaction')),
            ],
            bases=('interactions.interaction',),
        ),
        migrations.CreateModel(
            name='PrivateInfoFormInteraction',
            fields=[
                ('interaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='interactions.Interaction')),
            ],
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='ConsideringSelfServiceInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='DesiredCurrencyInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='DialogTerminationInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='IntentRetrievalInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='OfficeRecommendationInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='OnlineReservingFinalizationInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='OperatorSwitchInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
    ]