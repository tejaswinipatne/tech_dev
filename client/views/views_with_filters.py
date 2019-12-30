from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from django.conf import settings
from setupdata.models import countries,countries1 as countries_list , states, states1, industry_type, industry_speciality, cities
from client_vendor.models import client_vendor
from user.models import user
from django.urls import resolve
import json
from vendors.views.views import *
from django.http import HttpResponse, JsonResponse
from setupdata.serializer import Stateserializers, Cityserializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from campaign.models import *
from setupdata.models import *
from client_vendor.models import *
from user.models import *
from django.views import View
from campaign.forms import *
from campaign.forms import *
from django.core import serializers
import difflib  # get ratio of string similarity
from operator import itemgetter
from client.models import *
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt

from client.utils import *

import random

from django.core.files.storage import FileSystemStorage

def cdashboard(request):
    if "is_login" in request.session:
        if request.session['is_login'] == True:
            vendordetail = []
            userid = request.session['userid']
            # countries1 = countries.objects.all()
            countries1 = countries_list.objects.all()
            industry = industry_type.objects.all()
            expert = industry_speciality.objects.all()
            countrow = client_vendor.objects.filter(user_id=userid).count()
            topcampaigns = Campaign.objects.filter(user_id=userid)
            for row in topcampaigns:
                campaignallocationdetails = campaign_allocation.objects.filter(
                    campaign_id=row.id, status=1)
                for row1 in campaignallocationdetails:
                    if client_vendor.objects.filter(user_id=row1.client_vendor_id).count() == 1:
                        clientvendordetail = client_vendor.objects.get(
                            user_id=row1.client_vendor_id)
                        # country = countries.objects.filter(
                        #     id=clientvendordetail.user.country)
                        country = countries_list.objects.filter(
                             id=clientvendordetail.user.country)
                        speciality = industry_speciality.objects.filter(
                            id=clientvendordetail.industry_speciality_id)
                        vendordetail.append({"vendorname": clientvendordetail.user.user_name,
                                             "website": clientvendordetail.website,
                                             "country": country[0] if country else '',
                                             "leads": clientvendordetail.lead_per_month,
                                             "speciality": speciality[0] if speciality else ''
                                             })
            if countrow == 1:
                client_vendor_detail = client_vendor.objects.get(
                    user_id=userid)
                userdetails = user.objects.get(id=userid)
                # country = countries.objects.get(id=userdetails.country)
                country = countries_list.objects.get(id=userdetails.country)
                # city=cities.objects.filter(id=userdetails.city)
                # state = states.objects.get(id=userdetails.state)
                state = states1.objects.get(id=userdetails.state)
                industry = industry_type.objects.get(
                    id=client_vendor_detail.industry_type_id)
                speciality = industry_speciality.objects.get(
                    id=client_vendor_detail.industry_speciality_id)

                return render(request, 'dashboard/cdashboard.html', {'vendordetail': vendordetail, 'topcampaigns': topcampaigns, 'speciality': speciality, 'industry': industry, 'state': state, 'country': country, 'userdetails': userdetails, 'client_vendor': client_vendor_detail, 'expert': expert, 'countries': countries1, 'industry': industry})
            else:

                return render(request, 'dashboard/cdashboard.html', {'vendordetail': vendordetail, 'expert': expert, 'countries': countries1, 'industry': industry, 'topcampaigns': topcampaigns})

        else:
            return redirect('/login/')
    else:
        return redirect('/login/')


def loadstates(request):
    countryid = request.POST.get('id', None)
    # important: convert the QuerySet to a list object
    data = states1.objects.filter(country_id=countryid)
    # data = states.objects.filter(country_id=countryid)
    serializer = Stateserializers(data, many=True)
    return JsonResponse(serializer.data, safe=False)


def loadcity(request):
    stateid = request.POST.get('id', None)
    # important: convert the QuerySet to a list object
    data = cities.objects.filter(state_id=stateid)
    serializer = Cityserializers(data, many=True)
    return JsonResponse(serializer.data, safe=False)


def onBording(request):
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


def check_is_logged_in(request):
    message, success = "", False
    if request:
        if request.session:
            if 'userid' in request.session:
                message = "User_id available in session"
                success = True
            else:
                success = False
                message = "Error ... User_id not exists inside request.session so calling /logout/ url"
        else:
            message += "Session not exists for current request"
    else:
        message = "Request is not valid"

    response = {
        "success": success,
        "message": message,
    }
    return response


