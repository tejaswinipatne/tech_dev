from django.shortcuts import render, redirect
from campaign.models import *
from client.models import *
from superadmin.models import *
from setupdata.models import countries1 as countries_list
# Create your views here.

def user_dashboard(request):
    # import pdb;pdb.set_trace()
    if "is_login" in request.session:
        if request.session['is_login'] == True and (request.session['usertype'] == 6):
            client_list = []
            try:
                client = Client_User_Group.objects.filter(group_users=request.session['userid'])
                topcampaigns = campaign_allocation.objects.filter(client_vendor=client[0].group_owner).order_by('-id')[:5]
                request.session['ext_userid']=request.session['userid']
                request.session['userid']=client[0].group_owner.id
            except Exception as e:
                topcampaigns = campaign_allocation.objects.filter(client_vendor=request.session['userid']).order_by('-id')[:5]
            for data in topcampaigns:
                client = user.objects.filter(id=data.campaign.user_id)
                # country = countries.objects.filter(id=client[0].country)
                country = countries_list.objects.filter(id=client[0].country)
                client_list.append({
                    'name': client[0].user_name,
                    'email': client[0].email,
                    'contact': client[0].contact,
                    'country': country[0].name if country else '',
                })
            return render(request, 'dashboard/user_dashboard.html', {'topcampaigns': topcampaigns, 'client_list': client_list})
    return redirect('/login/')
