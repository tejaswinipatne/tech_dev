# Generated by Django 2.1.1 on 2018-12-26 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('setupdata', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='card_details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_no', models.BigIntegerField()),
                ('card_holder_name', models.CharField(max_length=100)),
                ('card_type', models.CharField(max_length=50)),
                ('expiry_month', models.CharField(max_length=2)),
                ('expiry_year', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='client_vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_contact', models.BigIntegerField(blank=True, null=True)),
                ('primary_name', models.CharField(blank=True, max_length=100, null=True)),
                ('primary_designation', models.TextField(blank=True, null=True)),
                ('primary_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('primary_directdial', models.BigIntegerField(blank=True, null=True)),
                ('secondary_contact', models.BigIntegerField(blank=True, null=True)),
                ('secondary_name', models.CharField(max_length=100)),
                ('secondary_designation', models.TextField(blank=True, null=True)),
                ('secondary_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('secondary_directdial', models.BigIntegerField(blank=True, null=True)),
                ('alt_number1', models.BigIntegerField(blank=True, null=True)),
                ('alt_number2', models.BigIntegerField(blank=True, null=True)),
                ('logo', models.TextField(blank=True, null=True)),
                ('website', models.TextField(blank=True, null=True)),
                ('document_file', models.TextField(blank=True, null=True)),
                ('lead_per_month', models.IntegerField(blank=True, null=True)),
                ('unique_reach_per_month', models.IntegerField(blank=True, null=True)),
                ('company_name', models.CharField(blank=True, max_length=120, null=True)),
                ('company_registerd_date', models.DateField(blank=True, null=True)),
                ('company_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('annual_revenue', models.IntegerField(blank=True, null=True)),
                ('company_logo', models.FileField(blank=True, null=True, upload_to='media/')),
                ('company_background', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.company_background')),
                ('company_size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.company_size')),
                ('geo_loc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.countries')),
                ('industry_speciality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.industry_speciality')),
                ('industry_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.industry_type')),
                ('job_levels', models.ManyToManyField(to='setupdata.job_level')),
                ('marketing_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.source_touches')),
                ('pricing_flexibility', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.pricing_flexibility')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
        migrations.CreateModel(
            name='complex_program_capacity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leads', models.IntegerField(blank=True, null=True)),
                ('is_active', models.IntegerField(default=1)),
                ('level_intent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.level_intent')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
        migrations.CreateModel(
            name='data_assesment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_overview', models.CharField(blank=True, max_length=500, null=True)),
                ('unique_value_prop', models.CharField(blank=True, max_length=500, null=True)),
                ('sweet_spot', models.CharField(blank=True, max_length=500, null=True)),
                ('sweet_spot_text', models.CharField(blank=True, max_length=500, null=True)),
                ('year_incorporated', models.CharField(blank=True, max_length=500, null=True)),
                ('database_overall_size', models.CharField(blank=True, max_length=500, null=True)),
                ('database_size_us', models.CharField(blank=True, max_length=500, null=True)),
                ('database_opt_in', models.CharField(blank=True, max_length=500, null=True)),
                ('database_attribute', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_time', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_method', models.CharField(blank=True, max_length=100, null=True)),
                ('vendor_type', models.CharField(blank=True, max_length=100, null=True)),
                ('registration_process', models.CharField(blank=True, max_length=100, null=True)),
                ('lead_gen_capacity', models.CharField(blank=True, max_length=500, null=True)),
                ('complex_program_capacity', models.CharField(blank=True, max_length=500, null=True)),
                ('language_supported', models.CharField(blank=True, max_length=500, null=True)),
                ('networks_and_publishers', models.CharField(blank=True, max_length=500, null=True)),
                ('networks_and_publishers_other', models.CharField(blank=True, max_length=500, null=True)),
                ('language_supported_other', models.CharField(blank=True, max_length=500, null=True)),
                ('nda_aggrement', models.IntegerField(default=0)),
                ('msa_aggrement', models.IntegerField(default=0)),
                ('gdpr_aggrement', models.IntegerField(default=0)),
                ('dpa_aggrement', models.IntegerField(default=0)),
                ('io_aggrement', models.IntegerField(default=0)),
                ('call_center_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='call_center_location', to='setupdata.countries')),
                ('data_processing_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='data_processing_location', to='setupdata.countries')),
                ('hq_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hq_ocation', to='setupdata.countries')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
        migrations.CreateModel(
            name='database_attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=25, null=True)),
                ('is_active', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='language_supported',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=25, null=True)),
                ('is_active', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='lead_gen_capacity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leads', models.IntegerField(blank=True, null=True)),
                ('is_active', models.IntegerField(default=1)),
                ('source_touches', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='setupdata.source_touches')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
        migrations.CreateModel(
            name='networks_and_publishers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=25, null=True)),
                ('is_active', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='registration_process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=25, null=True)),
                ('is_active', models.IntegerField(default=1)),
            ],
        ),
        migrations.AddField(
            model_name='card_details',
            name='client_vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client_vendor.client_vendor'),
        ),
    ]
