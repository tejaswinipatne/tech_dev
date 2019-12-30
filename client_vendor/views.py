import ast
from datetime import datetime
from user.models import *

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import resolve, reverse
from campaign.forms import CounterCPLForm
from campaign.models import *
from client.decorators import *
from client.utils import RegisterNotification, noti_via_mail
from login_register.views import *
from setupdata.models import *
from setupdata.models import countries1 as countries_list
from vendors.models import *
from vendors.views import *
from vendors.views.views import (create_custom_header, create_header,
                                 get_lead_header, getCplNLead)
from campaign.choices import *

@login_required
def vendor_portal(request):
    """ external vendor login """
    username = request.POST.get("username")
    password = request.POST.get("password")
    countrow = user.objects.filter(email=username, password=password).count()
    if countrow == 1:
        usertype = user.objects.get(email=username, password=password)
        usertype.is_login = 1
        usertype.save()
        if usertype.usertype_id == 5 or usertype.usertype_id == 2:
            request.session['username'] = username
            request.session['is_login'] = True
            request.session['usertype'] = usertype.usertype_id
            request.session['userid'] = usertype.id

            return HttpResponseRedirect('/vendor-portal/dashboard/')
        else:
            error = "your using wrong url!..."
            return render(request, 'vendor_portal/vendor-portal.html', {"error": error})

    else:
        error = "Username and password Missmatch!..."
        return render(request, 'vendor_portal/vendor-portal.html', {"error": error})

@login_required

def cdashboard(request):
    """ external vendor dashboard """
    if request.session['is_login'] == True and (request.session['usertype'] == 5 or request.session['usertype'] == 2):
        topcampaigns = campaign_allocation.objects.filter(
            client_vendor=request.session['userid']).order_by('-id')[:5]
        client_list = []
        for data in topcampaigns:
            client = user.objects.filter(id=data.campaign.user_id)
            country = countries_list.objects.filter(id=client[0].country)
            # country = countries.objects.filter(id=client[0].country)
            client_list.append({
                'name': client[0].user_name,
                'email': client[0].email,
                'contact': client[0].contact,
                'country': country[0].name if country else '',
            })
        return render(request, 'dashboard/vendor_portal_dashboard.html', {'topcampaigns': topcampaigns, 'client_list': client_list})
    else:
        return redirect('/login/')


def logout(request):
    """ logout  """
    for key in list(request.session.keys()):
        del request.session[key]
    return HttpResponseRedirect('/login/')


@login_required

def cv_manage_campaign(request):
    ''' external vendor campaign notebook '''
    counter = campaign_allocation.objects.filter(
        client_vendor_id=request.session['userid']).count()
    data = []
    CPL_form = CounterCPLForm(request.POST)
    if counter > 0:
        campaign_allocation_datails = campaign_allocation.objects.filter(
            client_vendor_id=request.session['userid'])
        for row in campaign_allocation_datails:
            campaign_details = Campaign.objects.get(id=row.campaign_id)
            data1 = getCplNLead(row, campaign_details)
            if data1['camp'] == 1:
                if campaign_details.adhoc:
                    type = 'adhoc'
                else:
                    if row.cpl == -1 or row.volume == -1:
                        type = 'RFQ'
                    else:
                        type = 'Normal'
                data.append({
                    'id': campaign_details.id,
                    'name': campaign_details.name,
                    'description': campaign_details.description,
                            'io_number': campaign_details.io_number,
                            'cpl': data1['cpl'],
                            'leads': data1['lead'],
                            'start_date': campaign_details.start_date,
                            'end_date': campaign_details.end_date,
                            'status': row.status,
                            'type': type,
                            'camp_alloc_id': row.id
                            })
        return data
    else:
        return render(request, 'vendor_portal/manage_campaign.html', )


@login_required
@is_vendor
def cv_vendor_live_campagin(request):
    """ return live campaign list """
    data = cv_manage_campaign(request)
    CPL_form = CounterCPLForm(request.POST)
    return render(request, 'vendor_portal/cv_live_campaign.html', {'camps': data, 'CPL_form': CPL_form})


