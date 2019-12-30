from django.db import models

from user.models import user

from campaign.models import *
from setupdata.models import *


# Create your models here.
class client_vendor(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)

    primary_contact = models.BigIntegerField(blank=True, null=True)
    primary_name = models.CharField(max_length=100, blank=True, null=True)
    primary_designation = models.TextField(blank=True, null=True)
    primary_email = models.EmailField(blank=True, null=True)
    primary_directdial = models.BigIntegerField(blank=True, null=True)

    secondary_contact = models.BigIntegerField(blank=True, null=True)
    secondary_name = models.CharField(max_length=100)
    secondary_designation = models.TextField(blank=True, null=True)
    secondary_email = models.EmailField(blank=True, null=True)
    secondary_directdial = models.BigIntegerField(blank=True, null=True)
    alt_number1 = models.BigIntegerField(blank=True, null=True)
    alt_number2 = models.BigIntegerField(blank=True, null=True)

    logo = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    geo_loc = models.ForeignKey(
        countries, on_delete=models.CASCADE, blank=True, null=True)
    document_file = models.TextField(blank=True, null=True)

    industry_type = models.ForeignKey(
        industry_type, on_delete=models.CASCADE, blank=True, null=True)
    industry_speciality = models.ForeignKey(
        industry_speciality, on_delete=models.CASCADE, blank=True, null=True)

    job_levels = models.ManyToManyField(job_level)

    lead_per_month = models.IntegerField(blank=True, null=True)
    unique_reach_per_month = models.IntegerField(blank=True, null=True)
    marketing_method = models.ForeignKey(
        source_touches, on_delete=models.CASCADE, null=True)

    company_name = models.CharField(max_length=120, blank=True, null=True)
    company_registerd_date = models.DateField(blank=True, null=True)
    company_email = models.EmailField(null=True, blank=True)
    company_size = models.ForeignKey(
        company_size, on_delete=models.CASCADE, blank=True, null=True)
    company_background = models.ForeignKey(
        company_background, on_delete=models.CASCADE, blank=True, null=True)
    pricing_flexibility = models.ForeignKey(
        pricing_flexibility, on_delete=models.CASCADE, blank=True, null=True)
    annual_revenue = models.IntegerField(blank=True, null=True)
    company_logo = models.FileField(upload_to='media/', blank=True, null=True)
    media_kit = models.FileField(upload_to='media/', blank=True, null=True)

    def __str__(self):
        return self.user.user_name


# registrtions proccess
class registration_process(models.Model):
    type = models.CharField(max_length=25, blank=True, null=True)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return self.type


# database Attribute for vendor on boarding
class database_attribute(models.Model):
    type = models.CharField(max_length=25, blank=True, null=True)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return self.type

# Language Supported for vendor on boarding


class language_supported(models.Model):
    type = models.CharField(max_length=25, blank=True, null=True)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return self.type

# Language Supported for vendor on boarding


class networks_and_publishers(models.Model):
    type = models.CharField(max_length=25, blank=True, null=True)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return self.type


class lead_gen_capacity(models.Model):
    source_touches = models.ForeignKey(
        source_touches, on_delete=models.CASCADE, blank=True, null=True)
    leads = models.IntegerField(blank=True, null=True)
    user_id = models.ForeignKey(
        user, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return self.source_touches.type


class complex_program_capacity(models.Model):
    level_intent = models.ForeignKey(
        level_intent, on_delete=models.CASCADE, blank=True, null=True)
    leads = models.IntegerField(blank=True, null=True)
    user_id = models.ForeignKey(
        user, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return self.user_id.user_name

# data assessement details for vendors


class data_assesment(models.Model):
    company_overview = models.CharField(max_length=500, blank=True, null=True)
    hq_location = models.ForeignKey(
        countries, on_delete=models.CASCADE, blank=True, null=True, related_name='hq_ocation')
    call_center_location = models.ForeignKey(
        countries, on_delete=models.CASCADE, blank=True, null=True, related_name='call_center_location')
    data_processing_location = models.ForeignKey(
        countries, on_delete=models.CASCADE, blank=True, null=True, related_name='data_processing_location')
    unique_value_prop = models.CharField(max_length=500, blank=True, null=True)
    sweet_spot = models.CharField(max_length=500, blank=True, null=True)
    sweet_spot_text = models.CharField(max_length=500, blank=True, null=True)
    year_incorporated = models.CharField(max_length=500, blank=True, null=True)
    database_overall_size = models.CharField(
        max_length=500, blank=True, null=True)
    database_size_us = models.CharField(max_length=500, blank=True, null=True)
    database_opt_in = models.CharField(max_length=500, blank=True, null=True)
    database_attribute = models.CharField(
        max_length=100, blank=True, null=True)

    delivery_time = models.CharField(max_length=100, blank=True, null=True)
    delivery_method = models.CharField(max_length=100, blank=True, null=True)
    vendor_type = models.CharField(max_length=100, blank=True, null=True)
    registration_process = models.CharField(
        max_length=100, blank=True, null=True)
    lead_gen_capacity = models.CharField(max_length=500, blank=True, null=True)
    complex_program_capacity = models.CharField(
        max_length=500, blank=True, null=True)
    language_supported = models.CharField(
        max_length=500, blank=True, null=True)
    networks_and_publishers = models.CharField(
        max_length=500, blank=True, null=True)
    networks_and_publishers_other = models.CharField(
        max_length=500, blank=True, null=True)
    language_supported_other = models.CharField(
        max_length=500, blank=True, null=True)
    nda_aggrement = models.IntegerField(default=0)
    nda_aggrement_path = models.FileField(upload_to='Client_Vendor/Data_assesments', blank=True, null= True)   #new
    msa_aggrement = models.IntegerField(default=0)
    msa_aggrement_path = models.FileField(upload_to='Client_Vendor/Data_assesments', blank=True, null= True)#new
    gdpr_aggrement = models.IntegerField(default=0)
    gdpr_aggrement_path = models.FileField(upload_to='Client_Vendor/Data_assesments', blank=True, null= True) #new
    dpa_aggrement = models.IntegerField(default=0)
    dpa_aggrement_path = models.FileField(upload_to='Client_Vendor/Data_assesments', blank=True, null= True) #new
    io_aggrement = models.IntegerField(default=0)
    io_aggrement_path = models.FileField(upload_to='Client_Vendor/Data_assesments', blank=True, null= True) #new
    user = models.ForeignKey(
        user, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user.user_name


# Card Details
class card_details(models.Model):
    client_vendor = models.ForeignKey(client_vendor, on_delete=models.CASCADE)
    card_no = models.BigIntegerField()
    card_holder_name = models.CharField(max_length=100)
    card_type = models.CharField(max_length=50)
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)

    def __str__(self):
        return self.type