def create_campaign(request):
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        """ create campaign """
        if request.method == "POST":
            message, success, title = "", 0, "error"
            print(request.POST)
            form = CampaignForm(request.POST)
            if form.is_valid():
                try:
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
                    print(message)
                    return redirect('add_campaign_spec', id=campaign_id)
                except:
                    print(form.is_valid())
                    print(form.errors)
                    pass
            else:
                print(form.errors)
                message = str(form.errors)
            #return HttpResponse(message)
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
    else:
        print(is_logged_in)
        return redirect("/logout/")


def add_campaign_spec(request, id):
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
        useAsTxtMapping = None
        volume_and_cpls = None
        txt_mapping_list = []

        if Campaign.objects.count():
            if Campaign.objects.filter(id=campaign_id):
                campaign = Campaign.objects.filter(id=campaign_id).first()
            else:
                message += "Campaign with id '" + str(campaign_id) + "' not found"
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

                specification = Specification.objects.filter(campaign=campaign).first()
                mapping = Mapping.objects.filter(campaign=campaign).first()
                terms = Terms.objects.filter(campaign=campaign).first()
                delivery = Delivery.objects.filter(campaign=campaign).first()
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
                industry_types = industry_type.objects.order_by("type")
                job_levels = job_level.objects.all()
                job_functions = job_function.objects.all()
                countries_list = countries_list.objects.all()
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
            message += "No campaign found to edit with id : \n" + str(campaign_id)
            print(message)
            return redirect("/client/create-campaign/")
    else:
        print(is_logged_in)
        return redirect("/logout/")


def change_campaign_status(request, id):
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        campaign_id = id
        campaign = Campaign.objects.filter(id=campaign_id).first()
        # change campaign status
        campaign.completion_status = "completed"
        campaign.status = 3
        campaign.save()
        # suggest vendors
        suggest_vendors(request, campaign_id)
        return redirect('client_pending_campaign')
    else:
        print(is_logged_in)
        return redirect("/logout/")


def edit_campaign(request):
    camapaign_id = 0  # init
    if 'camapaign_id' in request.POST:
        camapaign_id = request.POST.get("camapaign_id")
        request.session['camapaign_id'] = camapaign_id
    else:
        camapaign_id = request.session['camapaign_id']

    if 'title_of_panel' in request.POST:
        title_of_panel = request.POST.get("title_of_panel")
        request.session['title_of_panel'] = title_of_panel
    else:
        title_of_panel = request.session['title_of_panel']

    campaignform = CampaignForm()
    campaign = Campaign.objects.filter(id=camapaign_id).first()

    # other forms
    specificationform = SpecificationForm()
    specification = Specification.objects.filter(campaign=camapaign_id).first()

    mappingform = MappingForm()
    mapping = Mapping.objects.filter(campaign=camapaign_id).first()

    termsform = TermsForm()
    terms = Terms.objects.filter(campaign=camapaign_id).first()

    deliveryform = DeliveryForm()
    delivery = Delivery.objects.filter(campaign=camapaign_id).first()

    campaign_category = Campaign_category.objects.all()
    campaign_pacing = Campaign_pacing.objects.all()
    days = Days.objects.all()
    industry_types = industry_type.objects.all()
    job_levels = job_level.objects.all()
    job_functions = job_function.objects.all()
    # countries_list = countries.objects.all()
    countries_list = countries_list.objects.all()
    company_sizes = company_size.objects.all()

    context = {
        "camapaign_id": camapaign_id,
        "title_of_panel": title_of_panel,
        "campaignform": campaignform,
        "campaign": campaign,

        "specificationform": specificationform,
        "specification": specification,

        "mappingform": mappingform,
        "mapping": mapping,

        "termsform": termsform,
        "terms": terms,

        "deliveryform": deliveryform,
        "delivery": delivery,

        # set up data
        "campaign_category": campaign_category,
        "campaign_pacing": campaign_pacing,
        "days": days,
        "industry_types": industry_types,
        "job_levels": job_levels,
        "job_functions": job_functions,
        "company_sizes": company_sizes,
        "countries": countries_list,
    }
    return render(request, 'campaign/editcampaign.html', context)