@login_required
@is_vendor
def cv_vendor_paused_campagin(request):
    """ return pause campaign list """
    data = cv_manage_campaign(request)
    CPL_form = CounterCPLForm(request.POST)
    return render(request, 'vendor_portal/cv_paused_campaign.html', {'camps': data, 'CPL_form': CPL_form})


@login_required
@is_vendor
def cv_vendor_completed_campagin(request):
    """ return completed campaign list """
    data = cv_manage_campaign(request)
    CPL_form = CounterCPLForm(request.POST)
    return render(request, 'vendor_portal/cv_complete_campaign.html', {'camps': data, 'CPL_form': CPL_form})


@login_required
@is_vendor
def cv_vendor_assigned_campagin(request):
    """ return assigned campaign list """
    data = cv_manage_campaign(request)
    CPL_form = CounterCPLForm(request.POST)
    return render(request, 'vendor_portal/cv_assigned_campaign.html', {'camps': data, 'CPL_form': CPL_form})


@login_required
@is_vendor
def cv_pending_campaign(request):
    """ return pending campaign list """
    data = cv_manage_campaign(request)
    CPL_form = CounterCPLForm(request.POST)
    return render(request, 'vendor_portal/cv_pending_campaign.html', {'camps': data, 'CPL_form': CPL_form})


@login_required
@is_vendor
def cv_vendor_account(request):
    """ store vendor account details """
    userid = request.session['userid']
    marketing_method = source_touches.objects.all()
    company_size_data = company_size.objects.all()
    capacity_type = source_touches.objects.all()
    company_backgrounds = company_background.objects.all()
    pricing_flexibilitys = pricing_flexibility.objects.all()
    countrow = client_vendor.objects.filter(user_id=userid)
    if countrow:
        users = user.objects.filter(id=userid)
        clients = [item for item in client_vendor.objects.filter(
            user_id__in=users)][0]
        data_acqusitions_data = data_acqusitions.objects.filter(
            user_id_id=userid)
        built = opt_in = bought = bought_values = opt_in_values = built_values = 0
        built_display = opt_in_display = bought_display = 'none'
        for row in data_acqusitions_data:
            if row.type == 'built':
                built = 'checked'
                built_values = row.amt_millions
                built_display = 'block'
            elif row.type == 'opt_in':
                opt_in = 'checked'
                opt_in_values = row.amt_millions
                opt_in_display = 'block'
            elif row.type == 'bought':
                bought = 'checked'
                bought_values = row.amt_millions
                bought_display = 'block'

        data_acqusitions_list = {'built_display': built_display, 'opt_in_display': opt_in_display, 'bought_display': bought_display, 'built': built,
                                 'opt_in': opt_in, 'bought': bought, 'bought_values': bought_values, 'opt_in_values': opt_in_values, 'built_values': built_values}
        return render(request, 'dashboard/vendor_account.html', {'pricing_flexibilitys': pricing_flexibilitys, 'data_acqusitions_data': data_acqusitions_list, 'company_backgrounds': company_backgrounds, 'capacity_type': capacity_type, 'company_size': company_size_data, 'marketing_method': marketing_method, 'user_info': clients, 'user': users, 'client_vendor': countrow[0]})
    else:
        return render(request, 'dashboard/vendor_account.html', {'pricing_flexibilitys': pricing_flexibilitys, 'company_backgrounds': company_backgrounds, 'capacity_type': capacity_type, 'company_size': company_size_data, 'marketing_method': marketing_method})


