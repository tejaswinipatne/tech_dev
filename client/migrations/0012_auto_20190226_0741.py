# Generated by Django 2.1.4 on 2019-02-26 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0011_auto_20190226_0621'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaigntrack',
            old_name='campaign_id',
            new_name='campaign',
        ),
    ]