# save records through ajax
def save_specifications(request):
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
                    campaign = Campaign.objects.filter(id=campaign_id).first()
                    if Specification.objects.count():
                        if Specification.objects.filter(campaign=campaign.id):
                            specification = Specification.objects.filter(
                                campaign=campaign.id).first()
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


# save records through ajax
def save_mapping(request):
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
                    campaign = Campaign.objects.filter(id=campaign_id).first()
                    if Mapping.objects.count():
                        if Mapping.objects.filter(campaign=campaign.id):
                            mapping = Mapping.objects.filter(campaign=campaign.id).first()
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
                    campaign = Campaign.objects.filter(id=campaign_id).first()
                    if Terms.objects.count():
                        if Terms.objects.filter(campaign=campaign.id):
                            terms = Terms.objects.filter(campaign=campaign.id).first()
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
                        terms, field_name, field_value)  # f.foo=bar
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
                    campaign = Campaign.objects.filter(id=campaign_id).first()
                    if Delivery.objects.count():
                        if Delivery.objects.filter(campaign=campaign.id):
                            delivery = Delivery.objects.filter(
                                campaign=campaign.id).first()
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
                print(delivery.__dict__)
                # check object has property with field name
                if hasattr(delivery, field_name):
                    is_attr_set = setattr(
                        delivery, field_name, field_value)  # f.foo=bar
                    delivery.save()  # this will update only

                    # campaign.completion_status = 'completed'
                    # campaign.save()

                    success = 1
                    title = 'success'
                    message = "delivery updated successfully"
                else:
                    message += "Error... delivery object has no field '" + field_name + "'"
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
    print(request.POST)
    comments = {}
    if not request.POST.get("data") == '':
        campaign_id = request.POST.get("campaign_id")  # 26
        element = request.POST.get("element")
        data = request.POST.get("data")
        campaign = Delivery.objects.filter(campaign=campaign_id)
        print(campaign[0].__dict__)
        campaign[0].comments = comments.update({element:data})
        campaign[0].save()
        # import pdb;pdb.set_trace()

    pass

def save_alternative_text(request):
    campaign_id = request.POST.get("campaign_id")  # 26
    original_txt = request.POST.get("original_txt")
    alternative_txt = request.POST.get("alternative_txt")
    print("campaign id :", campaign_id)
    print("original_txt :", original_txt)
    print("alternative_txt :", alternative_txt)

    campaign = Campaign.objects.filter(id=campaign_id).first()
    create_new_record = False

    is_table_records_exist = UseAsTxtMapping.objects.count()
    if is_table_records_exist:
        useAsTxtMapping = UseAsTxtMapping.objects.filter(
            campaign=campaign,
            original_txt=original_txt,
        ).first()
        if(useAsTxtMapping):
            if not alternative_txt:  # if empty means delete record
                useAsTxtMapping.delete()
            else:
                useAsTxtMapping.alternative_txt = alternative_txt
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


def save_volume_and_cpl(request):
    campaign_id = request.POST.get("campaign_id")  # 26
    level_of_intent = request.POST.get("level_of_intent")
    volume = request.POST.get("volume")
    cpl = request.POST.get("cpl")
    print("campaign id :", campaign_id)
    print("level_of_intent :", level_of_intent)
    print("volume :", volume)
    print("cpl :", cpl)

    campaign = Campaign.objects.filter(id=campaign_id).first()
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
    campaign_id = request.POST.get("campaign_id")  # 26
    level_of_intent = request.POST.get("level_of_intent")
    print("level_of_intent :", level_of_intent)
    print("campaign id :", campaign_id)

    campaign = Campaign.objects.filter(id=campaign_id).first()
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

@csrf_exempt
def upload_abm_company_list(request):
    """ Account based marketing File upload """
    if request.method == 'POST':
        """
        abm_company_list_file = request.FILES['abm_company_list_file']
        fs = FileSystemStorage()
        filename = fs.save(abm_company_list_file.name, abm_company_list_file)
        uploaded_file_url = fs.url(filename)
        """
        print(request.FILES)
        jsonresponse = {
            "success": 1,
            "title": request.POST,
            "message": "File uploaded successfully",
        }
        return JsonResponse(jsonresponse, safe=False)