def Counter_CPL_form(request):
    """ counter cpl on campaign allocation """
    campaign = campaign_allocation.objects.filter(id=request.POST.get('camp_all_id'))
    userid = user.objects.filter(id=campaign[0].client_vendor_id)
    if Counter_cpl.objects.filter(campaign=campaign[0].campaign,user_id=userid[0]).count() == 0:
        if request.method == "POST":
            form = CounterCPLForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.Counter_reason = request.POST.get('Counter_reason')
                post.req_cpl = request.POST.get('req_cpl') if request.POST.get('req_cpl') else None
                post.user_id = userid[0]
                post.campaign = campaign[0].campaign
                post.campaign_allocation = campaign[0]
                post.Desc = request.POST.get('desc')
                post.save()
                title="Counter Request on "+str(campaign[0].campaign.name)
                desc=request.POST.get('desc')+' -'+str(userid[0].user_name)
                client=Campaign.objects.get(id=campaign[0].campaign_id)
                # print(client.user_id)
                from client.utils import noti_via_mail
                noti_via_mail(userid[0].id, title, desc, mail_noti_rfq_cpl_req_by_superadmin)
                RegisterNotification(userid[0].id,client.user_id,desc,title, 2,campaign[0].campaign,None)
                camp=campaign_allocation.objects.get(id=request.POST.get('camp_all_id'))
                camp.counter_status=1
                camp.save()
                data = {'success': 1, }
            else:
                data = {'success': 2, }
        else:
            data = {'success': 2, }
    else:
        data={'success':3}
    return JsonResponse(data)

# chat screen data

@login_required
def campaign_chat_screen(request, camp_id):
    """ display chat screen """
    camp = Campaign.objects.get(id=camp_id)
    camp_name = Campaign.objects.all()
    campaign_list = campaign_allocation.objects.filter(
        campaign_id__in=camp_name, client_vendor_id=request.session['userid'], status__in=[1])
    return render(request, 'campaign_chat/vendor_chat_screen.html', {'sender_id': request.session['userid'], 'campaign_list': campaign_list, 'campaign': camp})

@login_required
def accpet_campaign_request(request, camp_alloc_id):
    """ accept campaign request """
    import datetime
    sender = request.session['userid']
    camp_alloc = campaign_allocation.objects.get(id=camp_alloc_id)
    camp_alloc.status = 5
    camp_alloc.save()

    camp = Campaign.objects.get(id=camp_alloc.campaign_id)
    camp.approveleads = camp.approveleads+camp_alloc.volume
    if camp.approveleads == camp.target_quantity:
        camp.status = 5

    today = datetime.datetime.strftime(datetime.datetime.now().date(),'%Y-%m-%d')
    if today == camp.start_date or today > camp.start_date:
        camp_alloc.status = 1
        camp_alloc.save()
        camp.status = 1
    camp.save()

    client = Campaign.objects.get(id=camp_alloc.campaign_id)
    superadmin = user.objects.get(usertype_id=4)

    title = "Campaign Request Accept"
    desc = request.session['username']

    sender1 = user.objects.get(id=sender)
    from client.utils import noti_via_mail
    noti_via_mail(superadmin.id, title, desc, mail_noti_vendor_action_on_camp_request)
    noti_via_mail(client.user_id, title, desc, mail_noti_vendor_action_on_camp_request)
    RegisterNotification(sender, superadmin.id, desc, title, 2,client,None)
    RegisterNotification(sender, client.user_id, desc, title, 2,client,None)
    if camp.status == 1 and camp_alloc.status == 1:
        return redirect('/vendor-portal/live-campaign/')
    else:
        return redirect('/vendor-portal/assigned-campaign/')

#external vendor give the Suggestions to client about rfq campaign
def rfqcpl(request):
    """sunmit rfq cpl and volume """
    vendor_id=request.session['userid']
    camp_alloc_id=request.POST.get('camp_alloc_id')
    t=campaign_allocation.objects.get(id=camp_alloc_id,campaign_id=request.POST.get('camp_id'),status=3,cpl=-1,client_vendor_id=vendor_id)
    if t.rfqcpl != 0 and t.rfqcpl:
        data={'success':2,'msg':'you have allready submitted cpl and volume'}
    else:
        t.rfqcpl=request.POST.get('cpl')
        t.rfqvolume=request.POST.get('volume')
        t.cpl=0
        t.save()
        data={'success':1}
        title = "RFQ Suggestions On "+str(t.campaign.name)
        desc =  str(t.client_vendor.user_name)+" Suggestions : CPL is "+str(request.POST.get('cpl'))+" & Volume is "+str(request.POST.get('volume'))

        # noti_via_mail(t.campaign.user.id, title, desc, 1)
        RegisterNotification(t.client_vendor.id, t.campaign.user.id, desc, title, 2,t.campaign,None)
    return JsonResponse(data)

