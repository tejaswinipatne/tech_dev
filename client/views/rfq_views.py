import ast
import difflib  # get ratio of string similarity
import functools
import json
import datetime
import operator
import random
from operator import itemgetter
from user.models import *
from user.models import user

from django.conf import settings
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve, reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from campaign.forms import *
from campaign.models import *
from client.decorators import *
from client.models import *
from client.utils import *
from client.views.views import *
from client_vendor.models import *
from client_vendor.models import client_vendor
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from setupdata.models import *
from setupdata.models import (cities, countries, countries1 as countries_list, industry_speciality,
                              industry_type, states, states1 as state_list)
from setupdata.serializer import Cityserializers, Stateserializers
from vendors.views.views import *
from campaign.choices import *

@login_required
@is_client
def create_rfq_campaign(request):
    # countries1 = countries.objects.all()
    countries1 = countries_list.objects.all()
    region_list=region1.objects.all()
    # region_list=region.objects.all()
    industry_types = industry_type.objects.all()
    company_sizes = company_size.objects.all()
    vendor_type=VendorType.objects.all()
    revenue_size=RevenueSize.objects.all()
    message, success, title = "", 0, "error"
    abm_status,suppression_status,lead_validation_list=0,0,[]
    if request.method == "POST":

        form = CampaignForm(request.POST)
        if form.is_valid():
            form.save()
            campaign = Campaign.objects.latest("id")

            campaign_id = campaign.id

            # converting normal datetime to iso format for passing to js function
            expiry = datetime.strptime(request.POST.get('rfq_timer'), '%Y/%m/%d %H:%M')
            expiry = datetime.isoformat(expiry)
            expiry_timer = Campaign.objects.get(id=campaign_id)
            expiry_timer.rfq_timer = expiry
            expiry_timer.save()

            # create other table with empty data
            # so we can open edit case paer page directly

            if 'abm_status' not in request.POST:
                abm_status=0
            else:
                abm_status=1

            if 'suppression_status' not in request.POST:
                suppression_status=0
            else:
                suppression_status=1



            specification=Specification.objects.create(campaign_id=campaign_id,abm_status=abm_status,suppression_status=suppression_status)
            mapping=Mapping.objects.create(campaign_id=campaign_id,industry_type=','.join(request.POST.getlist(u'industry_type')),special_instructions=request.POST.get('special_instructions'),job_title_function=request.POST.get('job_title_function'),
            country=','.join(request.POST.getlist('geo')),company_size=','.join(request.POST.getlist('company_size')),revenue_size=','.join(request.POST.getlist('revenue_size')),custom_question=int(request.POST.get('custom_question',0)))
            terms=Terms.objects.create(campaign_id=campaign_id)
            delivery=Delivery.objects.create(campaign_id=campaign_id)


            #store default lead validation in database
            lead_validation =LeadValidationComponents.objects.filter(is_default=1)

            for lead in lead_validation:
                lead_validation_list.append(lead.function_name)

            SelectedLeadValidation.objects.create(campaign=campaign,component_list=lead_validation_list)
            HeaderSpecsValidation.objects.create(campaign=campaign,company_limit=4)

            message = "Campaign Created Successfully"

            # add notification
            title = 'New RFQ Campaign Created'
            desc = "Campaign named '" + \
                str(campaign.name) + "' created successfully"
            sender_id = request.session['userid']
            receiver_id = request.session['userid']
            superadmins = user.objects.filter(usertype__id=4)
            from client.utils import noti_via_mail
            for superad in superadmins:
                noti_via_mail(superad.id, title, desc, mail_noti_new_campaign)
                RegisterNotification(sender_id, superad.id, desc,
                                     title, 1, campaign, None)
            #send request to vendors for rfq campaign

            rfq_vendor_allocation(campaign_id,sender_id)
            # add set as default data
            #objects_list = [campaign, specification, mapping, terms, delivery]
            #hook_add_campaign_data(campaign.user, objects_list)
            return redirect('client_pending_campaign')
        else:
            message += str(form.errors)
            specificationform = SpecificationForm()
            print(message)
        # return HttpResponse(message)
        context = {
            'campaignform': form,
            'region_list':region_list,
            'countries': countries1,
            "industry_types": industry_types,
            'mappingform':MappingForm(),
            "specificationform":specificationform,
            "company_sizes":company_sizes,
            "vendor_type":vendor_type,
            "revenue_size":revenue_size,
            "company_limit":4,
        }
        # send with errors
        return render(request, 'campaign/create_rfq_campaign.html', context)

    # get method
    else:
        campaignform = CampaignForm()
        specificationform = SpecificationForm()
        context = {
            'campaignform': campaignform,
            'region_list':region_list,
            'countries': countries1,
            "industry_types": industry_types,
            'mappingform':MappingForm(),
            "specificationform":specificationform,
            "company_sizes":company_sizes,
            "vendor_type":vendor_type,
            "revenue_size":revenue_size,
            "company_limit":4,
        }
        # return render(request,'campaign/createcampaign.html', context)
        return render(request, 'campaign/create_rfq_campaign.html', context)