# suggest venderos to superadmin
# def suggest_venders(request): # campaign_id
def suggest_vendors_old(camapaign_id):  # campaign_id
    # camapaign_id = 34 # testing
    campaign = Campaign.objects.filter(id=camapaign_id).first()
    if campaign:
        json_campaign = serializers.serialize('json', [campaign], indent=4)
        specification = Specification.objects.filter(campaign=campaign).first()

        mapping = Mapping.objects.filter(campaign=campaign).first()
        terms = Terms.objects.filter(campaign=campaign).first()

        delivery = Terms.objects.filter(campaign=campaign).first()

        # get client vendor
        client_vendors = client_vendor.objects.all()

        vendor_matching = []
        # iterate in client_vendors
        for vendor in client_vendors:
            # match percentage
            total_matching_per = 0  # init

            # comapny_size
            campaign_company_size = mapping.company_size
            if(campaign_company_size):
                print(campaign_company_size)
                vendor_company_size_id = vendor.company_size_id
                if(vendor_company_size_id):
                    vendor_company_size = company_size.objects.filter(
                        id=vendor_company_size_id)
                    if(vendor_company_size):
                        print(vendor_company_size)
                        matching_ratio = difflib.SequenceMatcher(
                            None, str(mapping.company_size), str(vendor_company_size)).ratio()
                        total_matching_per = total_matching_per + \
                            int(matching_ratio)


            # outreach method
            campaign_method = campaign.method
            if(campaign_method):
                vendor_method = vendor.marketing_method
                if(vendor_method_id):
                    vendor_method = source_touches.objects.filter(
                        id=vendor_company_size_id).first()
                    if(vendor_company_size):
                        print(vendor_company_size)
                        matching_ratio = difflib.SequenceMatcher(
                            None, str(mapping.company_size), str(vendor_company_size)).ratio()
                        total_matching_per = total_matching_per + \
                            int(matching_ratio)


            print("total_matching_per :" + str(total_matching_per))

            match = {
                'vendor': vendor.user.id,
                'matching_per': total_matching_per,
            }
            vendor_matching.append(match)

        sorted_vendor_matching = sorted(
            vendor_matching, key=itemgetter('matching_per'))

        # store top 3 in db
        max = 3
        for index, matching in enumerate(sorted_vendor_matching):
            if index == max:
                break

            key = "vendor"
            matching = dict(matching)
            for key in matching:
                cvendor = matching[key]
                print(cvendor)

            is_user_exists = user.objects.filter(id=cvendor)
            if(is_user_exists):
                User = user.objects.filter(id=cvendor).first()
                print(User)

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

        # return HttpResponse("Vendor matching  <pre> " + str(sorted_vendor_matching) + "</pre>")
        return True
    else:
        # return HttpResponse("Campaign is empty of id :", str(camapaign_id))
        return False


def suggest_vendors_top2(request, campaign_id):  # campaign_id
    message, success, title = "", 0, "error"
    # campaign_id = 49 # testing
    campaign = Campaign.objects.filter(id=campaign_id).first()
    if campaign:
        json_campaign = serializers.serialize('json', [campaign], indent=4)
        specification = Specification.objects.filter(campaign=campaign).first()

        mapping = Mapping.objects.filter(campaign=campaign).first()
        terms = Terms.objects.filter(campaign=campaign).first()

        delivery = Terms.objects.filter(campaign=campaign).first()

        # get client vendor
        client_vendors = client_vendor.objects.all()[:2]


        for index, vendor in enumerate(client_vendors):
            user_id = vendor.user.id
            print(user_id)
            is_user_exists = user.objects.filter(id=user_id)
            if(is_user_exists):
                User = user.objects.filter(id=user_id).first()
                print(User)

                match_vendor = match_campaign_vendor.objects.filter(
                    campaign=campaign,
                    client_vendor=User,
                ).first()
                if not match_vendor:
                    match_campaign_vendor.objects.create(
                        campaign=campaign,
                        client_vendor=User,
                        is_active=1
                    )

        return HttpResponse("completed")
        return True
    else:
        # return HttpResponse("Campaign is empty of id :", str(camapaign_id))
        return False


