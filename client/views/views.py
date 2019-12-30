import difflib  # get ratio of string similarity
import functools
import json
import csv
import re
from xlrd import open_workbook
import operator
import random
from operator import itemgetter
from user.models import *
from user.models import user
import datetime
from django.conf import settings
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve, reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import ast

from campaign.forms import *
from campaign.models import *
from client.decorators import *
from client.models import *
from client.utils import *
from client.views.rfq_views import *
from client_vendor.models import *
from client_vendor.models import client_vendor
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from setupdata.models import *
from setupdata.models import (cities, countries,countries1 as countries_list1, industry_speciality,
                              industry_type, states, states1)
from setupdata.serializer import Cityserializers, Stateserializers
from vendors.views.views import *

from form_builder.views import *
from leads.models import *
from support.models import *
from itertools import chain
from operator import itemgetter
from campaign.choices import *



from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64



@login_required
@is_client
def cdashboard(request):
    """ return client dashboard data """

    if "is_login" in request.session:
        if request.session['is_login'] == True:
            userid = request.session['userid']
            vendordetail1 = client_top_vendor(userid)
            vendordetail = sorted(vendordetail1, key=itemgetter('revenue'), reverse=True)
            top_tc_vendors = tc_top_vendors_types()
            countries1 = countries_list1.objects.all()
            # countries1 = countries.objects.all()
            industry = industry_type.objects.all()
            expert = industry_speciality.objects.all()
            countrow = client_vendor.objects.filter(user_id=userid).count()
            topcampaigns = Campaign.objects.filter(
                user_id=userid).order_by('-id')[:5]

            if countrow == 1:
                client_vendor_detail = client_vendor.objects.get(
                    user_id=userid)
                userdetails = user.objects.get(id=userid)
                country = countries_list1.objects.get(id=userdetails.country)
                # country = countries.objects.get(id=userdetails.country)
                # city=cities.objects.filter(id=userdetails.city)
                state = states1.objects.get(id=userdetails.state)
                # state = states.objects.get(id=userdetails.state)
                industry = industry_type.objects.get(
                    id=client_vendor_detail.industry_type_id)
                speciality = industry_speciality.objects.get(
                    id=client_vendor_detail.industry_speciality_id)

                return render(request, 'dashboard/cdashboard.html', {'onBording': request.session['onBording'], 'topvendors': top_tc_vendors, 'vendordetail': vendordetail[:5], 'topcampaigns': topcampaigns, 'speciality': speciality, 'industry': industry, 'state': state, 'country': country, 'userdetails': userdetails, 'client_vendor': client_vendor_detail, 'expert': expert, 'countries': countries1, 'industry': industry})
            else:
                return render(request, 'dashboard/cdashboard.html', {'onBording': 0, 'vendordetail': vendordetail[:5], 'topvendors': top_tc_vendors, 'expert': expert, 'countries': countries1, 'industry': industry, 'topcampaigns': topcampaigns})

        else:
            return redirect('/login/')
    else:
        return redirect('/login/')


def loadstates(request):
    """ returns states """
    countryid = request.POST.get('id', None)
    # important: convert the QuerySet to a list object
    data = states1.objects.filter(country_id=countryid)
    # data = states.objects.filter(country_id=countryid)
    serializer = Stateserializers(data, many=True)
    return JsonResponse(serializer.data, safe=False)


def loadcity(request):
    """ returs cities """
    stateid = request.POST.get('id', None)
    # important: convert the QuerySet to a list object
    data = cities.objects.filter(state_id=stateid)
    serializer = Cityserializers(data, many=True)
    return JsonResponse(serializer.data, safe=False)


def onBording(request):
    """ submit client onbording form """
    userid = request.session['userid']
    countrow = client_vendor.objects.filter(user_id=userid).count()
    if countrow == 1:
        t = client_vendor.objects.get(user_id=userid)
        t.primary_name = request.POST['primary_name']
        t.primary_designation = request.POST['primary_designation']
        t.primary_email = request.POST['primary_email']
        t.primary_directdial = request.POST['primary_directdial']
        t.secondary_name = request.POST['secondary_name']
        t.secondary_designation = request.POST['secondary_designation']
        t.secondary_email = request.POST['secondary_email']
        t.secondary_directdial = request.POST['secondary_directdial']
        t.website = request.POST['website']
        t.industry_speciality_id = request.POST['industry_speciality_id']
        t.industry_type_id = request.POST['industry_type_id']
        t.save()

        t = user.objects.get(id=userid)
        t.user_name = request.POST['user_name']
        t.contact = request.POST['contact']
        t.address_line1 = request.POST['address_line1']
        t.address_line2 = request.POST['address_line2']
        t.country = request.POST['country']
        t.state = request.POST['state']
        t.save()

        site_url = settings.BASE_URL
        if request.session['usertype'] == 1:
            pages = 'client'
        else:
            pages = 'vendor'
        data = {'success': 1, 'site_url': site_url, 'pages': pages}
        return JsonResponse(data)
    else:
        t = user.objects.get(id=userid)
        t.user_name = request.POST['user_name']
        t.contact = request.POST['contact']
        t.address_line1 = request.POST['address_line1']
        t.address_line2 = request.POST['address_line2']
        t.country = request.POST['country']
        t.state = request.POST['state']
        t.status = '2'
        t.save()

        client_vendor.objects.create(
            primary_name=request.POST['primary_name'],
            primary_designation=request.POST['primary_designation'],
            primary_email=request.POST['primary_email'],
            primary_directdial=request.POST['primary_directdial'],
            primary_contact=request.POST['primary_directdial'],
            secondary_name=request.POST['secondary_name'],
            secondary_designation=request.POST['secondary_designation'],
            secondary_email=request.POST['secondary_email'],
            secondary_directdial=request.POST['secondary_directdial'],
            secondary_contact=request.POST['secondary_directdial'],
            alt_number1=request.POST['primary_directdial'],
            alt_number2=request.POST['secondary_directdial'],
            website=request.POST['website'],
            industry_speciality_id=request.POST['industry_speciality_id'],
            industry_type_id=request.POST['industry_type_id'],
            user_id=userid,
        )
        site_url = settings.BASE_URL
        if request.session['usertype'] == 1:
            pages = 'client'
        else:
            pages = 'vendor'
        data = {'success': 1, 'site_url': site_url, 'pages': pages}
        return JsonResponse(data)


def hook_add_campaign_data(user, objects_list):
    """
    * function Used to
      1) Check is data avaliable in set as default table for user.
         - If data exist then copy it with field names
      2) Copy save as txt data if exist

    parameters:
      1) objects_list - holds objects like campaign, mapping, specification, delivery

    """
    message, success, title = "", 0, "error"

    if SetDefault.objects.count():
        set_defaults_data = SetDefault.objects.filter(user=user)

        if(set_defaults_data):
            for set_default in set_defaults_data:
                field_name = set_default.field
                field_value = set_default.values

                for obj in objects_list:
                    # check is mapping object has current field
                    if hasattr(obj, field_name):
                        is_attr_set = setattr(
                            obj, field_name, field_value)  # f.foo=bar
                        obj.save()  # this will update only

        else:
            message += "No set as default data exists for user"
    else:
        message += "Set as default table is empty so skipping cloning of data"
    print(message)
    return True


