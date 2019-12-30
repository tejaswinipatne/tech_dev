import ast
import json
from user.models import user
from zipfile import *

from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (get_object_or_404, redirect, render,
                              render_to_response)
from django.template import loader
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.html import strip_tags
from client.models import ApiLinks
from campaign.forms import Script_Form
from campaign.models import *
from client.decorators import *
from client.models import *
from client.utils import RegisterNotification, saving_assets, update_assets,get_external_vendors, noti_via_mail
from leads.models import *
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from setupdata.models import *
from vendors.views.views import *
from superadmin.utils import collect_campaign_details
from superadmin.models import *
from campaign.choices import *

def client_invoice1(request):
    return render(request, 'invoice/client_invoice.html', {})
