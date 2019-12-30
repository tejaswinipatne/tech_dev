from django.db import models
from campaign.models import *
from user.models import *
import datetime

class UseAsTxtMapping(models.Model):
    ''' Model for saving use as text values '''
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        null='true'
    )

    original_txt = models.CharField(
        blank='true',
        max_length=500,
        null='true'
    )
    alternative_txt = models.CharField(
        blank='true', max_length=500, null='true')

    def __str__(self):
        return str(self.campaign) + " " + str(self.original_txt) + str(self.alternative_txt)


# External vendor.
class external_vendor(models.Model):
    ''' storing extrtnal vendor records '''
    client_id = models.CharField(blank='true', max_length=500, null='true')
    user = models.ForeignKey(user, on_delete=models.CASCADE, null='true')

    def __str__(self):
        return self.client_id


class ComponentsList(models.Model):
    """ list of specifications to show while creating campaign """
    label = models.CharField(blank='true', max_length=210, null='true')
    invoke_div = models.CharField(blank='true', max_length=200, null='true')
    position = models.IntegerField(blank='true',  null='true')
    # extra css class name for card div in dragula
    extra_css_class = models.CharField(
        blank='true',  null='true', max_length=210)
    is_default = models.BooleanField(blank='true', default="0")
    category = models.CharField(blank='true', max_length=210, null='true')

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Component List'
        verbose_name_plural = 'Component Lists'
        ordering = ['position']


class SelectedComponents(models.Model):
    """ Storing selceted components according to campaign """
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, null='true')
    component = models.ForeignKey(
        ComponentsList, on_delete=models.CASCADE, null='true')

    def __str__(self):
        return str(self.campaign)


class SetDefault(models.Model):
    """ Store set default valuses for specifications """
    field = models.CharField(blank='true', max_length=210, null='true')
    values = models.TextField(blank='true', null='true')
    user = models.ForeignKey(user, on_delete=models.CASCADE, null='true')

    def __str__(self):
        return str(self.field)

    class Meta:
        verbose_name = 'Set as Default'
        verbose_name_plural = 'Set as Defaults'
        ordering = ['user']


class LeadValidationComponents(models.Model):
    """ list of Custom validation  """
    label = models.CharField(blank='true', max_length=210, null='true')
    function_name = models.CharField(blank='true', max_length=210, null='true')
    position = models.IntegerField(blank='true',  null='true')
    is_default = models.BooleanField(blank='true', default="0")

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Lead validation Components'
        verbose_name_plural = 'Lead validation Components'
        ordering = ['position']


class SelectedLeadValidation(models.Model):
    """ Storing selceted lead validation to campaign """
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, null='true')
    component_list = models.TextField(null='true')

    def __str__(self):
        return str(self.campaign)

class HeaderSpecsValidation(models.Model):
    """ Storing selceted lead validation to campaign """
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, null='true')
    company_limit=models.IntegerField(null='true')

    def __str__(self):
        return str(self.campaign)

class HeadersValidation(models.Model):
    """ Storing header specs needed for validation """
    email_list = models.TextField(null='true')
    company_limit = models.IntegerField(null='true')

    def __str__(self):
        return str(self.email_list)


class ApiLinks(models.Model):

    links = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' ' + self.links


class ApiAccessUsers(models.Model):
    # Model for API links to client's users

    client_id = models.ForeignKey(user, on_delete=models.CASCADE)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    token = models.CharField(max_length=200)
    ApiAccess = models.ManyToManyField(
        ApiLinks, related_name='recommended', blank=True)

    def __str__(self):
        return self.email


class CampaignTrack(models.Model):

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    created_date = models.DateTimeField(blank=True)
    start_date = models.DateTimeField(auto_now=False, blank=True)
    data_vendor_assign = models.TextField(blank=True)
    data_vendor_assign_count = models.IntegerField(default=0)
    client_action = models.TextField(blank=True)
    client_action_count = models.IntegerField(default=0)
    complete_status = models.TextField(blank=True)
    complete_status_count = models.IntegerField(default=0)

    def __str__(self):
        return self.campaign.name



# docusign pdf
class Document(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    nda_mnda_document = models.FileField(upload_to='documents/', blank=True, null=True)
    msa_document = models.FileField(upload_to='documents/', blank=True, null=True)
    gdpr_document = models.FileField(upload_to='documents/', blank=True, null=True)
    dpa_document = models.FileField(upload_to='documents/', blank=True, null=True)
    io_document = models.FileField(upload_to='documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
