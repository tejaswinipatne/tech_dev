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
from vendors.views.views import *
from form_builder.views import *
from leads.models import *
from itertools import chain
from operator import itemgetter

@login_required
@is_client
def leadreports(request):
    """
        This Function Used for load data in lead report page and display.
    """
    campaign_list=client_manage_campaign(request)
    return render(request, 'reports/leadReport/leadsReport.html',{'campaign_list':campaign_list})

def get_vendor_list_campaign(request):
    """
        This funtions used for get list of vendor according to campaign ID.
    """
    camp_id=request.POST.get('camp_id')
    vendor_list=campaign_allocation.objects.filter(campaign_id=camp_id)
    data='<option value="">Select Vendor</option>'
    for vendor in vendor_list:
        data+='<option value="'+ str(vendor.client_vendor.id) +'">'+ str(vendor.client_vendor.user_name) +'</option>'
    return HttpResponse(data)

def get_geo_list_campaign(request):
    """
        This funtions used for get list of Geo according to campaign ID.
    """    
    camp_id=request.POST.get('camp_id')
    geo_list=Mapping.objects.get(campaign_id=camp_id)
    geo_list=geo_list.country.split(',')
    data='<option value="">Select Geo</option>'
    for geo in geo_list:
        data+='<option value="'+ str(geo) +'">'+ str(geo) +'</option>'
    return HttpResponse(data)

def lead_report_table_data(request):
    """
        This funtions used for get Lead Report Data.
    """
    camp_id=int(request.POST.get('camp_id'))
    vendor_id=int(request.POST.get('vendor_id'))
    status=request.POST.get('status')
    if camp_id > 0 and vendor_id > 0 :
        data=campaign_allocation.objects.filter(campaign_id=camp_id,client_vendor_id=vendor_id,status=1)
    else:
        data=campaign_allocation.objects.filter(campaign_id=camp_id,status=1)
    lead_data=[]
    for lead in data:
        if lead.submited_lead > 0:
            lead_data +=list(ast.literal_eval(lead.upload_leads))

    return HttpResponse(data)        