def suggest_vendors(request, campaign_id):  # campaign_id
    message, success, title = "", 0, "error"
    # campaign_id = 49 # testing
    campaign = Campaign.objects.filter(id=campaign_id).first()
    if campaign:
        #json_campaign = serializers.serialize('json', [campaign], indent=4)
        specification = Specification.objects.filter(campaign=campaign).first()
        mapping = Mapping.objects.filter(campaign=campaign).first()
        terms = Terms.objects.filter(campaign=campaign).first()
        delivery = Terms.objects.filter(campaign=campaign).first()

        industry_types = []
        job_levels = []
        camp_company_size_list = []
        company_sizes = []

        # get matching parameters
        camp_source_in_touches = campaign.method.all()  # all() is important for many to many field
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

        # campaign company size
        camp_company_size_str = mapping.company_size
        if camp_company_size_str:
            camp_company_size_list = camp_company_size_str.split(",")
            company_sizes = company_size.objects.filter(
                range__in=camp_company_size_list,
            )
            # print(company_sizes)
        else:
            message += "\n Company Size is null in campaign"

        # get client vendor
        client_vendors = client_vendor.objects.filter(
            Q(marketing_method__in=camp_source_in_touches) |
            Q(industry_type__in=industry_types) |
            Q(job_levels__in=job_levels) |
            Q(company_size__in=company_sizes)
            ).distinct()

        for index, vendor in enumerate(client_vendors):
            user_id = vendor.user.id
            # print(user_id)
            is_user_exists = user.objects.filter(id=user_id)
            if(is_user_exists):
                User = user.objects.filter(id=user_id).first()
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
                    campaign = Campaign.objects.filter(id=campaign_id).first()
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
                            component=is_component_valid
                        )
                        print(is_already_exist)
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
                    campaign = Campaign.objects.filter(id=campaign_id).first()
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


def ChangePwd(request):
    userid = request.session['userid']
    oldpassword = request.POST.get('opwd')
    countrow = user.objects.filter(id=userid, password=oldpassword).count()
    if countrow == 1:
        t = user.objects.filter(id=userid).first()
        t.password = request.POST.get('npwd')
        t.save()
        data = {'success': 1}
        return JsonResponse(data)
    else:
        data = {'success': 0}
        return JsonResponse(data)


def managecampaign(request):
    camps = Campaign.objects.filter(user_id=request.session['userid'])
    return render(request, 'campaign/managecampaign.html', {'camps': camps})


def clone_campaign(request, campaign_id):
    message, success, title = "", 0, "error"
    # check is logged in
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        if campaign_id:
            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.filter(id=campaign_id).first()
                else:
                    message += "Error Campaign does not exist with an id '"+ str(campaign_id) + "'"
            else:
                message = "Error.. Campaign table is empty"

            if campaign:
                specification = Specification.objects.filter(campaign=campaign).first()
                mapping = Mapping.objects.filter(campaign=campaign).first()
                terms = Terms.objects.filter(campaign=campaign).first()
                delivery = Terms.objects.filter(campaign=campaign).first()

                # clone data and create new campaign
                campaign.pk = None
                campaign.id = None
                campaign.name = campaign.name + "cloned"
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
                return redirect(reverse('edit_cloned_campaign', kwargs={'campaign_id':campaign_id}))
            else:
                print(message)
                return False
        else:
            message += "Please pass an campaign id in GET request"
    else:
        print(is_logged_in)
        return redirect("/logout/")


def edit_cloned_campaign(request, campaign_id):
    message, success, title = "", 0, "error"
    # check is logged in
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        if campaign_id:
            if Campaign.objects.count():
                if Campaign.objects.filter(id=campaign_id):
                    campaign = Campaign.objects.filter(id=campaign_id).first()
                else:
                    message += "Error Campaign does not exist with an id '"+ str(campaign_id) + "'"
            else:
                message = "Error.. Campaign table is empty"

            if campaign:
                specification = Specification.objects.filter(campaign=campaign).first()
                mapping = Mapping.objects.filter(campaign=campaign).first()
                terms = Terms.objects.filter(campaign=campaign).first()
                delivery = Terms.objects.filter(campaign=campaign).first()

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
                return render(request, 'campaign/clonecampaign_edit.html', context)
            else:
                print(message)
                return False
        else:
            message += "Please pass an campaign id in GET request"
    else:
        print(is_logged_in)
        return redirect("/logout/")


