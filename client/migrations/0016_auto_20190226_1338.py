# Generated by Django 2.1.4 on 2019-02-26 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0015_auto_20190226_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaigntrack',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaign.Campaign'),
        ),
    ]
