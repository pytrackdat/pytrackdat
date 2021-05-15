# Generated by Django 3.2.2 on 2021-05-15 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snapshot_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snapshot',
            name='name',
            field=models.TextField(help_text='Name of JSON snapshot file', max_length=127),
        ),
        migrations.AlterField(
            model_name='snapshot',
            name='size',
            field=models.IntegerField(help_text='Size of snapshot (in bytes)'),
        ),
    ]