def update_c_mandatory_fields(request, campaign_id):
    campaign = Campaign.objects.filter(id=campaign_id).first()
    form = CampaignForm(request.POST, instance = campaign)
    if form.is_valid():
        form.save()
        return redirect('add_campaign_spec', id=campaign_id)
    else:
        # return redirect('clonecampaign', id=campaign_id)
        print(form.errors)
        return redirect(reverse('edit_cloned_campaign', kwargs={'campaign_id':campaign_id}))


def client_activity(request):
    return render(request, 'campaign/client_activity.html', {})


def vendor_comparison(request):
    return render(request, 'campaign/vendor-comparison.html', {})


def leads(request):
    context = {
        'days': [1, 2, 3],
    }
    # return render(request,'campaign/demo.html', context)
    return render(request, 'campaign/leads.html', {})


def campaignreports(request):
    return render(request, 'campaign/campaignreports.html', {})


def schedulereports(request):
    return render(request, 'campaign/schedulereports.html', {})


def account(request):
    userid = request.session['userid']
    countrow = client_vendor.objects.filter(user_id=userid).count()
    if countrow == 1:
        users = user.objects.filter(id=userid)
        client = [item for item in client_vendor.objects.filter(
            user_id__in=users)][0]
        # country = countries.objects.filter(id=client.user.country)
        country = countries_list.objects.filter(id=client.user.country)
        city = cities.objects.filter(id=client.user.city)
        state = states1.objects.filter(id=client.user.state)
        # state = states.objects.filter(id=client.user.state)
        return render(request, 'campaign/account.html', {'client': client,
                                                         'country': country[0] if country else '',
                                                         'city': city[0] if city else '',
                                                         'state': state[0] if state else ''})
    else:
        return render(request, 'campaign/account.html', {})


def raise_ticket(request):
    return render(request, 'campaign/raise_ticket.html', {})


def contactus(request):
    return render(request, 'campaign/contactus.html', {})


def faq(request):
    return render(request, 'campaign/faq.html', {})


def terms(request):
    return render(request, 'campaign/terms.html', {})


def campaingdesc(request, camp_id):
    camp = Campaign.objects.filter(id=camp_id).first()
    vendoralloc = campaign_allocation.objects.filter(campaign_id=camp_id).first()
    return render(request, 'campaign/campdescription.html', {'camp': camp, 'vendoralloc': vendoralloc})


def vendorprofile(request, vendor_id):
    vendor = client_vendor.objects.filter(id=vendor_id)
    return render(request, 'vendor1/vendor_profile.html', {'vendor': vendor})


def view_campaign_details(request, campaign_id):
    campaign = Campaign.objects.filter(id=campaign_id).first()
    specification = Specification.objects.filter(campaign=campaign).first()
    mapping = Mapping.objects.filter(campaign=campaign).first()
    terms = Terms.objects.filter(campaign=campaign).first()
    delivery = Delivery.objects.filter(campaign=campaign).first()
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
    # countries_list = countries.objects.all()
    countries_list = countries_list.objects.all()
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


def client_manage_campaign(request):
    counter = Campaign.objects.filter(
        user_id = request.session['userid']).count()
    data = []
    if counter:
        campaign_details = Campaign.objects.filter(user_id=request.session['userid']).order_by('priority')
        return campaign_details
    else:
        return render(request, 'campaign/managecampaign.html', {})



def client_live_campagin(request):
    data = client_manage_campaign(request)
    return render(request,'campaign/client_live_campaign.html',{'camps':data})


def client_paused_campagin(request):
    data = client_manage_campaign(request)
    return render(request,'campaign/client_pause_campaign.html',{'camps':data})


def client_completed_campagin(request):
    data = client_manage_campaign(request)
    return render(request,'campaign/client_complete_campaign.html',{'camps':data})


def client_pending_campaign(request):
    data = client_manage_campaign(request)
    return render(request,'campaign/client_pending_campaign.html',{'camps':data})


def client_draft_campagin(request):
    is_logged_in = check_is_logged_in(request)
    if(is_logged_in['success']):
        data = client_manage_campaign(request)
        return render(request,'campaign/client_draft_campaign.html',{'camps':data})
    else:
        print(is_logged_in)
        return redirect("/logout/")


def client_assigned_campagin(request):