#-----following code about remove campaign from pending session:kishor
@login_required
def remove_campaign_from_pending(request,camp_id,leads):
    """ remove campaign """
    vendor_id=request.session['userid']
    campaign_details=campaign_allocation.objects.get(id=camp_id)
    data=Campaign.objects.get(id=campaign_details.campaign_id)
    data.raimainingleads=data.raimainingleads+leads
    data.save()
    campaign_allocation.objects.get(id=camp_id).delete()
    vendor=user.objects.get(id=vendor_id)
    superadmin=user.objects.get(usertype_id=4)
    title="Campaign remove by vendor"
    desc=vendor.user_name
    # noti_via_mail(superadmin.id, title, desc, 1)
    RegisterNotification(vendor_id,superadmin.id,desc,title,2,data,None)
    return redirect('/vendor-portal/pending-campaign/')

@login_required
@is_vendor
def cv_campaign_notebook(request):
    """ campaign notebook """
    campaign_details = campaign_allocation.objects.filter(client_vendor=request.session['userid'])
    vendor = user.objects.filter(id=request.session['userid'])
    if campaign_details:
        return render(request,'vendor_portal/cv_campaign_notebook.html',{'camps':campaign_details,'user':vendor[0].user_name if vendor else None})
    else:
        return render(request,'vendor_portal/cv_campaign_notebook.html',{'user':vendor[0].user_name if vendor else None})

@login_required
def vendor_leadlist(request, camp_id, status):
    """ return vendor list """

    list = []
    all_header = []
    all_lead_header = []
    labels=[]
    camp_alloc = campaign_allocation.objects.filter(id=camp_id)
    Custom_question_status = Mapping.objects.filter(campaign_id=camp_alloc[0].campaign_id)[0].custom_status
    if camp_alloc.count() == 1 and status == 1:
        camp_alloc = campaign_allocation.objects.get(id=camp_id)
        header = create_custom_header(
            camp_alloc.campaign_id, request.session['userid'])
        is_upload=check_lead_uploadable(int(camp_alloc.volume),int(camp_alloc.submited_lead),int(camp_alloc.return_lead))
        data = {'camp_id': camp_alloc.campaign_id,'client_name':camp_alloc.campaign.user.user_name, 'camp_alloc_id': camp_id, 'camp_name': camp_alloc.campaign.name, 'cpl': camp_alloc.cpl,
                'lead': camp_alloc.volume,'is_upload':is_upload, 'submited_lead': camp_alloc.submited_lead, 'return_lead': camp_alloc.return_lead}
        if camp_alloc.submited_lead > 0:
            list = ast.literal_eval(camp_alloc.upload_leads)
            if len(header) == 0:
                for dict in list:
                    count=0
                    if len(dict.keys()) > count :
                        count = len(dict.keys())
                        all_header,all_lead_header=[],[]
                        for key in dict:
                            all_header.append(key)
                            all_lead_header.append(key)
                all_header = create_header(all_header)
        labels=get_lead_header(camp_alloc.campaign_id)
        labels +=join_custom_question_header(camp_alloc.campaign_id)
        if len(all_header) == 0:
            all_header=labels
        return render(request, 'campaign/leadlist.html', {'Custom_question_status':Custom_question_status,'edit_lead_header':labels,'campaigns': data, 'leadlist': list, 'all_lead_header': all_lead_header, 'all_header': all_header, 'header': header, 'status': camp_alloc.status, 'camp_id': camp_id})
    elif camp_alloc.count() == 1 and status == 4:
        camp_alloc = campaign_allocation.objects.get(id=camp_id)
        header = create_custom_header(
            camp_alloc.campaign_id, request.session['userid'])
        data = {'camp_id': camp_alloc.campaign_id, 'camp_alloc_id': camp_id, 'camp_name': camp_alloc.campaign.name, 'cpl': camp_alloc.old_cpl,
                'lead': camp_alloc.old_volume, 'submited_lead': camp_alloc.submited_lead, 'return_lead': camp_alloc.return_lead}
        if camp_alloc.upload_leads != None:
            list = ast.literal_eval(camp_alloc.upload_leads)
            if len(header) == 0:
                for dict in list:
                    count=0
                    if len(dict.keys()) > count :
                        count = len(dict.keys())
                        all_header,all_lead_header=[],[]
                        for key in dict:
                            all_header.append(key)
                            all_lead_header.append(key)
                all_header = create_header(all_header)

        labels=get_lead_header(camp_alloc.campaign_id)
        labels +=join_custom_question_header(camp_alloc.campaign_id)
        if len(all_header) == 0:
            all_header=labels
        return render(request, 'campaign/leadlist.html', {'Custom_question_status':Custom_question_status,'edit_lead_header':labels,'campaigns': data, 'leadlist': list, 'all_lead_header': all_header, 'all_header': all_header, 'header': header, 'status': status, 'camp_id': camp_id})
    return render(request, 'campaign/leadlist.html', {'Custom_question_status':Custom_question_status,'camp_id': camp_id, 'status': status})

