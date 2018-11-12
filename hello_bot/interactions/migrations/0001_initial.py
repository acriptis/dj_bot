# Generated by Django 2.1.2 on 2018-11-06 14:02

from django.db import migrations, models
import django.db.models.deletion
import interactions.models.interactions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='UserDialog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='UserInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('Init', 'init'), ('Active', 'Active'), ('Ignored', 'Ignored'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed')], default='Init', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='UserSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='UserSlotProcess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=200)),
                ('slot_codename', models.CharField(max_length=200)),
                ('state', models.CharField(choices=[('Init', 'init'), ('Active', 'Active'), ('Ignored', 'Ignored'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed')], default='Init', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionInteractionFactory',
            fields=[
                ('interaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='interactions.Interaction')),
                ('question', models.CharField(max_length=200)),
                ('slot_name', models.CharField(max_length=200)),
            ],
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='SendTextOperation',
            fields=[
                ('interaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='interactions.Interaction')),
                ('text', models.CharField(max_length=200)),
            ],
            bases=('interactions.interaction',),
        ),
        migrations.AddField(
            model_name='userinteraction',
            name='interaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interactions.Interaction'),
        ),
        migrations.AddField(
            model_name='userinteraction',
            name='userdialog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interactions.UserDialog'),
        ),
        migrations.CreateModel(
            name='ByeInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
        migrations.CreateModel(
            name='GreetInteraction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('interactions.interaction', interactions.models.interactions.AbstractInteraction),
        ),
    ]