@login_required
@is_client
def create_campaign(request):
    """
    create campaign

    Arguments:
        request {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    message, success, title = "", 0, "error"
    lead_validation_list=[] #store all default lead validation specs
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            form.save()

            campaign = Campaign.objects.latest("id")

            campaign_id = campaign.id

            # create other table with empty data
            # so we can open edit case paer page directly
            specification = Specification(campaign=campaign)
            specification.save()

            mapping = Mapping(campaign=campaign)
            mapping.save()

            terms = Terms(campaign=campaign)
            terms.save()

            delivery = Delivery(campaign=campaign)
            delivery.save()
            message = "Campaign Created Successfully"

            #store default lead validation in database
            lead_validation =LeadValidationComponents.objects.filter(is_default='True')

            for lead in lead_validation:
                lead_validation_list.append(lead.function_name)

            SelectedLeadValidation.objects.create(campaign=campaign,component_list=lead_validation_list)
            HeaderSpecsValidation.objects.create(campaign=campaign,company_limit=4)

            # add notification
            title = 'New Campaign Created'
            desc = "Campaign named '" + \
                str(campaign.name) + "' created successfully"
            sender_id = request.session['userid']
            receiver_id = request.session['userid']
            print(receiver_id, title, desc, 1)
            from client.utils import noti_via_mail
            noti_via_mail(receiver_id, title, desc, mail_noti_new_campaign)
            RegisterNotification(sender_id, receiver_id,
                                 desc, title, 1, campaign, None)

            # add set as default data
            objects_list = [campaign, specification, mapping, terms, delivery]
            hook_add_campaign_data(campaign.user, objects_list)

            print(message)
            return redirect('add_campaign_spec', id=campaign_id)
        else:
            print(form.errors)
            message += str(form.errors)
        # return HttpResponse(message)
        context = {
            'campaignform': form,
        }
        # send with errors
        return render(request, 'campaign/create_campagin.html', context)

    # get method
    else:
        campaignform = CampaignForm()

        context = {
            'campaignform': campaignform,
        }
        # return render(request,'campaign/createcampaign.html', context)
        return render(request, 'campaign/create_campagin.html', context)


# select campaign type
@login_required
@is_client
def campaigntype(request):
    return render(request, 'campaign/campaign_type.html', {})


@login_required
@is_client
def add_campaign_spec(request, id):
    """ Add campaign specifications """
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        campaign_id = id
        message, success, title = "", 0, "error"
        #import ipdb; ipdb.set_trace()
        component_list = None
        if ComponentsList.objects.count():
            component_list = ComponentsList.objects.all()
        else:
            message = "Component_List table is empty \n"
        selected_component_list = None
        selected_component_ids = [-1]  # list of ids
        # get selected component list

        campaign = None  # init
        specification = None
        mapping = None
        terms = None
        delivery = None
        lead_validation=None
        lead_validation_list=[]
        useAsTxtMapping = []
        volume_and_cpls = None
        txt_mapping_list = []

        if Campaign.objects.count():
            if Campaign.objects.filter(id=campaign_id):
                campaign = Campaign.objects.get(id=campaign_id)
            else:
                message += "Campaign with id '" + \
                    str(campaign_id) + "' not found"
        else:
            message += "Campaign table is empty\n"

        # print("campaign ", campaign)
        if campaign:
            # is status is draft mode i.e. 0  or pending:3
            if campaign.status == 0 or campaign.status == 3:
                if SelectedComponents.objects.count():
                    selected_component_list = SelectedComponents.objects.filter(
                        campaign=campaign,
                    )
                    selected_component_ids = SelectedComponents.objects.filter(
                        campaign=campaign).values_list('component', flat=True)
                else:
                    message += "Selected Component list for campaign" + \
                        str(campaign.id) + " is empty\n"

                specification = Specification.objects.get(campaign=campaign)
                mapping = Mapping.objects.get(campaign=campaign)
                terms = Terms.objects.get(campaign=campaign)
                delivery = Delivery.objects.get(campaign=campaign)
                if SelectedLeadValidation.objects.filter(campaign=campaign).count() > 0 :
                    obj=SelectedLeadValidation.objects.filter(campaign=campaign)
                    for lead_validation_list in obj:
                        lead_validation_list=lead_validation_list.component_list
                # use as text mapping
                txt_mapping_exist = UseAsTxtMapping.objects.count()
                if(txt_mapping_exist):  # if records exist
                    useAsTxtMapping = UseAsTxtMapping.objects.filter(
                        campaign=campaign).values()  # list of dicts
                    # print(useAsTxtMapping.values())

                # CPL and Volume of level of intent
                volume_and_cpls_exist = Volume_CPL.objects.count()
                if(volume_and_cpls_exist):  # if records exist
                    volume_and_cpls = Volume_CPL.objects.filter(
                        campaign=campaign).values()  # list of dicts
                    # print(volume_and_cpls)

                campaignform = CampaignForm()
                specificationform = SpecificationForm()
                mappingform = MappingForm()
                termsform = TermsForm()
                deliveryform = DeliveryForm()

                # data filler
                campaign_category = Campaign_category.objects.all()
                campaign_pacing = Campaign_pacing.objects.all()
                days = Days.objects.all()
                industry_types = industry_type.objects.all()
                job_levels = job_level.objects.all()
                job_functions = job_function.objects.all()
                countries_list = countries_list1.objects.all()
                # countries_list = countries.objects.all()
                company_sizes = company_size.objects.all()
                source_touch = source_touches.objects.all()
                level_intents = level_intent.objects.all()
                assets_all = assets.objects.all()
                region_list=region1.objects.all()
                # region_list=region.objects.all()

                data_headers = data_header.objects.all()
                delivery_methods = delivery_method.objects.all()
                delivery_times = delivery_time.objects.all()

                lead_validation=LeadValidationComponents.objects.all()
                revenue_sizes = RevenueSize.objects.all()
                set_as_defaults = SetDefault.objects.filter(
                    user=request.session['userid']
                ).values_list('field', flat=True)

                if HeaderSpecsValidation.objects.filter(campaign=campaign).count() > 0:
                    company_limit = HeaderSpecsValidation.objects.get(campaign=campaign)
                    company_limit = company_limit.company_limit
                else:
                    company_limit=4
                context = {
                    'campaign': campaign,
                    'campaignform': campaignform,
                    'specification': specification,
                    'specificationform': specificationform,
                    "mappingform": mappingform,
                    "mapping": mapping,
                    "termsform": termsform,
                    "terms": terms,
                    "deliveryform": deliveryform,
                    "delivery": delivery,
                    # data filler
                    # set up data
                    "lead_validation":lead_validation,
                    "lead_list":lead_validation_list,
                    "company_limit":company_limit,
                    "campaign_category": campaign_category,
                    "campaign_pacing": campaign_pacing,
                    "days": days,
                    "industry_types": industry_types,
                    "job_levels": job_levels,
                    "job_functions": job_functions,
                    "company_sizes": company_sizes,
                    "countries": countries_list,
                    "source_touches": source_touch,
                    "level_intent": level_intents,
                    "assets": assets_all,
                    "region_list":region_list,
                    "tc_header_status":delivery.tc_header_status,
                    "custom_header_status":delivery.custom_header_status,
                    "data_headers": data_headers,
                    "custom_headers":delivery.custom_header.split(',') if delivery.custom_header else [],
                    "delivery_methods": delivery_methods,
                    "delivery_times": delivery_times,
                    "revenue_sizes": revenue_sizes,
                    "set_as_defaults": set_as_defaults,
                    "useAsTxtMapping": useAsTxtMapping,
                    "volume_and_cpls": volume_and_cpls,
                    "component_list": component_list,
                    "selected_component_list": selected_component_list,
                    "selected_component_ids": selected_component_ids,
                    "i": 0,  # incrementing variable in template
                }
                print(message)
                return render(request, 'campaign/add_campaign_specs.html', context)
            else:
                message += "Campaign status must be incomplete(i.e in draft mode or pending) to edit"
                print(message)
                return redirect("/client/create-campaign/")
        else:
            message += "No campaign found to edit with id : \n" + \
                str(campaign_id)
            print(message)
            return redirect("/client/create-campaign/")
    else:
        print(is_logged_in)
        return redirect("/logout/")


@login_required
@is_client
def change_campaign_status(request, id):
    """ change camapign status on action """
    campaign_id = id
    campaign = Campaign.objects.get(id=campaign_id)
    # change campaign status
    campaign.completion_status = "completed"
    campaign.status = 3
    campaign.save()

    # add notification
    if campaign.status == 3:
        title = 'New Campaign'
        desc = str(campaign.user.user_name)+" Created '" + \
            str(campaign.name) + "' Campaign"
    elif campaign.status == 1:
        title = 'Campaign Status Changed'
        desc = "Status of campaign '" + \
            str(campaign.name) + "' changed to live"
    elif campaign.status == 4:
        title = 'Campaign Completed'
        desc = str(campaign.name) + " Completed"
    sender_id = request.session['userid']
    receiver_id = request.session['userid']
    from client.utils import noti_via_mail
    noti_via_mail(receiver_id, title, desc, mail_noti_camp_status)
    RegisterNotification(sender_id, receiver_id, desc,
                         title, 1, campaign, None)
    superadmins = user.objects.filter(usertype__id=4)
    from client.utils import noti_via_mail
    for superad in superadmins:
        noti_via_mail(superad.id, title, desc, mail_noti_camp_status)
        RegisterNotification(sender_id, superad.id, desc,
                             title, 1, campaign, None)

    # suggest vendors
    suggest_vendors(request, campaign_id)
    # redirect to suggested vendor list page
    map_data = Mapping.objects.get(campaign_id=campaign_id)
    if campaign.rfq == 0:
        if (map_data.custom_status == 0 and map_data.custom_question > 0):
            return redirect(reverse('custom_question',kwargs={'camp_id': campaign_id}))
        else:
            if (campaign_allocation.objects.filter(campaign_id=campaign_id).count() == 0):
                return redirect(reverse('campaign-vendor-list', kwargs={'camp_id': campaign_id}))
            else:
                return redirect('client_pending_campaign')
    else:
        if ( map_data.custom_status == 0 and map_data.custom_question > 0):
            return redirect(reverse('custom_question',kwargs={'camp_id': campaign_id}))
        else:
            return redirect('client_pending_campaign')

# save records through ajax
def save_specifications(request):
    """ saving specifications selected values """
    message, success, title = "", 0, "error"
    specification = None
    if request.method == 'POST':
        data_in_post = ["campaign", "field_name", "field_value"]
        # defined in utils.py
        is_data_in_post = check_all_data_available_in_post(
            data_in_post, request.POST)

        if is_data_in_post['success']:
            campaign_id = request.POST.get("campaign")  # 26
            field_name = request.POST.get("field_name")
            field_value = request.POST.get("field_value")

            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.get(id=campaign_id)
                    if Specification.objects.count():
                        if Specification.objects.get(campaign=campaign.id):
                            specification = Specification.objects.get(
                                campaign=campaign.id)
                        else:
                            message += "No Specification exists with campaign id :" + \
                                str(campaign.id)
                    else:
                        message += "Error while getting specification object . Specification table is empty"
                else:
                    message += "No campaign exists with id :" + \
                        str(campaign_id)
            else:
                message += "Campaign Table is empty"

            # update fields
            if specification:
                # check object has property with field name
                if hasattr(specification, field_name):
                    is_attr_set = setattr(
                        specification, field_name, field_value)  # f.foo=bar
                    specification.save()  # this will update only

                    success = 1
                    title = 'success'
                    message = "specification updated successfully"
                else:
                    message += "Error... Specification table has no field '" + field_name + "'"
        else:
            message = is_data_in_post['message']
    else:
        message = "Please post data using post method"

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


#save lead validation through ajax
def save_lead_validation(request):
    """ update lead validations """
    campaign_id = request.POST.get("campaign")
    obj = Campaign.objects.get(id=campaign_id)
    # lead=SelectedLeadValidation(campaign=obj)
    lead = SelectedLeadValidation.objects.filter(campaign=obj)
    if lead:
        lead[0].component_list=list(request.POST.get('field_value').split(','))
        lead[0].save()
        jsonresponse = {
            "success": 1,
            "title": 'success',
            "message": 'Lead validation updated successfully',
        }
    else:
        lead = SelectedLeadValidation.objects.create(campaign=obj)
        lead.component_list=list(request.POST.get('field_value').split(','))
        lead.save()
        jsonresponse = {
            "success": 1,
            "title": 'success',
            "message": 'Lead validation updated successfully',
        }
    return JsonResponse(jsonresponse)

# save records through ajax
def save_mapping(request):
    """ saving campaign and specufications mapping """
    message, success, title = "", 0, "error"
    mapping = None

    if request.method == 'POST':
        data_in_post = ["campaign", "field_name", "field_value"]
        # defined in utils.py
        is_data_in_post = check_all_data_available_in_post(
            data_in_post, request.POST)

        if is_data_in_post['success']:
            campaign_id = request.POST.get("campaign")  # 26
            field_name = request.POST.get("field_name")
            field_value = request.POST.get("field_value")

            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.get(id=campaign_id)
                    if Mapping.objects.count():
                        if Mapping.objects.filter(campaign=campaign.id):
                            mapping = Mapping.objects.get(campaign=campaign.id)
                        else:
                            message += "No mapping exists with campaign id :" + \
                                str(campaign.id)
                    else:
                        message += "Error while getting mapping object . mapping table is empty"
                else:
                    message += "No campaign exists with id :" + \
                        str(campaign_id)
            else:
                message += "Campaign Table is empty"

            # update fields
            if mapping:
                # check object has property with field name
                if hasattr(mapping, field_name):
                    is_attr_set = setattr(
                        mapping, field_name, field_value)  # f.foo=bar
                    mapping.save()  # this will update only

                    success = 1
                    title = 'success'
                    message = "mapping updated successfully"
                else:
                    message += "Error... mapping table has no field '" + field_name + "'"
        else:
            message = is_data_in_post['message']
    else:
        message = "Please post data using post method"

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


# save records through ajax
def save_terms(request):
    """ savnig campaign terms data """
    message, success, title = "", 0, "error"
    mapping = None

    if request.method == 'POST':
        data_in_post = ["campaign", "field_name", "field_value"]
        # defined in utils.py
        is_data_in_post = check_all_data_available_in_post(
            data_in_post, request.POST)

        if is_data_in_post['success']:
            campaign_id = request.POST.get("campaign")  # 26
            field_name = request.POST.get("field_name")
            field_value = request.POST.get("field_value")

            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.get(id=campaign_id)
                    if Terms.objects.count():
                        if Terms.objects.filter(campaign=campaign.id):
                            terms = Terms.objects.get(campaign=campaign.id)
                        else:
                            message += "No Terms exists with campaign id :" + \
                                str(campaign.id)
                    else:
                        message += "Error while getting Terms object . Terms table is empty"
                else:
                    message += "No campaign exists with id :" + \
                        str(campaign_id)
            else:
                message += "Campaign Table is empty"

            # update fields
            if terms:
                # check object has property with field name
                if hasattr(terms, field_name):
                    is_attr_set = setattr(
                        terms, field_name, field_value)  # equal to f.foo=bar
                    terms.save()  # this will update only

                    success = 1
                    title = 'success'
                    message = "terms updated successfully"
                else:
                    message += "Error... terms table has no field '" + field_name + "'"
        else:
            message = is_data_in_post['message']
    else:
        message = "Please post data using post method"

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


def save_delivery(request):
    """ saving delivery details of campaign """
    message, success, title = "", 0, "error"
    mapping = None
    if request.method == 'POST':
        data_in_post = ["campaign", "field_name", "field_value"]
        # defined in utils.py
        is_data_in_post = check_all_data_available_in_post(
            data_in_post, request.POST)

        if is_data_in_post['success']:
            campaign_id = request.POST.get("campaign")  # 26
            field_name = request.POST.get("field_name")
            field_value = request.POST.get("field_value")
            print(field_value)

            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.get(id=campaign_id)
                    if Delivery.objects.count():
                        if Delivery.objects.filter(campaign=campaign.id):
                            delivery = Delivery.objects.get(
                                campaign=campaign.id)
                        else:
                            message += "No delivery exists with campaign id :" + \
                                str(campaign.id)
                    else:
                        message += "Error while getting delivery object . delivery table is empty"
                else:
                    message += "No campaign exists with id :" + \
                        str(campaign_id)
            else:
                message += "Campaign Table is empty"

            # update fields
            if delivery:
                # check object has property with field name
                if hasattr(delivery, field_name):
                    is_attr_set = setattr(delivery, field_name, field_value)  # f.foo=bar
                    # if (field_value !=  ''):
                    #     delivery.tc_header_status = 1
                    # else:
                    #     delivery.tc_header_status = 0
                    delivery.save()  # this will update only

                    # campaign.completion_status = 'completed'
                    # campaign.save()

                    success = 1
                    title = 'success'
                    message = "delivery updated successfully"
                else:
                    message += "Error... delivery table has no field '" + field_name + "'"
        else:
            message = is_data_in_post['message']
    else:
        message = "Please post data using post method"

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


@csrf_exempt
def save_delivery_method_comments(request):
    # print(request.POST)
    comments = {}
    if not request.POST.get("data") == '':
        campaign_id = request.POST.get("campaign_id")  # 26
        element = request.POST.get("element")
        data = request.POST.get("data")
        campaign = Delivery.objects.filter(campaign=campaign_id)
        print(campaign[0].__dict__)
        campaign[0].comments = comments.update({element: data})
        campaign[0].save()
    pass


def save_alternative_text(request):
    """ save alternative texts """
    campaign_id = request.POST.get("campaign_id")  # 26
    original_txt = request.POST.get("original_txt")
    alternative_txt = request.POST.get("alternative_txt")
    # print("campaign id :", campaign_id)
    # print("original_txt :", original_txt)
    # print("alternative_txt :", alternative_txt)
    campaign = Campaign.objects.get(id=campaign_id)
    create_new_record = False

    is_table_records_exist = UseAsTxtMapping.objects.count()
    if is_table_records_exist:
        useAsTxtMapping = UseAsTxtMapping.objects.filter(
            campaign=campaign,
            original_txt=original_txt,
        ).first()
        if(useAsTxtMapping):
            if alternative_txt == '':  # if empty means delete record
                useAsTxtMapping.delete()
            else:
                useAsTxtMapping.alternative_txt = alternative_txt
                # print(useAsTxtMapping.__dict__)
                if (useAsTxtMapping.alternative_txt == ''):
                    useAsTxtMapping.delete()
                else:
                    useAsTxtMapping.save()
        else:
            create_new_record = True
    else:
        create_new_record = True

    if(create_new_record):
        # create new mapping record
        useAsTxtMapping = UseAsTxtMapping.objects.create(
            campaign=campaign,
            original_txt=original_txt,
            alternative_txt=alternative_txt,
        )
        useAsTxtMapping.save()

    jsonresponse = {
        "success": 1,
        "title": "success",
        "message": "Alternative text saved successfully",
    }
    return JsonResponse(jsonresponse)

def save_lead_limit_cmp(request):
    """ Save lead limitation """
    campaign_id = int(request.POST.get("campaign_id"))
    limit       = int(request.POST.get("lead_limit"))
    if HeaderSpecsValidation.objects.filter(campaign=campaign_id).count() > 0 :
        lead_limit_update=HeaderSpecsValidation.objects.get(campaign=campaign_id)
        lead_limit_update.company_limit=limit
        lead_limit_update.save()
    else:
        HeaderSpecsValidation.objects.create(campaign_id=campaign_id,company_limit=limit)

    jsonresponse = {
        "success": 1,
        "title": "success",
        "message": "lead limit saved successfully",
    }
    return JsonResponse(jsonresponse)

def save_volume_and_cpl(request):
    ''' save campaign volume and cpl '''
    campaign_id = request.POST.get("campaign_id")  # 26
    level_of_intent = request.POST.get("level_of_intent")
    volume = request.POST.get("volume")
    cpl = request.POST.get("cpl")
    # print("campaign id :", campaign_id)
    # print("level_of_intent :", level_of_intent)
    # print("volume :", volume)
    # print("cpl :", cpl)

    campaign = Campaign.objects.get(id=campaign_id)
    create_new_record = False

    is_table_records_exist = Volume_CPL.objects.count()
    if is_table_records_exist:
        volume_CPL_list = Volume_CPL.objects.filter(
            campaign=campaign,
            level_of_intent=level_of_intent,
        ).first()
        if volume_CPL_list:
            volume_CPL_list.level_of_intent = level_of_intent
            volume_CPL_list.volume = volume
            volume_CPL_list.cpl = cpl
            volume_CPL_list.save()
        else:
            create_new_record = True
    else:
        create_new_record = True

    if(create_new_record):
        # create new mapping record
        volume_CPL_list = Volume_CPL.objects.create(
            campaign=campaign,
            level_of_intent=level_of_intent,
            volume=volume,
            cpl=cpl,
        )
        volume_CPL_list.save()

    jsonresponse = {
        "success": 1,
        "title": "success",
        "message": "Volume and CPL saved successfully",
    }
    return JsonResponse(jsonresponse)


def delete_volume_and_cpl(request):
    """ delete campaign colume and cpl """
    campaign_id = request.POST.get("campaign_id")  # 26
    level_of_intent = request.POST.get("level_of_intent")
    # print("level_of_intent :", level_of_intent)
    # print("campaign id :", campaign_id)

    campaign = Campaign.objects.get(id=campaign_id)
    jsonresponse = None

    is_table_records_exist = Volume_CPL.objects.count()
    if is_table_records_exist:
        volume_CPL_list = Volume_CPL.objects.filter(
            campaign=campaign,
            level_of_intent=level_of_intent,
        ).first()
        if(volume_CPL_list):
            volume_CPL_list.delete()
            jsonresponse = {
                "success": 1,
                "title": "success",
                "message": "Volume and CPL deleted successfully",
            }
    else:
        jsonresponse = {
            "success": 0,
            "title": "error",
            "message": "Error while deleting volume and CPL.. record not exist",
        }
    return JsonResponse(jsonresponse, safe=False)


# getattr and setattr on nested objects?
def nested_setattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(nested_getattr(obj, pre) if pre else obj, post, val)

# using wonder's beautiful simplification: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects/31174427?noredirect=1#comment86638618_31174427


def nested_getattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

def checkABMTemplate(header):
    """ Checket Template is valid or not """
    labels = ['DOMAIN_NAME','COMPANY_NAME']
    if set(header) == set(labels):
        return 1
    else:
        return 0

def checkSuppressionTemplate(header):
    """ Checket Template is valid or not """
    labels = ['DOMAIN_NAME','COMPANY_NAME']
    if set(header) == set(labels):
        return 1
    else:
        return 0

def creat_dict_list(data,header,last_id,abm_data):
    """
        Convert List to List of dict.
    """
    from datetime import datetime
    lead_data=[]
    current_data={}
    date = datetime.now()
    currant_date = date.strftime("%B %d %Y")
    time = date.strftime('%H:%M:%S')
    if len(abm_data)>0:
        for i in range(len(data)):
            if any(d['DOMAIN_NAME'] == data[i][0] for d in abm_data) != True:
                for j in range(len(header)):
                    current_data[header[j]]=data[i][j]
                last_id += 1
                new_data = {'id':last_id,'time':time, 'date': currant_date}
                current_data.update(new_data)
                lead_data.append(current_data)
                current_data={}
    else:
        for i in range(len(data)):
            for j in range(len(header)):
                current_data[header[j]]=data[i][j]
            last_id += 1
            new_data = {'id':last_id,'time':time, 'date': currant_date}
            current_data.update(new_data)
            lead_data.append(current_data)
            current_data={}
    return lead_data

def get_last_id_abm(campaign):
    """
        get last ID OF ABM
    """
    last_id=Specification.objects.get(campaign=campaign)
    return last_id.abm_count

def get_last_id_suppression(campaign):
    """
        get last ID OF Suppression
    """
    last_id=Specification.objects.get(campaign=campaign)
    return last_id.suppression_count

@csrf_exempt
def upload_single_file(request):
    """ used to upload single file form """
    message, success, title = "", 0, "error"
    is_data_ok = False


    if request.method == 'POST':
        data_in_post = ["id_campaign", "field_name"]
        # defined in utils.py
        is_data_in_post = check_all_data_available_in_post(
            data_in_post, request.POST)

        if is_data_in_post['success']:
            is_data_ok = True
        else:
            message = is_data_in_post['message']

        if is_data_ok:
            for filename, file in request.FILES.items():
                name = request.FILES[filename].name

                # get campaign id
                id_campaign = request.POST.get("id_campaign")

                # myfile = request.FILES['abm_company_list_file']
                myfile = request.FILES[filename]
                fs = FileSystemStorage()
                filename = fs.save("campaign/" + myfile.name,  myfile)




                # django get campaign object from model
                campaign = Campaign.objects.filter(id=id_campaign).first()

                if campaign:
                    # get specification record
                    specification = Specification.objects.filter(
                        campaign=campaign).first()
                    if specification:
                        # get field name to save
                        field_name = request.POST.get("field_name")

                        # check object has property with field name
                        if hasattr(specification, field_name):
                            # nested_setattr(object, 'pet.name', 'Sparky')
                            model_field_name = str(field_name) + ".name"
                            model_field_name = model_field_name.replace(
                                " ", "")

                            #abhi 9-2-2019 store abm data in list formate in database
                            if field_name == 'abm_company_file' :
                                filename='media/'+filename
                                rows,abm_list=[],[]
                                with open(filename, 'r') as csvfile:
                                    csvreader = csv.reader(csvfile)
                                    for row in csvreader:
                                        rows.append(row)
                                if checkABMTemplate(rows[0]):
                                    last_id=get_last_id_abm(id_campaign)
                                    if specification.abm_count > 0 :
                                        abm_list=ast.literal_eval(specification.abm_file_content)
                                        abm_list+=creat_dict_list(rows[1:],rows[0],last_id,abm_list)
                                        specification.abm_file_content=abm_list
                                        specification.abm_count=len(abm_list)
                                    else:
                                        abm_list=creat_dict_list(rows[1:],rows[0],last_id,abm_list)
                                        specification.abm_file_content=abm_list
                                        specification.abm_count=len(abm_list)

                                    specification.save()
                                    success = 1
                                    title = 'success'
                                    message = "specification updated successfully"
                                else:
                                    message += "ABM Template Not Match Plz Upload Valid Template: '"
                                    jsonresponse = {
                                        "success": 0,
                                        "title": request.POST,
                                        "message": message,
                                    }
                                    return JsonResponse(jsonresponse, safe=False)
                            elif field_name == 'suppression_company_file':
                                filename='media/'+filename
                                rows,supp_list=[],[]
                                with open(filename, 'r') as csvfile:
                                    csvreader = csv.reader(csvfile)
                                    for row in csvreader:
                                        rows.append(row)
                                if checkSuppressionTemplate(rows[0]):
                                    last_id=get_last_id_suppression(id_campaign)
                                    if specification.suppression_count > 0 :
                                        supp_list=ast.literal_eval(specification.suppression_file_content)
                                        supp_list+=creat_dict_list(rows[1:],rows[0],last_id,supp_list)
                                        specification.suppression_file_content=supp_list
                                        specification.suppression_count=len(supp_list)
                                    else:
                                        supp_list=creat_dict_list(rows[1:],rows[0],last_id,supp_list)
                                        specification.suppression_file_content=supp_list
                                        specification.suppression_count=len(supp_list)

                                    specification.save()
                                    success = 1
                                    title = 'success'
                                    message = "specification updated successfully"
                                else:
                                    message += "suppression Template Not Match Plz Upload Valid Template: '"
                                    jsonresponse = {
                                        "success": 0,
                                        "title": request.POST,
                                        "message": message,
                                    }
                                    return JsonResponse(jsonresponse, safe=False)
                                    #abhi
                        else:
                            message += "Error... Specification table has no field '" + field_name + "'"
                    else:
                        message += "Specification not exists with campaign: '", str(
                            campaign), "'"
                else:
                    message += "Campaign not exist with id : '", id_campaign, "'"

                # uploaded_file_url = fs.url(filename)
                success = 1
    else:
        message = "Please post data using post method"

    jsonresponse = {
        "success": 1,
        "title": request.POST,
        "message": message,
    }

    return JsonResponse(jsonresponse, safe=False)


def add_default(request):
    """ set as default function """
    message, success, title, is_data_ok = "", 0, "error", False
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        if request.method == "POST":
            data_in_post = ["invoke_div_name", "value"]
            # defined in utils.py
            is_data_in_post = check_all_data_available_in_post(
                data_in_post, request.POST)

            if is_data_in_post['success']:
                is_data_ok = True
            else:
                message = is_data_in_post['message']
        else:
            message += "Please use post method to post data"
    else:
        message = "Please login to add set as default fields of campaign"

    userid = request.session['userid']
    current_user = None
    if userid:
        if(user.objects.count()):
            if(user.objects.filter(id=userid)):
                current_user = user.objects.get(id=userid)
            else:
                message += "No records found with userid: '", reuest_userid, "' when adding set as default"
        else:
            message += "USer table looks empty when tried to get user for set as default"
    else:
        message += "user_id is not found in session"

    print(message)

    if(is_data_ok and current_user):
        field_name = request.POST.get("invoke_div_name")
        field_value = request.POST.get("value")

        """
        @params:
            field -- used for filter purpose
            defaults -- are used for insertion
        @output:
            object : the object of model in dict format
            created : Boolean value(True/ False)
        """
        obj, created = SetDefault.objects.update_or_create(
            field=field_name, user=current_user,
            defaults={'field': field_name,
                      'values': field_value, 'user': current_user},
        )
        success = 1
        title = "success"
        modified_field_name = field_name.title().replace("_", " ")
        if created:
            message = "'" + modified_field_name + \
                "' field added successfully as 'Default field'. It will automatically added to future campaign"
        else:
            message = "'" + modified_field_name + \
                "' field updated successfully as 'Default field'. It will automatically added to future campaign"

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


def remove_default(request):
    """ remvoing defaults from database """
    message, success, title, is_data_ok = "", 0, "error", False
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        if request.method == "POST":
            data_in_post = ["invoke_div_name", "value"]
            # defined in utils.py
            is_data_in_post = check_all_data_available_in_post(
                data_in_post, request.POST)

            if is_data_in_post['success']:
                is_data_ok = True
            else:
                message = is_data_in_post['message']
        else:
            message += "Please use post method to post data"
    else:
        message = "Please login to add set as default fields of campaign"

    userid = request.session['userid']
    current_user = None
    if userid:
        if(user.objects.count()):
            if(user.objects.filter(id=userid)):
                current_user = user.objects.get(id=userid)
            else:
                message += "No records found with userid: '", reuest_userid, "' when adding set as default"
        else:
            message += "USer table looks empty when tried to get user for set as default"
    else:
        message += "user_id is not found in session"

    print(message)

    if(is_data_ok and current_user):
        field_name = request.POST.get("invoke_div_name")
        field_value = request.POST.get("value")

        if SetDefault.objects.filter(field=field_name, user=current_user):
            # delete record
            SetDefault.objects.get(
                field=field_name, user=current_user).delete()
            success = 1
            title = "success"
            modified_field_name = field_name.title().replace("_", " ")
            message = "'" + modified_field_name + \
                "' field removed successfully from 'Default field' list."

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


# campaign_id
def suggest_vendors_old_client_vendor_table(request, campaign_id):

    message, success, title = "", 0, "error"
    # campaign_id = 49 # testing
    campaign = Campaign.objects.get(id=campaign_id)
    if campaign:
        #json_campaign = serializers.serialize('json', [campaign], indent=4)
        specification = Specification.objects.get(campaign=campaign)
        mapping = Mapping.objects.get(campaign=campaign)
        terms = Terms.objects.get(campaign=campaign)
        delivery = Delivery.objects.get(campaign=campaign)

        industry_types = []
        job_levels = []

        # get matching parameters
        # all() is important for many to many field
        camp_source_in_touches = campaign.method.all()
        if not camp_source_in_touches:
            message = "\n Source In touches in campaign is null"

        # campaign industry type
        camp_industry_type_str = mapping.industry_type
        # print(mapping.__dict__)
        if camp_industry_type_str:
            camp_industry_type_list = camp_industry_type_str.split(",")
            industry_types = industry_type.objects.filter(
                type__in=camp_industry_type_list,
            )
            # print(industry_types)
        else:
            message += "\n Industry Type is null in campaign"

        # campaign job level
        camp_job_level_str = mapping.job_level
        if camp_job_level_str:
            camp_job_level_list = camp_job_level_str.split(",")
            job_levels = job_level.objects.filter(
                type__in=camp_job_level_list,
            )
            # print(job_levels)
        else:
            message += "\n Industry Type is null in campaign"
        # get vendors
        # filter(user__usertype='2') -- filters by foreign key properties
        # here vendor contains user foreign key -- user table has usertype foreign key -- usertype table has type property
        client_vendors = client_vendor.objects.filter(user__usertype__type='vendor').filter(
            Q(marketing_method__in=camp_source_in_touches) |
            Q(industry_type__in=industry_types) |
            Q(job_levels__in=job_levels)
        ).distinct()

        if client_vendors:
            print(client_vendors[0].user.usertype.type)

        for index, vendor in enumerate(client_vendors):
            user_id = vendor.user.id
            # print(user_id)
            is_user_exists = user.objects.filter(id=user_id)
            if(is_user_exists):
                User = user.objects.get(id=user_id)
                # print(User)

                match_vendor = match_campaign_vendor.objects.filter(
                    campaign=campaign,
                    client_vendor=User,
                )
                if not match_vendor:
                    match_campaign_vendor.objects.create(
                        campaign=campaign,
                        client_vendor=User,
                        is_active=1
                    )
        # print(client_vendors)
        # return HttpResponse("completed")
        return True
    else:
        # return HttpResponse("Campaign is empty of id :", str(camapaign_id))
        return False


def suggest_vendors(request, campaign_id):  # campaign_id

    message, success, title = "", 0, "error"
    # campaign_id = 49 # testing
    campaign = Campaign.objects.get(id=campaign_id)
    if campaign:
        #json_campaign = serializers.serialize('json', [campaign], indent=4)
        specification = Specification.objects.get(campaign=campaign)
        mapping = Mapping.objects.get(campaign=campaign)
        terms = Terms.objects.get(campaign=campaign)
        delivery = Delivery.objects.get(campaign=campaign)

        outreach_method = []
        sweet_spot_geo = []  # country
        complex_program = []  # campaign_type
        industry_types = []

        # import ipdb; ipdb.set_trace(context=20)
        # get matching parameters # outreach_method
        # all() is important for many to many field
        camp_source_in_touches = campaign.method.all()
        if not camp_source_in_touches:
            message = "\n Source In touches in campaign is null"

        # convert queryset values to list
        method_list = []
        for method in camp_source_in_touches:
            method_list.append(str(method.id))

        # campaign country
        camp_country_str = mapping.country
        # print(mapping.__dict__)

        if camp_country_str:
            camp_country_list = camp_country_str.split(",")
            matching_countries = countries_list1.objects.filter(
                name__in=camp_country_list,
            )
            # matching_countries = countries.objects.filter(
            #     name__in=camp_country_list,
            # )
            # print(matching_countries)
        else:
            message += "\n Country is null in campaign"

        # get vendors
        # filter(user__usertype='2') -- filters by foreign key properties
        # here vendor contains user foreign key -- user table has usertype foreign key -- usertype table has type property
        # !!! -- temp removed .filter(user__status=3)

        # Filter Django database for field containing any value in an array
        query = Q()
        for letter in camp_country_list:
            query = query | Q(sweet_spot_text__icontains=letter)

        # Filter Django database for field containing any value in an array
        query2 = Q()
        for letter in method_list:
            query2 = query2 | Q(vendor_type__icontains=letter)

        # print(query)


        vendors = data_assesment.objects.filter(user__usertype__type='vendor').filter(query, query2).distinct()

        if vendors:
            print(vendors[0].user.usertype.type)

        match_campaign_vendor.objects.filter(campaign=campaign).delete()

        for index, vendor in enumerate(vendors):
            user_id = vendor.user.id
            # print(user_id)
            is_user_exists = user.objects.filter(id=user_id)
            if(is_user_exists):
                User = user.objects.get(id=user_id)
                # print(User)

                match_vendor = match_campaign_vendor.objects.filter(
                    campaign=campaign,
                    client_vendor=User,
                )
                if not match_vendor:
                    match_campaign_vendor.objects.create(
                        campaign=campaign,
                        client_vendor=User,
                        is_active=1
                    )
        # print(client_vendors)
        # return HttpResponse("completed")
        return True
    else:
        # return HttpResponse("Campaign is empty of id :", str(camapaign_id))
        return False


@csrf_exempt
def save_selected_components(request):
    """ save selected components """
    # return HttpResponse("save_selected_components() called from ajax")
    message, success, title = "", 0, "error"

    if request.method == 'POST':
        data_in_post = ["id_campaign", "id_selected_component"]
        # defined in utils.py
        is_data_in_post = check_all_data_available_in_post(
            data_in_post, request.POST)

        if is_data_in_post['success']:
            campaign_id = request.POST.get("id_campaign")  # 26
            id_component = request.POST.get("id_selected_component")

            campaign = None
            # check is campaigns are available in table
            campaigns_cnt = Campaign.objects.count()
            if campaigns_cnt:
                is_campaign_exist = Campaign.objects.filter(id=campaign_id)
                if is_campaign_exist:
                    campaign = Campaign.objects.get(id=campaign_id)
                else:
                    message += "Campaign with id " + \
                        str(campaign_id) + " not exist in table\n"
            else:
                message += "Campaign table is empty\n"

            # check is selected component available in original list of components
            if campaign:
                cnt_components = ComponentsList.objects.count()
                if cnt_components:
                    is_component_valid = ComponentsList.objects.filter(
                        id=id_component,
                    ).first()
                    if is_component_valid:
                        # check is already exist
                        is_already_exist = SelectedComponents.objects.filter(
                            campaign=campaign,
                            component=is_component_valid,
                        )
                        if is_already_exist:
                            message = "Selected component already exist in selected_list table( so skipping record insertion)."
                        else:
                            # add to selected element list
                            SelectedComponents.objects.create(
                                campaign=campaign,
                                component=is_component_valid,
                            )
                            success = 1
                            message = "Selected component added successfully."  # dont append replace message
                    else:
                        message += "Selected component '" + selected_component + \
                            "' not exist in Components_List table\n"
                else:
                    message += "It looks like component table is empty\n"
        else:
            message = is_data_in_post['message']
    else:
        message = "Please post data using post method"

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


@csrf_exempt
def remove_selected_component(request):
    """ remove component through ajax """
    message, success, title = "", 0, "error"

    if request.method == 'POST':
        data_in_post = ["id_campaign", "id_selected_component"]
        # defined in utils.py
        is_data_in_post = check_all_data_available_in_post(
            data_in_post, request.POST)

        if is_data_in_post['success']:
            campaign_id = request.POST.get("id_campaign")  # 26
            id_component = request.POST.get("id_selected_component")

            campaign = None
            # check is campaigns are available in table
            campaigns_cnt = Campaign.objects.count()
            if campaigns_cnt:
                is_campaign_exist = Campaign.objects.filter(id=campaign_id)
                if is_campaign_exist:
                    campaign = Campaign.objects.get(id=campaign_id)
                else:
                    message += ("Campaign with id " +
                                str(campaign_id) + " not exist in table\n")
            else:
                message += "Campaign table is empty \n"

            # check is selected component available in original list of components
            if campaign:
                cnt_components = ComponentsList.objects.count()
                if cnt_components:
                    is_component_valid = ComponentsList.objects.filter(
                        id=id_component,
                    ).first()
                    if is_component_valid:
                        # check is already exist
                        selected_component = SelectedComponents.objects.filter(
                            campaign=campaign,
                            component=is_component_valid,
                        ).first()
                        if selected_component:
                            selected_component.delete()
                            success = 1
                            message = "Selected Component successfully removed from table record"
                        else:
                            message = "Selected component not exist in table."
                    else:
                        message += "Selected component '" + selected_component + \
                            "' not exist in Components_List table\n"
                else:
                    message += "It looks like component table is empty\n"
        else:
            message = is_data_in_post['message']
    else:
        message = "Please post data using post method"

    jsonresponse = {
        "success": success,
        "title": title,
        "message": message,
    }
    return JsonResponse(jsonresponse)


def test_ajax(request):
    return render(request, 'testing_ajax.html')


@login_required
@is_client
def clone_campaign(request, campaign_id):
    """ cloneing campaign """
    message, success, title = "", 0, "error"
    # check is logged in
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        if campaign_id:
            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.get(id=campaign_id)
                    campaign_original = Campaign.objects.get(id=campaign_id)
                else:
                    message += "Error Campaign does not exist with an id '" + \
                        str(campaign_id) + "'"
            else:
                message = "Error.. Campaign table is empty"

            if campaign:
                specification = Specification.objects.get(campaign=campaign)
                mapping = Mapping.objects.get(campaign=campaign)
                terms = Terms.objects.get(campaign=campaign)
                delivery = Delivery.objects.get(campaign=campaign)
                methods = campaign.method.all()

                # clone data and create new campaign
                campaign.pk = None
                campaign.id = None
                campaign.io_number = None
                campaign.name = campaign.name + "cloned"
                campaign.status = 0
                campaign.save()

                # get new campaign id
                campaign_id = campaign.id
                print(" campign after clone: ", campaign)
                print(" campaign id after clone : ", campaign_id)

                specification.pk = None
                specification.id = None
                specification.campaign = campaign
                specification.save()

                mapping.pk = None
                mapping.id = None
                mapping.campaign = campaign
                mapping.save()

                terms.pk = None
                terms.id = None
                terms.campaign = campaign
                terms.save()

                delivery.pk = None
                delivery.id = None
                delivery.campaign = campaign
                delivery.save()

                #saving all methods
                campaign.method.add(*methods)
                campaign.save()
                # copy selected components also in draggable campaign
                if SelectedComponents.objects.count():
                    selected_component_list = SelectedComponents.objects.filter(
                        campaign=campaign_original,
                    )
                    modified_selected_component_list = []
                    for component in selected_component_list:
                        # copy elements
                        component.pk = None
                        component.id = None
                        component.campaign = campaign  # change campaign to new
                        modified_selected_component_list.append(component)

                    # bulk insert
                    if(modified_selected_component_list):
                        SelectedComponents.objects.bulk_create(
                            modified_selected_component_list)
                    else:
                        message += "Modified selected component list is empty so skipping bulk insert"

                else:
                    message += "Selected Component list for campaign" + \
                        str(campaign.id) + " is empty\n"

                # redirect to add specs
                if campaign.rfq == 1:
                    return redirect(reverse('edit_rfq_campaign', kwargs={'campaign_id': campaign_id}))
                else:
                    return redirect(reverse('edit_campaign', kwargs={'campaign_id': campaign_id}))
            else:
                print(message)
                return False
        else:
            message += "Please pass an campaign id in GET request"
    else:
        print(is_logged_in)
        return redirect("/logout/")


@login_required
@is_client
def edit_campaign(request, campaign_id):
    """ edit campaign """
    message, success, title = "", 0, "error"
    # check is logged in
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        if campaign_id:
            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.filter(id=campaign_id).first()
                else:
                    message += "Error Campaign does not exist with an id '" + \
                        str(campaign_id) + "'"
            else:
                message = "Error.. Campaign table is empty"

            if campaign:
                specification = Specification.objects.filter(
                    campaign=campaign).first()
                mapping = Mapping.objects.filter(campaign=campaign).first()
                terms = Terms.objects.filter(campaign=campaign).first()
                delivery = Delivery.objects.filter(campaign=campaign).first()

                campaignform = CampaignForm()
                all_selected_method = []
                for method in campaign.method.all():
                    all_selected_method.append(method.id)
                context = {
                    'campaign': campaign,
                    'specification': specification,
                    'mapping': mapping,
                    'terms': terms,
                    'delivery': delivery,
                    'campaignform': campaignform,
                    'all_selected_method': all_selected_method,
                }

                return render(request, 'campaign/campaign_edit.html', context)
            else:
                print(message)
                return False
        else:
            message += "Please pass an campaign id in GET request"
    else:
        print(is_logged_in)
        return redirect("/logout/")


@login_required
@is_client
def update_c_mandatory_fields(request, campaign_id):
    """ update campaign manadatory fields """
    # print(request.POST)

    campaign = Campaign.objects.get(id=campaign_id)
    form = CampaignForm(request.POST, instance=campaign)
    # print(form)
    if form.is_valid():
        form.save()
        if campaign.rfq == 1:
            mapping=Mapping.objects.get(campaign_id=campaign.id)
            mapping.country = request.POST.getlist('geo')
            mapping.save()
            message = "Campaign Created Successfully"

            # add notification
            title = 'New RFQ Campaign Created'
            desc = "Campaign named '" + \
                str(campaign.name) + "' created successfully"
            sender_id = request.session['userid']
            receiver_id = request.session['userid']
            superadmins = user.objects.filter(usertype__id=4)
            # noti_via_mail(sender_id, title, desc, mail)
            for superad in superadmins:
                RegisterNotification(sender_id, superad.id, desc,
                                     title, 1, campaign, None)
            #send request to vendors for rfq campaign
            rfq_vendor_allocation(campaign_id,sender_id)
            campaign.raimainingleads = campaign.target_quantity
            campaign.approveleads = 0
            campaign.save()
            return redirect('client_pending_campaign')
        else:
            campaign.raimainingleads = campaign.target_quantity
            campaign.approveleads = 0
            campaign.save()
            return redirect('add_campaign_spec', id=campaign_id)
    else:
        # return redirect('clonecampaign', id=campaign_id)
        print(form.errors)
        if campaign.rfq == 1:
            return redirect(reverse('edit_rfq_campaign', kwargs={'campaign_id': campaign_id}))
        else:
            return redirect(reverse('edit_campaign', kwargs={'campaign_id': campaign_id}))


@login_required
@is_client
def client_activity(request):
    """ client activity display """
    return render(request, 'campaign/client_activity.html', {})


@login_required
@is_client
def vendor_comparison(request):
    """ compair venodrs """
    return render(request, 'campaign/vendor-comparison.html', {})


@login_required
@is_client
def leads(request):
    context = {
        'days': [1, 2, 3],
    }
    # return render(request,'campaign/demo.html', context)
    return render(request, 'campaign/leads.html', {})


@login_required
@is_client
def campaignreports(request):
    """ generating campaign reports """
    return render(request, 'campaign/campaignreports.html', {})


@login_required
@is_client
def schedulereports(request):
    """ set scheduled reports """
    return render(request, 'campaign/schedulereports.html', {})


@login_required
@is_client
def account(request):
    """ Get clients TC account details """
    userid = request.session['userid']
    countrow = client_vendor.objects.filter(user_id=userid).count()
    if countrow == 1:
        users = user.objects.filter(id=userid)
        client = [item for item in client_vendor.objects.filter(
            user_id__in=users)][0]
        country = countries_list1.objects.filter(id=client.user.country)
        # country = countries.objects.filter(id=client.user.country)
        city = cities.objects.filter(id=client.user.city)
        state = states1.objects.filter(id=client.user.state)
        # state = states.objects.filter(id=client.user.state)
        return render(request, 'campaign/account.html', {'client': client,
                                                         'country': country[0] if country else '',
                                                         'city': city[0] if city else '',
                                                         'state': state[0] if state else ''})
    else:
        return render(request, 'campaign/account.html', {})


@login_required
@is_client
def raise_ticket(request):
    """ raise tickets for issue """
    tc_cat = Ticket_Category.objects.all()
    tickets = Raised_Tickets.objects.all()
    return render(request, 'campaign/raise_ticket.html', {'tc_cat':tc_cat,'tickets':tickets})


@login_required
@is_client
def contactus(request):
    """ return contact us page """
    return render(request, 'campaign/contactus.html', {})


@login_required
@is_client
def faq(request):
    """ returs TC faq page """
    return render(request, 'campaign/faq.html', {})


@login_required
@is_client
def terms(request):
    """ returs TC terms and conditions """
    return render(request, 'campaign/terms.html', {})


@login_required
@is_client
def campaingdesc(request, camp_id):
    """ campiaign descriptions  """
    camp = Campaign.objects.get(id=camp_id)
    vendoralloc = campaign_allocation.objects.filter(campaign_id=camp_id)
    return render(request, 'campaign/campdescription.html', {'camp': camp, 'vendoralloc': vendoralloc})


def vendorprofile(request, vendor_id):
    """ return selected vendor profille """
    vendor = client_vendor.objects.filter(id=vendor_id)
    return render(request, 'vendor1/vendor_profile.html', {'vendor': vendor})


@login_required
@is_client
def view_campaign_details(request, campaign_id):
    """ campaign details """
    campaign = Campaign.objects.get(id=campaign_id)
    specification = Specification.objects.get(campaign=campaign)
    mapping = Mapping.objects.get(campaign=campaign)
    terms = Terms.objects.get(campaign=campaign)
    delivery = Delivery.objects.get(campaign=campaign)
    campaignform = CampaignForm()
    specificationform = SpecificationForm()
    mappingform = MappingForm()
    termsform = TermsForm()
    deliveryform = DeliveryForm()

    # data filler
    campaign_category = Campaign_category.objects.all()
    campaign_pacing = Campaign_pacing.objects.all()
    days = Days.objects.all()
    industry_types = industry_type.objects.all()
    job_levels = job_level.objects.all()
    job_functions = job_function.objects.all()
    countries_list = countries_list1.objects.all()
    # countries_list = countries.objects.all()
    company_sizes = company_size.objects.all()
    source_touch = source_touches.objects.all()
    level_intents = level_intent.objects.all()
    assets_all = assets.objects.all()

    data_headers = data_header.objects.all()
    delivery_methods = delivery_method.objects.all()

    context = {
        'campaign': campaign,
        'campaignform': campaignform,
        'specification': specification,
        'specificationform': specificationform,
        "mappingform": mappingform,
        "mapping": mapping,
        "termsform": termsform,
        "terms": terms,
        "deliveryform": deliveryform,
        "delivery": delivery,
        # data filler
        # set up data
        "campaign_category": campaign_category,
        "campaign_pacing": campaign_pacing,
        "days": days,
        "industry_types": industry_types,
        "job_levels": job_levels,
        "job_functions": job_functions,
        "company_sizes": company_sizes,
        "countries": countries_list,
        "source_touches": source_touch,
        "level_intent": level_intents,
        "assets": assets_all,

        "data_headers": data_headers,
        "delivery_methods": delivery_methods,
    }
    return render(request, 'campaign/view_campaign_details.html', context)


@login_required
@is_client
def client_manage_campaign(request):
    ''' return all campaigns of current client on camapign notebook  '''
    counter = Campaign.objects.filter(
        user_id=request.session['userid']).count()
    data = []
    if counter:
        campaign_details = Campaign.objects.filter(
            user_id=request.session['userid']).order_by('priority')
        return campaign_details
    else:
        return render(request, 'campaign/managecampaign.html', {})


@login_required
@is_client
def client_live_campagin(request):
    ''' return all live campaigns of current client on camapign notebook  '''
    data = client_manage_campaign(request)
    # campaign_details = Campaign.objects.filter(id=camp_id)
    # vendor_list = get_vendor_list_of_campaign(camp_id)
    return render(request, 'campaign/individual_campaign_notebook.html', {'camps': data, })


@login_required
@is_client
def client_paused_campagin(request):
    ''' return all pause campaigns of current client on camapign notebook  '''
    data = client_manage_campaign(request)
    return render(request, 'campaign/client_pause_campaign.html', {'camps': data})


@login_required
@is_client
def client_completed_campagin(request):
    ''' return all completed campaigns of current client on camapign notebook  '''
    data = client_manage_campaign(request)
    return render(request, 'campaign/client_complete_campaign.html', {'camps': data})


@login_required
@is_client
def client_pending_campaign(request):
    ''' return all pending campaigns of current client on camapign notebook  '''
    data = client_manage_campaign(request)
    return render(request, 'campaign/client_pending_campaign.html', {'camps': data})


@login_required
@is_client
def client_draft_campagin(request):
    ''' return all draft campaigns of current client on camapign notebook  '''
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        data = client_manage_campaign(request)
        return render(request, 'campaign/client_draft_campaign.html', {'camps': data})
    else:
        print(is_logged_in)
        return redirect("/logout/")


@login_required
@is_client
def client_assigned_campagin(request):
    ''' return all assigned campaigns of current client on camapign notebook  '''
    data = client_manage_campaign(request)
    return render(request, 'campaign/client_assigned_campaign.html', {'camps': data})


def timeout(request):
    print('hello timeout')
    data = {
        'msg': 'Hello timeout!',
    }
    return JsonResponse(data)



@is_client
def campaign_lifecycle(request, camp_id):
    if CampaignTrack.objects.filter(campaign_id=camp_id).exists():
        intro = CampaignTrack.objects.get(campaign_id=camp_id)

        list_for_uploaded = []
        uploaded = Lead_Uploaded_Error.objects.filter(campaign_id=camp_id, lead_upload_status=0 )
        for upload in uploaded:
            d = {}
            d['type'] = 'upload'
            d['vendor_id'] = upload.user.id
            d['vendor'] = upload.user.user_name
            t = upload.exact_time
            d['date'] = t.isoformat()
            d['lead_row_id'] = upload.id
            d['all_uploaded_leads'] = int(upload.uploaded_lead_count) + int(upload.duplicate_with_our_cnt) + int(upload.duplicate_with_vendor_cnt) + int(upload.remove_lead_header_cnt) + int(upload.remove_duplicate_lead_csv_cnt)
            d['valid_leads'] = upload.uploaded_lead_count
            d['client_percentage'] = upload.client_percentage
            d['vendor_percentage'] = upload.vendor_percentage
            list_for_uploaded.append(d)

        info = list()

        dic = {'a':intro.data_vendor_assign_count, 'b':intro.client_action_count, 'c':intro.complete_status_count}

        for i in dic:
            if dic[i] > 0:
                if i == 'a':
                    info += list(chain(eval(intro.data_vendor_assign)))
                elif i == 'b':
                    info += list(chain(eval(intro.client_action)))
                elif i == 'c':
                    info += list(chain(eval(intro.complete_status)))

        info += list(chain(list_for_uploaded))

        newlist = sorted(info, key=itemgetter('date'))


        target = int(intro.campaign.target_quantity)
        camp_all = campaign_allocation.objects.filter(campaign_id=camp_id)
        camp = Campaign.objects.get(id=camp_id)
        approve = 0

        for i in camp_all:
            if i.approve_leads is not None:
                approve += int(i.approve_leads)

        start = datetime.datetime.strptime(camp.start_date, '%Y-%m-%d')
        # start1 = datetime.date(start)
        end = datetime.datetime.strptime(camp.end_date, '%Y-%m-%d')
        # end1 = datetime.date(end)
        today = datetime.datetime.now()

        lapsed = (today-start).days
        if lapsed < 0:
            lapsed = 0
        total_days = (end-start).days
        per_day = int(target)/int(total_days)
        if lapsed > total_days:
            till_date_to_be_approved = per_day*total_days
            day_per = 100
            days = int(total_days)
        else:
            till_date_to_be_approved = per_day*lapsed
            day_per = (lapsed/total_days)*100
            days = int(lapsed)
        per = percentage(camp_id)
        if till_date_to_be_approved > int(approve):
            message = 'Warning: Campaign is lagging behind the Schedule.'
            color = 'bg-danger'
        elif till_date_to_be_approved == int(approve):
            message = 'Good! Campaign is on time.'
            color = 'bg-info'

        else:
            message = 'Great! Campaign is ahead of Schedule.'
            color = 'bg-success'

        submitted_leads = 0
        for i in camp_all:
            submitted_leads += int(i.submited_lead)

        context = {
            'intro': intro,
            'info': newlist,
            'per':per,
            'color':color,
            'message':message,
            'day_per':int(day_per),
            'days':days,
            'total':int(total_days),
            'Total_leads': int(camp.target_quantity),
            'Submitted_Leads': submitted_leads,
            'approved_leads': int(approve),
        }
        return render(request, 'campaign_life_cycle/campaign_lifecycle.html', context)

    else:
        context = {}
        return render(request, 'errors/raise404.html', context)


def reports(request):
    return render(request, 'reports/reports.html')


def leadreports(request):
    return render(request, 'reports/leadReport/leadsReport.html')

@login_required
@is_client
def custom_datafield(request,camp_id):
    header=data_header.objects.all()
    return render(request, 'custom_datafields/create_custom_datafields.html',{'header':header,'camp_id':camp_id})

@login_required
@is_client
@csrf_exempt
def save_custom_header(request):
    '''
        This Function Used for store custom header in database.
    '''
    from operator import itemgetter
    if request.method == 'POST' :
        data=ast.literal_eval(request.POST['header'])
        camp_id=request.POST['camp_id']
        base_url=settings.BASE_URL
        url=base_url+'client/add_campaign_spec/'+camp_id
        newlist = sorted(data, key=itemgetter('sort'))
        custom_header=[]
        for header in newlist:
            custom_header.append(header['user_header'])
        custom_header=','.join(custom_header)
        if Delivery.objects.filter(campaign_id=camp_id).count() > 0:
            custom=Delivery.objects.get(campaign_id=camp_id)
            custom.custom_header = custom_header
            custom.custom_header_mapping = newlist
            custom.custom_header_status = 1
            custom.save()
            return JsonResponse({'success':1,'msg':'Custom Template Created Successfully!...','url':url})
        return JsonResponse({'success':0,'msg':'Campaign Does Not Exist!...'})
    return JsonResponse({'success':0,'msg':'Without Post Method You not Access this Fuctionality.'})




@login_required
@is_client
def get_custom_header_csv(request):
    import pandas
    header=[]
    if 'file' in request.FILES:
        filehandle = request.FILES['file']
        if filehandle.name.endswith('.csv'):
            data = pandas.read_csv(filehandle,skip_blank_lines=True,na_filter=False,encoding ='latin1')
            data = data.dropna()
            print(data)
            for row in data: #get Template header
                header.append(row)
    context = {'header':header}

    html = render_to_response('custom_datafields/custom_header_csv.html', context)
    return html

@login_required
@is_client
def vendors_comparison(request):
    """
    Show list of all vendors in grid format

    Arguments:
        request {WSGIRequest} -- django.core.handlers.wsgi.WSGIRequest

    Returns:
        [type] -- [description]
    """
    final_vendors = []
    # get filter options
    all_sweet_spots = countries_list1.objects.all()
    # all_sweet_spots = countries.objects.all()
    all_marketing_methods = source_touches.objects.all()
    all_languages = language_supported.objects.all()

    vendors = client_vendor.objects.filter(user__usertype__type="vendor")

    for vendor in vendors:
        vendor_more_data = data_assesment.objects.filter(user=vendor.user).first()

        # """ Process languages """
        str_lang_ids = vendor_more_data.language_supported
        # Convert string representation of list to list
        list_lang_ids = ast.literal_eval(str_lang_ids) if str_lang_ids else []

        if list_lang_ids != []:
            lang_ids = [int(float(i)) for i in list_lang_ids]

            supported_languages = language_supported.objects.filter(
                id__in=lang_ids
                ).values_list('type', flat=True)
            if supported_languages.count() > 0:
                supported_languages_str = ', '.join(list(supported_languages))
            else:
                supported_languages_str = "--"
        else:
            supported_languages_str = "--"
        # """ Process languages the end """

        # Process lead gen capacity
        str_lead_gen_capacity = vendor_more_data.lead_gen_capacity
        dict_lead_gen_capacity = ast.literal_eval(str_lead_gen_capacity) if str_lead_gen_capacity else {}

        final_lead_gen_capacity = ""
        if dict_lead_gen_capacity != {}:
            for key, value in dict_lead_gen_capacity.items():
                lead_gen = lead_gen_capacity.objects.filter(id=key).first()
                if lead_gen:
                    source_touches_type = lead_gen.source_touches.type
                    if source_touches_type:
                        final_lead_gen_capacity += f"{source_touches_type} : {value} \n"
                    else:
                        print(f"source_touches_type is null for {lead_gen}")
        else:
            final_lead_gen_capacity = "--"
        print(final_lead_gen_capacity)
        if vendor_more_data:
            vendor_info = {
                "vendor_id": vendor.id,
                "name": vendor.user.user_name,
                "logo_url":vendor.company_logo.url if vendor.company_logo else None,
                "sweet_spot": vendor_more_data.sweet_spot,
                "sweet_spot_text": vendor_more_data.sweet_spot_text,
                "database_overall_size": vendor_more_data.database_overall_size,
                "marketing_method": vendor.marketing_method,
                "language_supported": supported_languages_str,
                "lead_gen_capacity": final_lead_gen_capacity,

            }
            final_vendors.append(vendor_info)

    context = {
        'final_vendors': final_vendors,
        'all_sweet_spots': all_sweet_spots,
        'all_marketing_methods': all_marketing_methods,
        'all_languages': all_languages,
    }
    return render(request, 'vendor1/vendors_list.html', context)
    # return HttpResponse("Hello")

# Agreement Sign


from django.conf import settings
import os
import shutil
from os import path
import datetime


def sign(request):

    img = request.POST.get("img")
    # print(img)
    imgdata = img.split(',')
    with open('dumy.txt','w+') as f:
        f.write(imgdata[1])
     # I assume you have a way of picking unique filenames
    image = 'sign1.jpg'
    with open(image, 'wb') as f:
        f.write(base64.decodebytes(open('dumy.txt', 'rb').read()))

    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawImage(image, 500, 80, width=100, height=100)
    can.save()

    datapdf = request.POST.get("pdfdata")
    datafile = request.POST.get("pdfFile")
    datafile3 = request.POST.get("pdfFile3")
    datafile4 = request.POST.get("pdfFile4")
    datafile5 = request.POST.get("pdfFile5")

    user_ = user.objects.get(id=request.session['userid'])
    queryset = user_.data_assesment_set.all()
    if queryset.count() == 1:
        for i in queryset:
            id_ = i.id
    dataurl = {
        'pdf1': datapdf,
        'pdf2': datafile,
        'pdf3': datafile3,
        'pdf4': datafile4,
        'pdf5': datafile5,
        }
    data_ = {}
    for pdf_ in dataurl:
        datafile = dataurl[pdf_]

        url = datafile.split('/')
        url.remove('')
        url.remove('media')
        data =('/').join(url)


        # urldata = os.path.join(os.path.dirname(os.path.dirname(__file__)),'data')
        urldata = os.path.join(settings.MEDIA_ROOT, data)
        # print(urldata)


        newpdf, pdf = path.split(urldata)

        now = str(datetime.datetime.now())[:19]

        newdata = urldata + now + ".pdf"

        L = newdata.split('/')
        new_pdf_path = '/'

        for i in range(len(L)):
            if i > L.index('media'):
                new_pdf_path += L[i] + '/'

        newpath = shutil.copy(urldata, newdata)
        # print(newpath)
        # url = dataurl.lstrip('/media/')
        # pdfFile = os.path.join(settings.MEDIA_ROOT,os.path.abspath(urldata)) #request.POST.get("pdfdata")
        file = newpath


        # file = '
        # file = document
        # move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open(file, 'rb'))
        c = existing_pdf.getNumPages()

        output = PdfFileWriter()
        # addatermark" (which is the new pdf) on the existing page

        for i in range(c):
            page = existing_pdf.getPage(i)
            if i == c-1:
                page.mergePage(new_pdf.getPage(0))
            output.addPage(page)

        # finally, write "output" to a real file
        outputStream = open(file, "ab")
        output.write(outputStream)
        outputStream.close()


        if pdf_ == 'pdf1':
            user_.data_assesment_set.filter(id = id_).update(nda_aggrement_path = new_pdf_path)
            data_["pdf1"] = new_pdf_path

        elif pdf_ == 'pdf2':
            user_.data_assesment_set.filter(id = id_).update(msa_aggrement_path = new_pdf_path)
            data_["pdf2"] = new_pdf_path

        elif pdf_ == 'pdf3':
            user_.data_assesment_set.filter(id = id_).update(gdpr_aggrement_path = new_pdf_path)
            data_["pdf3"] = new_pdf_path

        elif pdf_ == 'pdf4':
            user_.data_assesment_set.filter(id = id_).update(dpa_aggrement_path = new_pdf_path)
            data_["pdf4"] = new_pdf_path

        elif pdf_ == 'pdf5':
            user_.data_assesment_set.filter(id = id_).update(io_aggrement_path = new_pdf_path)
            data_["pdf5"] = new_pdf_path
            print(5)

    return JsonResponse(data_, safe=False)
    # return render(request, 'dashboard/client_boarding.html',{})

    return render(request, 'dashboard/client_boarding.html',{})


@csrf_exempt
def save_header_choice(request):
    print(request.POST)
    camp = Delivery.objects.get(campaign_id=request.POST.get('campaign_id'))
    if int(request.POST.get('tc_header')) == 1:
        camp.tc_header_status = 1
        camp.custom_header_status = 0
    else:
        camp.tc_header_status = 0
        camp.data_header = ''
    if int(request.POST.get('custom_header')) == 1:
        camp.tc_header_status = 0
        camp.custom_header_status = 1
    else:
        camp.custom_header_status = 0
        camp.custom_header == ''
        camp.custom_header_mapping = ''
    camp.save()
    data = {'msg':'updated','custom_header':camp.custom_header_status,'tc_header':camp.tc_header_status }
    return JsonResponse(data)

def noti_via_mail_page(request):

    mail = MailNotification.objects.all().order_by('-id')
    access = []
    user_instance = user.objects.get(id=request.session['userid'])
    type = usertype.objects.get(id=request.session['usertype'])
    for m in mail:
        if type in m.usertype.all():
            if user_instance in m.user.all():
                access.append({
                    'id': m.id,
                    'access': m.noti_field,
                    'value': 1,
                })
            else:
                access.append({
                    'id': m.id,
                    'access': m.noti_field,
                    'value': 0,
                })
    return render(request, 'campaign/notisettings.html', {'mail': access})

@csrf_exempt
def save_mail_choice(request):

    match = eval(request.POST.get('data'))
    print(match)
    for i in match:
        mail = MailNotification.objects.get(id=i['id'])
        if i['check'] == 1:
            mail.user.add(user.objects.get(id=i['user']))
            mail.save()
        elif i['check'] == 0:
            mail.user.remove(user.objects.get(id=i['user']))
            mail.save()
    data = {'success': 1}
    return JsonResponse(data)

@csrf_exempt
def check_io(request):
    """ io number check """
    if Campaign.objects.filter(io_number=request.GET.get('ionumber')).count() > 0:
        data = {'status': 2}
        return JsonResponse(data)
    else:
        data = {'status': 1}
        return JsonResponse(data)


def new_all_campaigns(request):
    import datetime
    result = []
    all_camp = Campaign.objects.filter(user_id=request.session['userid'], status__in=[1,2,3,4,5])

    for i in all_camp:
        target = int(i.target_quantity)
        approve = 0
        camp_alloc = campaign_allocation.objects.filter(campaign_id=i.id)

        for j in camp_alloc:
            approve += int(j.approve_leads)

        start = datetime.datetime.strptime(i.start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(i.end_date, '%Y-%m-%d')
        today = datetime.datetime.now()

        lapsed = (today-start).days
        if lapsed < 0:
            lapsed = 0

        total_days = (end-start).days
        per_day = int(target)/int(total_days)

        if lapsed > total_days:
            till_date_to_be_approved = per_day*total_days
        else:
            till_date_to_be_approved = per_day*lapsed

        if till_date_to_be_approved > int(approve):
            color = '#ef5350'
        elif till_date_to_be_approved == int(approve):
            color = '#9575cd'
        else:
            color = '#37d97feb'
        progress = percentage(camp_id=i.id)

        result.append(
            {
                'id': i.id,
                'name': i.name,
                'cpl': i.cpl,
                'leads': target,
                'progress': progress,
                'color': color,
                'status': i.status,
            }
        )

    return render(request, 'campaign/campaign_notebook_new.html', {'result': result})
