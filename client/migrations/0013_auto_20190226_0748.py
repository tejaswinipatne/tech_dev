# Generated by Django 2.1.4 on 2019-02-26 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0012_auto_20190226_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaigntrack',
            name='start_date',
            field=models.DateTimeField(blank=True),
        ),
    ]