def rfq_vendor_allocation(camp_id,userid):
    """ send request all venodr according to campaign outrich method
        RFQ Vendor Allocation
    """
    ids=get_ID_OutrichMethod(camp_id)
    title = "New RFQ Campaign Arrived"
    desc = ""
    for id in ids:
        counter = campaign_allocation.objects.filter(
            campaign_id=camp_id, client_vendor_id=id, cpl=-1, volume=-1, status=3).count()
        allocation = campaign_allocation.objects.filter(
            campaign_id=camp_id, client_vendor_id=id)
        if counter != 1 and allocation.count() != 1:
            campaign_allocation.objects.create(
                campaign_id=camp_id, client_vendor_id=id, cpl=-1, volume=-1, status=3)
        else:
            if allocation:
                allocation[0].cpl = -1
                allocation[0].volume = -1
                allocation[0].status = 3
                allocation[0].save()
        camp_alloc = campaign_allocation.objects.latest('id') if allocation[0] != campaign_allocation.objects.latest('id') else allocation[0]
        from client.utils import noti_via_mail
        noti_via_mail(id, title, desc, mail_noti_new_campaign)
        RegisterNotification(userid, id, desc, title, 2, None, camp_alloc)
    return True

def get_ID_OutrichMethod(camp_id):
    """ get all IDS according to VendorType """
    method=[]
    ids=[]
    vendor_dict={}
    camp_detail=Campaign.objects.get(id=camp_id)
    for row in camp_detail.method.all():
        method.append(row.type)

    vendortype=VendorType.objects.all()
    for type in vendortype:
        vendor_dict[type.id]=type.type

    if camp_detail.tc_vendor == 1:
        user_data=user.objects.filter(usertype=2)
        data=data_assesment.objects.filter(user__in=user_data)
        for row in data:
            vendor_type = list(map(int, ast.literal_eval(row.vendor_type)))
            if len(vendor_type) > 0:
                for vendorId in vendor_type:
                    if vendorId in vendor_dict:
                        if vendor_dict[vendorId] in method :
                            ids.append(row.user_id)
                            break
    if camp_detail.external_vendor == 1:
        vendor_list = external_vendor.objects.filter()
        for row in vendor_list:
            list1 = ast.literal_eval(row.client_id)
            ids.append(row.user_id)
    return list(set(ids))



def edit_rfq_campaign(request, campaign_id):
    """ edit_rfq_campaigns """
    countries1 = countries_list.objects.all()
    # countries1 = countries.objects.all()
    region_list=region1.objects.all()
    # region_list=region.objects.all()
    industry_types = industry_type.objects.all()
    company_sizes = company_size.objects.all()
    vendor_type=VendorType.objects.all()
    revenue_size=RevenueSize.objects.all()
    message, success, title = "", 0, "error"
    abm_status,suppression_status=0,0
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
                specification = Specification.objects.filter(campaign=campaign).first()
                mapping = Mapping.objects.filter(campaign=campaign).first()
                terms = Terms.objects.filter(campaign=campaign).first()
                delivery = Delivery.objects.filter(campaign=campaign).first()

                campaignform = CampaignForm()
                specificationform = SpecificationForm()
                all_selected_method = []
                for method in campaign.method.all():
                    all_selected_method.append(method.id)

                context = {
                    'campaign': campaign,
                    'campaignform': campaignform,
                    'region_list':region_list,
                    'countries': countries1,
                    "industry_types": industry_types,
                    'mapping':mapping,
                    "specification":specification,
                    'all_selected_method': all_selected_method,
                    "company_sizes":company_sizes,
                    "vendor_type":vendor_type,
                    "revenue_size":revenue_size,
                    'mappingform':MappingForm(),
                    "specificationform":specificationform,
                }
                return render(request, 'campaign/edit_rfq_campaign.html', context)
            else:
                print(message)
                return False
        else:
            message += "Please pass an campaign id in GET request"
    else:
        print(is_logged_in)
        return redirect("/logout/")

@is_client
def update_campaign_expiry_date(request):
    if Campaign.objects.filter(id=request.POST.get('camp_id')).update(rfq_timer=request.POST.get('date')):
        data = {'status': 1, 'message': 'date change successfully'}
    else:
        data = {'status': 2, 'message': 'date change failed'}
    return JsonResponse(data)
