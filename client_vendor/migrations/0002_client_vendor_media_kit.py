# Generated by Django 2.1.4 on 2019-03-13 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_vendor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client_vendor',
            name='media_kit',
            field=models.FileField(blank=True, null=True, upload_to='media/'),
        ),
    ]
