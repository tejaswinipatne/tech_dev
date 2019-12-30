from django.shortcuts import get_object_or_404,render, redirect
from django.conf import settings
from setupdata.models import countries,states,industry_type,industry_speciality,cities
from client_vendor.models import client_vendor
from user.models import user
from django.urls import resolve
import json
from vendors.views import *

from django.http import HttpResponse,JsonResponse
from setupdata.serializer import Stateserializers,Cityserializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from campaign.models import *
from setupdata.models import *
from django.views import View

from campaign.forms import *

def cdashboard(request):
    #request.session['username'] = "Nivratti"
    #request.session['is_login'] = True
    #request.session['usertype'] = 1
    #request.session['userid']=2

    if request.session['is_login']==True:
        userid=request.session['userid']
        countries1=countries.objects.all()
        industry=industry_type.objects.all()
        expert=industry_speciality.objects.all()
        countrow = client_vendor.objects.filter(user_id=userid).count()
        notifydic=notification(userid)
        if countrow == 1 :
            client_vendor_detail=client_vendor.objects.get(user_id=userid)
            userdetails=user.objects.get(id=userid)
            country=countries.objects.get(id=userdetails.country)
            state=states.objects.get(id=userdetails.state)
            industry=industry_type.objects.get(id=client_vendor_detail.industry_type_id)
            speciality=industry_speciality.objects.get(id=client_vendor_detail.industry_speciality_id)
            return render(request,'dashboard/cdashboard.html',{'speciality':speciality,'industry':industry,'state':state,'country':country,'userdetails':userdetails,'client_vendor':client_vendor_detail,'expert':expert,'countries':countries1,'industry':industry,'notifycount':notifydic["notifycount"],'notify':notifydic["notify"]})
        else:
            return render(request,'dashboard/cdashboard.html',{'expert':expert,'countries':countries1,'industry':industry,'notifycount':notifydic["notifycount"],'notify':notifydic["notify"]})

    else:
        return redirect('/login/')

def loadstates(request):
    countryid = request.POST.get('id', None)
    data=states.objects.filter(country_id=countryid)  # important: convert the QuerySet to a list object
    serializer = Stateserializers(data,many=True)
    return JsonResponse(serializer.data, safe=False)

def loadcity(request):
    stateid = request.POST.get('id', None)
    data=cities.objects.filter(state_id=stateid)  # important: convert the QuerySet to a list object
    serializer = Cityserializers(data,many=True)
    return JsonResponse(serializer.data, safe=False)
def onBording(request):
    userid=request.session['userid']
    countrow = client_vendor.objects.filter(user_id=userid).count()
    if countrow == 1 :
        t = client_vendor.objects.get(user_id=userid)
        t.primary_name=request.POST['primary_name']
        t.primary_designation=request.POST['primary_designation']
        t.primary_email=request.POST['primary_email']
        t.primary_directdial=request.POST['primary_directdial']
        t.secondary_name=request.POST['secondary_name']
        t.secondary_designation=request.POST['secondary_designation']
        t.secondary_email=request.POST['secondary_email']
        t.secondary_directdial=request.POST['secondary_directdial']
        t.website=request.POST['website']
        t.industry_speciality_id=request.POST['industry_speciality_id']
        t.industry_type_id=request.POST['industry_type_id']
        t.save()

        t = user.objects.get(id=userid)
        t.user_name = request.POST['user_name']
        t.contact = request.POST['contact']
        t.address_line1 = request.POST['address_line1']
        t.address_line2 = request.POST['address_line2']
        t.country = request.POST['country']
        t.state = request.POST['state']
        t.save()

        site_url=settings.BASE_URL
        if request.session['usertype']==1:
            pages='client'
        else:
            pages='vendor'
        data={'success':1,'site_url':site_url,'pages':pages}
        return JsonResponse(data)
    else:
        t = user.objects.get(id=userid)
        t.user_name = request.POST['user_name']
        t.contact = request.POST['contact']
        t.address_line1 = request.POST['address_line1']
        t.address_line2 = request.POST['address_line2']
        t.country = request.POST['country']
        t.state = request.POST['state']
        t.status='2'
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
        site_url=settings.BASE_URL
        if request.session['usertype']==1:
            pages='client'
        else:
            pages='vendor'
        data={'success':1,'site_url':site_url,'pages':pages}
        return JsonResponse(data)


class CreateCampaignView(View):
    def get(self, request):
        campaignform = CampaignForm()
        context = {
            'campaignform' : campaignform,
        }
        return render(request,'campaign/createcampaign.html', context)

    def post(self, request):
        #campaignform = CampaignForm(request.POST)
        form = CampaignForm(request.POST)
        if form.is_valid():
            form.save()
            last_id = Campaign.objects.latest('id')
            json_response = {
                    "success" : 1,
                    "title" : "success",
                    "message" : "Campaign Created successfully",
                    'last_id' : last_id.id,
                    }

            # create other table with empty data
            # so we can open edit case paer page directly
            specification = Specification(campaign=last_id)
            specification.save()
            mapping = Mapping(campaign=last_id)
            mapping.save()
            terms = Terms(campaign=last_id)
            terms.save()
            delivery = Delivery(campaign=last_id)
            delivery.save()
            return JsonResponse(json_response, safe='false')

        else:
            json_response = {
                "success" : 0,
                "title" : "error",
                "message" : form.errors,# "Errors on Form",
                "errors" : form.errors,
            }
            return JsonResponse(json_response)

        return JsonResponse(json_response, safe='false')


def edit_campaign(request):
    camapaign_id = 0 # init
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
    campaign = Campaign.objects.filter(id=camapaign_id)

    # other forms
    specificationform = SpecificationForm()
    specification = Specification.objects.filter(campaign = camapaign_id)

    campaign_category = campaign_category.objects.all()

    context = {
        "camapaign_id": camapaign_id,
        "title_of_panel": title_of_panel,
        "campaignform": campaignform,
        "campaign": campaign[0],

        "specificationform": specificationform,
        "specification": specification[0],
    }
    return render(request,'campaign/editcampaign.html', context)


def managecampaign(request):
    return render(request,'campaign/managecampaign.html',{})


def clonecampaign(request):
    return render(request,'campaign/clonecampaign.html',{})

def client_activity(request):
    return render(request,'campaign/client_activity.html',{})

def vendor_comparison(request):
    return render(request,'campaign/vendor-comparison.html',{})

def leads(request):
    return render(request,'campaign/leads.html',{})

def campaignreports(request):
    return render(request,'campaign/campaignreports.html',{})
def schedulereports(request):
    return render(request,'campaign/schedulereports.html',{})

def account(request):
    return render(request,'campaign/account.html',{})
def raise_ticket(request):
    return render(request,'campaign/raise_ticket.html',{})
def contactus(request):
    return render(request,'campaign/contactus.html',{})
def faq(request):
    return render(request,'campaign/faq.html',{})
def terms(request):
    return render(request,'campaign/terms.html',{})