def upload_with_rejected_lead_web(request,camp_id,camp_alloc_id):
    import datetime
    userid=request.session['userid']
    date=datetime.datetime.today().strftime('%Y-%m-%d')
    if Lead_Uploaded_Error.objects.filter(campaign_id=camp_id,user_id=userid,created_date=date,lead_upload_status=1).exists():
        lead_data=Lead_Uploaded_Error.objects.filter(campaign_id=camp_id,user_id=userid,created_date=date,lead_upload_status=1).latest('exact_time')
        leads=[]
        """
            store all leads in leads
        """

        leads=ast.literal_eval(lead_data.all_lead)
        lead_data.lead_upload_status=0
        lead_data.status=0
        lead_data.save()
        last_id_lead=get_last_id_of_lead(camp_alloc_id)
        if len(leads)>0:
            for lead in leads:
                last_id_lead +=1
                lead['id']=last_id_lead
            lead_data=upload_lead_database(leads,camp_alloc_id,userid,1)
    camp_detail=campaign_allocation.objects.get(id=camp_alloc_id)
     # return redirect('vendor_portal_leadlist', camp_id=camp_id,status=camp_detail.status)
    return HttpResponseRedirect('/vendor-portal/vendor_leadlist/'+str(camp_alloc_id)+'/'+str(camp_detail.status))


def upload_without_rejected_lead_web(request,camp_id,camp_alloc_id):
    userid=request.session['userid']
    import datetime
    date=datetime.datetime.today().strftime('%Y-%m-%d')
    lead_data={'success':1}
    if Lead_Uploaded_Error.objects.filter(campaign_id=camp_id,user_id=userid,created_date=date,lead_upload_status=1).exists():
        lead_data=Lead_Uploaded_Error.objects.filter(campaign_id=camp_id,user_id=userid,created_date=date,lead_upload_status=1).latest('exact_time')
        real_data,leads=[],[]
        """
            store all leads in leads
        """

        leads=ast.literal_eval(lead_data.all_lead)
        lead_data.lead_upload_status=0
        lead_data.status=0
        lead_data.save()

        for lead in leads:
            if lead['TC_lead_status'] == 'valid lead':
                real_data.append(lead)

        last_id_lead=get_last_id_of_lead(camp_alloc_id)
        if len(real_data)>0:
            for lead in real_data:
                last_id_lead +=1
                lead['id']=last_id_lead
            lead_data=upload_lead_database(real_data,camp_alloc_id,userid,1)
    camp_detail=campaign_allocation.objects.get(id=camp_alloc_id)
    # return redirect('vendor_portal_leadlist', camp_id=camp_id,status=camp_detail.status)
    return HttpResponseRedirect('/vendor-portal/vendor_leadlist/'+str(camp_alloc_id)+'/'+str(camp_detail.status))
