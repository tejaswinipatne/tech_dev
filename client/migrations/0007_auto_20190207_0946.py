# Generated by Django 2.1.4 on 2019-02-07 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0006_auto_20190206_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadvalidationcomponents',
            name='is_default',
            field=models.BooleanField(blank='true', default='0'),
        ),
    ]