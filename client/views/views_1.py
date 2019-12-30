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
from django.urls import resolve, reverse
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.html import strip_tags
from client.models import ApiLinks
from campaign.forms import Script_Form
from campaign.models import *
from campaign.choices import *
from client.decorators import *
from client.models import *
from client.utils import RegisterNotification, saving_assets, update_assets,get_external_vendors,grand_child_access_call,email_domain_check, percentage, noti_via_mail
from leads.models import *
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from setupdata.models import *
from vendors.views.views import *
from superadmin.utils import collect_campaign_details
from .chat_view import get_vendor_list_of_campaign
from superadmin.models import *
from django.template import RequestContext
from client.views.views import *
@login_required
def vendor_list(request):
    ''' Return vendor list '''
    list = []
    vendor_list_details = []
    user_id = request.session['userid']
    apilinks = ApiLinks.objects.all()
    vendor_list = external_vendor.objects.filter()
    for row in vendor_list:
        list = ast.literal_eval(row.client_id)
        if user_id in list:
            user_details = user.objects.get(id=row.user_id)
            vendor_list_details.append(
                {'email': user_details.email, 'user_name': user_details.user_name})
    return render(request, 'vendor1/add_vendorlist.html', {'vendor_list': vendor_list_details, 'apilinks': apilinks})


@login_required
def campaingdesc(request, camp_id):
    """ campaign desciption includes vendors working on campaign """

    camp = Campaign.objects.get(id=camp_id)
    vendoralloc = campaign_allocation.objects.filter(campaign_id=camp_id)
    return render(request, 'campaign/campdescription.html', {'camp': camp, 'vendoralloc': vendoralloc})


@login_required
def feedback(request):
    """ feedback from client for vendor """
    # print(request.POST)
    vendor_rating = request.POST.get('rating')
    # vendor_rating = GenericRelation(Rating, related_query_name='foos')
    feedback = request.POST.get('feed')
    if feedback:
        feed_back = feedback_details.objects.create(feedback=feedback)
        feed_back.save()
    else:
        print("feedback is empty")
    return render(request, 'campaign/feedback.html', {})


@login_required
def leadlist(request, camp_id, status):
    """ return single vendor leads to the client """
    list1 = []
    all_header = []
    all_lead_header = []
    batchlist = []
    count = []
    camp_alloc = campaign_allocation.objects.filter(id=camp_id)
    global_rejected_reason = leads_rejected_reson.objects.filter(
        status=0, is_active=1)
    client_rejected_reason = leads_rejected_reson.objects.filter(
        status=1, is_active=1, user_id=request.session['userid'])
    global_rectify_reason = Leads_Rectify_Reason.objects.filter(
        status=0, is_active=1)
    client_rectify_reason = Leads_Rectify_Reason.objects.filter(
        status=1, is_active=1, user_id=request.session['userid'])
    if camp_alloc.count() == 1 and status == 1:
        camp_alloc = campaign_allocation.objects.get(id=camp_id)
        header = create_custom_header(
            camp_alloc.campaign_id, request.session['userid']) #fav lead
        data = {'campaign_id': camp_alloc.campaign_id, 'camp_status': status, 'camp_id': camp_id, 'status': status, 'camp_name': camp_alloc.campaign.name,
                'cpl': camp_alloc.cpl, 'lead': camp_alloc.volume, 'submited_lead': camp_alloc.submited_lead, 'return_lead': camp_alloc.return_lead, 'vendor_id': camp_alloc.client_vendor_id, 'user_name': user.objects.filter(id=camp_alloc.client_vendor_id)[0].user_name}
        if camp_alloc.upload_leads != None:
            list1 = ast.literal_eval(camp_alloc.upload_leads)
            batchlist = batch_list(list1)
            if len(header) == 0:
                for dict in list1:
                    count=0
                    if len(dict.keys()) > count :
                        count = len(dict.keys())
                        all_header,all_lead_header=[],[]
                        for key in dict:
                            all_header.append(key)
                            all_lead_header.append(key)
                all_header = create_header(all_header)
        labels = get_lead_header(camp_alloc.campaign_id)
        labels +=join_custom_question_header(camp_alloc.campaign_id)
        if batchlist != []:
            count = batchlist[1]
            batchlist = batchlist[0]
        if len(all_header) == 0:
            all_header = labels
        export_file_name=export_data(camp_alloc.campaign.name,camp_alloc.campaign_id,request.session['userid'],1,camp_alloc.client_vendor.password) # download  zipfile and save
        return render(request, 'campaign/client_leadlist.html', {'export_file_name':export_file_name,'approve_leads':check_approve_lead(list1),'client_rectify_reason': client_rectify_reason,
                'global_rectify_reason': global_rectify_reason, 'client_rejected_reason': client_rejected_reason, 'global_rejected_reason': global_rejected_reason, 'campaigns': data, 'leadlist': list1,
                'all_lead_header': all_lead_header, 'all_header': all_header, 'header': header, 'status': status,'batchlist':batchlist,'count':count})
    elif camp_alloc.count() == 1 and status == 4:
        camp_alloc = campaign_allocation.objects.get(id=camp_id)
        header = create_custom_header(
            camp_alloc.campaign_id, request.session['userid'])
        data = {'campaign_id': camp_alloc.campaign_id, 'camp_status': status, 'camp_id': camp_alloc.campaign_id, 'camp_alloc_id': camp_id, 'camp_name': camp_alloc.campaign.name,
                'cpl': camp_alloc.old_cpl, 'lead': camp_alloc.old_volume, 'submited_lead': camp_alloc.submited_lead, 'return_lead': camp_alloc.return_lead}
        if camp_alloc.upload_leads != None:
            list1 = ast.literal_eval(camp_alloc.upload_leads)
            if len(header) == 0:
                for dict in list1:
                    count=0
                    if len(dict.keys()) > count :
                        count = len(dict.keys())
                        all_header,all_lead_header=[],[]
                        for key in dict:
                            all_header.append(key)
                            all_lead_header.append(key)
                all_header = create_header(all_header)
        labels = get_lead_header(camp_alloc.campaign_id)
        labels +=join_custom_question_header(camp_alloc.campaign_id)
        if len(all_header) == 0:
            all_header = labels
        export_file_name=export_data(camp_alloc.campaign.name,camp_alloc.campaign_id,request.session['userid'],4,camp_alloc.client_vendor.password)
        return render(request, 'campaign/client_leadlist.html', {'export_file_name':export_file_name,'approve_leads':check_approve_lead(list1),'campaigns': data, 'leadlist': list, 'batchlist':batchlist,'count':count,'all_lead_header': all_lead_header, 'all_header': all_header, 'header': header, 'status': status_code})
    return render(request, 'campaign/client_leadlist.html', {'camp_id': camp_id, 'status': status,'approve_leads':0,})



def client_lead_list(request, camp_id, status):
    """ leadlist display when client upload leads"""

    leadlist = []
    all_header = []
    all_lead_header = []
    list=[]
    # import pdb;pdb.set_trace()
    if campaign_allocation.objects.filter(campaign_id=camp_id, status=status, client_vendor_id=request.session['userid']).count() == 1:
        camp_id = campaign_allocation.objects.get(
            campaign_id=camp_id, status=status, client_vendor_id=request.session['userid'])
        camp_id = camp_id.id
        camp_alloc = campaign_allocation.objects.filter(id=camp_id)
        if camp_alloc.count() == 1:
            camp_alloc = campaign_allocation.objects.get(id=camp_id)
            header = create_custom_header(
                camp_alloc.campaign_id, request.session['userid'])
            data = {'camp_id': camp_alloc.campaign_id, 'camp_alloc_id': camp_id, 'camp_name': camp_alloc.campaign.name, 'cpl': camp_alloc.campaign.cpl,
                    'lead': camp_alloc.campaign.target_quantity, 'submited_lead': camp_alloc.submited_lead, 'client_name':camp_alloc.campaign.user.user_name,'return_lead': camp_alloc.return_lead}
            if camp_alloc.upload_leads != None:
                list = ast.literal_eval(camp_alloc.upload_leads)
                if len(header) == 0:
                    count=0
                    for dict in list:
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
        return render(request, 'campaign/client_lead_upload.html', {'approve_leads': check_approve_lead(list), 'campaigns': data, 'leadlist': list, 'all_lead_header': all_lead_header, 'all_header': all_header, 'header': header, 'status': camp_alloc.status, 'camp_id': camp_id})
    else:
        if campaign_allocation.objects.create(campaign_id=camp_id,volume=0,cpl=0,status=status, client_vendor_id=request.session['userid']):
            camp_id = campaign_allocation.objects.get(
            campaign_id=camp_id, status=status, client_vendor_id=request.session['userid'])
            camp_id = camp_id.id
            camp_alloc = campaign_allocation.objects.filter(id=camp_id)
            if camp_alloc.count() == 1:
                camp_alloc = campaign_allocation.objects.get(id=camp_id)
                header = create_custom_header(
                    camp_alloc.campaign_id, request.session['userid'])
                data = {'camp_id': camp_alloc.campaign_id, 'camp_alloc_id': camp_id, 'camp_name': camp_alloc.campaign.name, 'cpl': camp_alloc.campaign.cpl,
                        'lead': camp_alloc.campaign.target_quantity, 'submited_lead': camp_alloc.submited_lead,'client_name':camp_alloc.campaign.user.user_name, 'return_lead': camp_alloc.return_lead}
                if camp_alloc.upload_leads != None:
                    list = ast.literal_eval(camp_alloc.upload_leads)
                    if len(header) == 0:
                        count=0
                        for dict in list:
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
    # return render(request, 'campaign/client_lead_upload.html', {'camp_id': camp_id, 'status': status})
    return render(request, 'campaign/client_lead_upload.html', {'approve_leads': check_approve_lead(list), 'campaigns': data, 'leadlist': list, 'all_lead_header': all_lead_header, 'all_header': all_header, 'header': header, 'status': camp_alloc.status, 'camp_id': camp_id})

@login_required
@is_client
def lead_error_list(request,camp_id,camp_alloc_id):
    import datetime
    userid=request.session['userid']
    date=datetime.datetime.today().strftime('%Y-%m-%d')
    lead_data={'success':1}
    if Lead_Uploaded_Error.objects.filter(campaign_id=camp_id,user_id=userid,created_date=date,lead_upload_status=1).exists():
        lead_data=Lead_Uploaded_Error.objects.filter(campaign_id=camp_id,user_id=userid,created_date=date,lead_upload_status=1).latest('exact_time')
        """
            store all leads in leads
        """

        leads=[]
        if lead_data.all_lead_count == 0:
            if lead_data.uploaded_lead_count > 0:
                leads=ast.literal_eval(lead_data.uploaded_lead)
            if lead_data.remove_duplicate_lead_csv_cnt > 0:
                leads=leads+ast.literal_eval(lead_data.remove_duplicate_lead_csv)
            if lead_data.remove_lead_header_cnt > 0:
                leads=leads+ast.literal_eval(lead_data.remove_lead_header)
            if lead_data.duplicate_with_vendor_cnt > 0:
                leads=leads+ast.literal_eval(lead_data.duplicate_with_vendor)
            if lead_data.duplicate_with_our_cnt > 0:
                leads=leads+ast.literal_eval(lead_data.duplicate_with_our)
            lead_data.all_lead=leads
            lead_data.all_lead_count=len(leads)
            lead_data.save()
        else:
            leads=ast.literal_eval(lead_data.all_lead)

        list = []
        all_header = []
        all_lead_header = []
        labels=get_lead_header(camp_id)
        labels +=join_custom_question_header(camp_id)
        if len(leads) > 0:
            for dict in leads[0]:
                all_header.append(dict)
                all_lead_header.append(dict)
        return render(request, 'campaign/lead_error_list.html', {'edit_lead_header':labels,'leadlist': leads, 'all_lead_header': all_lead_header, 'all_header': all_header,'camp_id': camp_id,'camp_alloc_id':camp_alloc_id})


def upload_with_rejected_lead_web(request,camp_id,camp_alloc_id):
    from datetime import  datetime
    userid=request.session['userid']
    date=datetime.today().strftime('%Y-%m-%d')
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
        last_batch_id = get_last_batch_id(camp_alloc_id)
        if len(leads)>0:
            for lead in leads:
                last_id_lead +=1
                lead['id']=last_id_lead
                lead['batch']=last_batch_id
            lead_data=upload_lead_database(leads,camp_alloc_id,userid,1,last_batch_id)
    camp_detail=campaign_allocation.objects.get(id=camp_alloc_id)
    return redirect('client_lead_list', camp_id=camp_id,status=camp_detail.status)

@login_required
@is_client
def upload_without_rejected_lead_web(request,camp_id,camp_alloc_id):
    from datetime import  datetime
    userid=request.session['userid']

    date=datetime.today().strftime('%Y-%m-%d')
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
            print(leads)
            if lead['TC_lead_status'] == 'valid lead':
                real_data.append(lead)

        last_id_lead=get_last_id_of_lead(camp_alloc_id)
        last_batch_id = get_last_batch_id(camp_alloc_id)
        if len(real_data)>0:
            for lead in real_data:
                last_id_lead +=1
                lead['id']=last_id_lead
                lead['batch']=last_batch_id
            lead_data=upload_lead_database(real_data,camp_alloc_id,userid,1,last_batch_id)
    camp_detail=campaign_allocation.objects.get(id=camp_alloc_id)
    return redirect('client_lead_list', camp_id=camp_id,status=camp_detail.status)


#upload excel lead data into database

def upload_lead_database(dict, camp_alloc_id, userid,is_upload,last_batch_id):
    """ Upload excel lead data into database """

    upload_lead_cnt=len(dict)
    data = campaign_allocation.objects.get(id=camp_alloc_id, client_vendor_id=userid)

    """
        IF user select upload with reject lead or with rejected lead
        Only that time upload data
    """
    if is_upload == 1:
        if data.submited_lead == 0:
            data.upload_leads = dict
            data.submited_lead = len(dict)
            data.batch_count = last_batch_id
            data.save()
        else:
            old_data = ast.literal_eval(data.upload_leads)
            data.upload_leads = old_data + dict
            data.submited_lead = len(old_data + dict)
            data.batch_count = last_batch_id
            data.save()
    if upload_lead_cnt > 0:
        return {'success':1,'upload_lead_cnt':upload_lead_cnt}
    return {'success':1,'upload_lead_cnt':0}

#get last id of lead data campaign
def get_last_id_of_lead(camp_alloc_id):
    """ Get last id of lead """
    camp_desc=campaign_allocation.objects.get(id=camp_alloc_id)
    if camp_desc.upload_leads:
        lead_desc=ast.literal_eval(camp_desc.upload_leads)
        if len(lead_desc) > 0:
            return lead_desc[-1]['id']
        return 0
    else:
        return 1

def get_last_batch_id(camp_alloc_id):
    '''get batch id for upload'''
    camp_desc=campaign_allocation.objects.get(id=camp_alloc_id)
    if camp_desc.batch_count > 0:
        return camp_desc.batch_count + 1
    return 1

# check approvr leads
def check_approve_lead(list):
    """ approve leads  """
    approve = 0
    for dict in list:
        if dict['status'] == 1:
            approve += 1
    return approve


def get_lead_header(camp_id):
    """ returs leads orginal headers """
    camp_lead=Delivery.objects.get(campaign_id=camp_id)
    if camp_lead.custom_header_status == 0 :
        labels = camp_lead.data_header
        labels = list(labels.split(','))
    else:
        labels = camp_lead.custom_header
        labels = labels.split(',')
    return labels

#lead data export into excel
def export_data(camp_name,camp_id,vendor_id,status,password):
    import unicodecsv as csv
    import os
    import shutil
    from os import path
    from shutil import make_archive
    from openpyxl import Workbook
    toCSV = []
    toCSV = convert_data_list(camp_id, vendor_id, status)
    if len(toCSV) > 0:
        if type(toCSV[0]) is dict:
            keys = toCSV[0].keys()
            with open('export_approve_leads.csv', 'wb') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(toCSV)
            with open('export_approve_leads.csv', 'rb') as myfile:

                response = HttpResponse(myfile, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=export_approve_leads.csv'

                src = path.realpath("export_approve_leads.csv")
                root_dir, tail = path.split(src)

                file_name='/static/'+str(camp_name)+'_'+str(camp_id)+'_'+str(vendor_id)+'.zip'

                import pyminizip
                compression_level = 5 # 1-9
                pyminizip.compress(root_dir+'/export_approve_leads.csv',None,root_dir+file_name, password, compression_level)
                return file_name


# convert lead data as per header lead
def convert_data_list(camp_id, vendor_id, status):
    """ convert lead data as per header lead """
    vendor_lead_list = []
    data = []
    lead_dict = {}
    labels = get_lead_header(camp_id)
    labels +=join_custom_question_header(camp_id)

    # status=1 means all vendors leads and 2 means particoluar vendor leads
    if status == 1:
        camp_lead_data = campaign_allocation.objects.filter(
            campaign_id=camp_id, status=1)
        for row in camp_lead_data:
            if row.submited_lead > 0:
                vendor_lead_list += ast.literal_eval(row.upload_leads)

        if len(vendor_lead_list) > 0:
            for dict in vendor_lead_list:
                if dict['status'] >=0 :
                    for key in dict:
                        if key in labels:
                            lead_dict.update({key: dict[key]})
                    data.append(lead_dict)
                    lead_dict = {}
            return data
        else:
            print("hiielse")
            return labels
    else:
        camp_lead_data = campaign_allocation.objects.filter(
            campaign_id=camp_id, status=1, client_vendor_id=vendor_id)
        for row in camp_lead_data:
            if row.submited_lead > 0:
                vendor_lead_list += ast.literal_eval(row.upload_leads)

        if len(vendor_lead_list) > 0:
            for dict in vendor_lead_list:
                if dict['status'] == 1:
                    for key in dict:
                        if key in labels:
                            lead_dict.update({key: dict[key]})
                    data.append(lead_dict)
                    lead_dict = {}
            return data
        else:
            return labels


def create_header(dict):
    """ creates header list """
    list = []
    for row in dict:
        if row == 'reason':
            list.append('Status Code')
        else:
            list.append(row)
    return list


def create_custom_header(camp_id, userid):
    """ create custome header list """
    fav_lead = []
    fav_lead_details = favorite_leads_header.objects.filter(
        campaign_id=camp_id, user_id=userid)
    if fav_lead_details.count() == 1:
        fav_lead_details = favorite_leads_header.objects.get(
            campaign_id=camp_id, user_id=userid)
        return ast.literal_eval(fav_lead_details.header)
    else:
        return fav_lead


def lead_approve(request):
    """ approve selected lead """
    return_lead = 0
    results = [int(i) for i in request.POST.getlist('id[]')]
    status = request.POST.get('status')
    camp_id = request.POST.get('camp_id')
    camp_alloc = campaign_allocation.objects.get(
        id=camp_id, status=status)
    list = ast.literal_eval(camp_alloc.upload_leads)
    for dict in list:
        if dict['id'] in results:
            dict['status'] = 1
        elif dict['status'] == 2:
            return_lead += 1
    camp_alloc.upload_leads = list
    camp_alloc.return_lead = return_lead
    camp_alloc.approve_leads = check_approve_lead(list)
    camp_alloc.save()
    action_on_camp_by_client(1, results, camp_alloc.campaign.id, camp_alloc.client_vendor.id, camp_alloc.client_vendor.user_name)
    data = {'success': 1, 'msg': 'Leads Approved Successfully!..'}
    return JsonResponse(data)


def lead_rejected(request):
    """ reject selected lead """
    return_lead = 0
    results = [int(i) for i in request.POST.getlist('id[]')]
    status = request.POST.get('status')
    camp_id = request.POST.get('camp_id')
    Reason = request.POST.get('Reason')
    lead_desc = request.POST.get('lead_desc')
    camp_alloc = campaign_allocation.objects.get(
        id=camp_id)
    list = ast.literal_eval(camp_alloc.upload_leads)
    for dict in list:
        if dict['id'] in results:
            dict['status'] = int(request.POST.get('lead_status'))
            dict['reason'] = Reason
            dict['lead_desc'] = lead_desc
        if dict['status'] == 2:
            return_lead += 1
    camp_alloc.upload_leads = list
    camp_alloc.return_lead = return_lead
    camp_alloc.save()
    action_on_camp_by_client(2, results, camp_alloc.campaign.id, camp_alloc.client_vendor.id, camp_alloc.client_vendor.user_name, Reason, lead_desc)
    data = {'success': 1, 'msg': 'Leads Rejected Successfully!..'}
    # send notification when rectify lead
    title = 'Lead Reject'
    desc = str(len(results))+'More leads Rejected on ' + \
        str(camp_alloc.campaign.name)
    from client.utils import noti_via_mail
    noti_via_mail(camp_alloc.client_vendor_id, title, desc, mail_noti_client_action_on_leads)
    RegisterNotification(
        request.session['userid'], camp_alloc.client_vendor_id, desc, title, 1, None, camp_alloc)
    return JsonResponse(data)


def lead_rectify(request):
    """ rectify selected leads """
    results = [int(i) for i in request.POST.getlist('id[]')]
    status = request.POST.get('status')
    camp_id = request.POST.get('camp_id')
    Reason = request.POST.get('Reason')
    lead_desc = request.POST.get('lead_desc')
    camp_alloc = campaign_allocation.objects.get(
        id=camp_id)
    list = ast.literal_eval(camp_alloc.upload_leads)
    for dict in list:
        if dict['id'] in results:
            dict['status'] = 3
            dict['reason'] = Reason
            dict['lead_desc'] = lead_desc
            batch = dict['batch']
    camp_alloc.upload_leads = list
    camp_alloc.save()
    action_on_camp_by_client(3, results, camp_alloc.campaign.id, camp_alloc.client_vendor.id, camp_alloc.client_vendor.user_name, Reason, lead_desc)
    data = {'success': 1, 'msg': 'Leads Rectify Successfully!..'}

    # send notification when rectify lead
    title = 'Lead Rectify'

    desc = f'#{str(len(results))} More leads Rectify in batch-{batch} on {str(camp_alloc.campaign.name)}.'


    desc = str(len(results))+' More leads Rectify on ' + \
        str(camp_alloc.campaign.name)
    from client.utils import noti_via_mail
    noti_via_mail(camp_alloc.client_vendor_id, title, desc, mail_noti_client_action_on_leads)

    RegisterNotification(
        request.session['userid'], camp_alloc.client_vendor_id, desc, title, 1, None, camp_alloc)
    return JsonResponse(data)


@login_required
def campaign_vendor_list(request, camp_id):
    """ campaign vendor list  """
    users = user.objects.filter(usertype_id=2)
    clients = match_campaign_vendor.objects.filter(client_vendor_id__in=users, campaign_id=camp_id)
    return render(request, 'vendor1/vendorlist.html', {'clients': clients, 'camp': camp_id})


def Suggest(request):
    """ suggest vendor list  """
    results = [int(i) for i in request.POST.getlist('id[]')]
    data = {'success': 0}
    for id in results:
        campaign_id = request.POST.get('camp_id', None)
        vendor_id = id
        counter = campaign_allocation.objects.filter(
            campaign_id=campaign_id, client_vendor_id=vendor_id, status=0, suggest_status=1).count()
        if counter == 1:
            t = campaign_allocation.objects.get(
                campaign_id=campaign_id, client_vendor_id=vendor_id)
            t.status = 0
            t.suggest_status = 1
            t.save()
            data = {'success': 1, 'msg': "Vendor Suggest Successfully!.."}
        else:
            campaign_allocation.objects.create(
                status=0, client_vendor_id=vendor_id, campaign_id=campaign_id, suggest_status=1)
            data = {'success': 1, 'msg': "Vendor Suggest Successfully!.."}

    return JsonResponse(data)


def create_demo_campaign(request):
    return render(request, 'campaign/create_demo_campaign.html', {})

def password_check(passwd):
    SpecialSym =['$', '@', '#', '%', '^', '&', '*', '+', '-', '!']
    if len(passwd) < 8:
        return False

    if not any(char.isdigit() for char in passwd):
        return False

    if not any(char.isupper() for char in passwd):
        return False

    if not any(char.islower() for char in passwd):
        return False

    if not any(char in SpecialSym for char in passwd):
        return False

    else:
        return True

def add_venodr(request):
    """ add vendors """
    status = 0
    email = str(request.POST.get('email')).lower()
    username = str(request.POST.get('username'))
    pwd = request.POST.get('pwd')
    user_id = request.session['userid']
    site_url = settings.BASE_URL
    email_check = email_domain_check(email)
    client = user.objects.get(id=user_id).user_name
    t = password_check(pwd)
    if t is True:
        if email_check['status'] == 1:
            if user.objects.filter(email=email).count() == 1:
                user_details = user.objects.get(email=email)
                data = add_external_vendor(user_details.id, user_id)
            else:
                data = add_external_user_vendor(user_id, email, pwd, username)
            subject = "Invitation From Techconnetr"
            html_message = render_to_string('email_templates/external_user_register_template.html', {
                                            'username': email,'client': client,'site_url': site_url, 'password': pwd})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to_list = [email]
            if send_mail(subject, plain_message, from_email, to_list, fail_silently=True,html_message=html_message):
                print('sent mail')
        else:
            data = email_check
        print(data)
        return JsonResponse(data)
    else:
        data = {'status':0,'msg':"Password should contain characters, numbers and special symbols!"}
        return JsonResponse(data)




def add_external_vendor(user_id, client_id):
    """ add TC vendor by superadmin """

    list = []
    if external_vendor.objects.count() > 0:
        if external_vendor.objects.filter(user_id=user_id).count() == 1:
            client_vendor_data = external_vendor.objects.get(user_id=user_id)
            list = ast.literal_eval(client_vendor_data.client_id)
            if client_id in list:
                return {'status': 0, 'msg': 'you already added this vendor', 'user_id': user_id}
            else:
                list.append(client_id)
                client_vendor_data.client_id = list
                client_vendor_data.save()
                return {'status': 2, 'msg': 'This vendor already added by another vendor', 'user_id': user_id}
        else:
            list.append(client_id)
            external_vendor.objects.create(client_id=list, user_id=user_id)
            return {'status': 1, 'msg': ' vendor added Successfully!...', 'user_id': user_id}
    else:
        list.append(client_id)
        external_vendor.objects.create(client_id=list, user_id=user_id)
        return {'status': 1, 'msg': ' vendor added Successfully!...', 'user_id': user_id}


def add_external_user_vendor(client_id, email, pwd, username):
    """ add vendor by client """
    user.objects.create(email=email, user_name=username,password=pwd, is_active=1, usertype_id=5)
    user_id = user.objects.latest('id')
    return add_external_vendor(user_id.id, client_id)



@login_required
def vendor_allocation(request, camp_id):
    """ vendor allocation by to client to his external vendor """
    campaign_details = Campaign.objects.get(id=camp_id)
    list = []
    vendor_list_details = []
    username = campaign_details.user.user_name
    data = {
        'username': username,
        'userid': campaign_details.user_id,
        'cpl': campaign_details.cpl,
        'targat_quantity': campaign_details.target_quantity,
        'ramaining_quantity': campaign_details.raimainingleads,
        'approveleads': campaign_details.approveleads,
    }
    user_id = request.session['userid']
    vendor_list = external_vendor.objects.filter()
    for row in vendor_list:
        list = ast.literal_eval(row.client_id)
        if user_id in list:
            print(row.user_id)
            if campaign_allocation.objects.filter(client_vendor_id=row.user_id, cpl__gte=0, volume__gte=0, campaign_id=camp_id).count() != 1:
                user_details = user.objects.get(id=row.user_id)
                vendor_list_details.append({
                    'email': user_details.email,
                    'checked': '0',
                    'display': 'none',
                    'vendor_name': user_details.email,
                    'vendor_id': row.user_id,
                    'camp_id': camp_id,
                })
    return render(request, 'campaign/client_vendor_allocation.html', {'campdata': data, 'vendor_data': vendor_list_details})


@login_required
def insert_lead(request, camp_id, camp_alloc_id):
    """ display lead header to upload indivdual lead """
    labels = get_lead_header(camp_id)
    labels +=join_custom_question_header(camp_id)
    camp_alloc = campaign_allocation.objects.get(id=camp_alloc_id)
    return render(request, 'campaign/addlead.html', {'lead_header': labels, 'camp_id': camp_id, 'camp_alloc_id': camp_alloc_id,'camp_alloc':camp_alloc})


# following code is submit asset data in to database kishor

def asset_submit(request):
    """ to submit assets for campaign """
    if request.POST:
        t = Terms.objects.filter(campaign=request.POST.get('campaign'))
        if t:
            t[0].assets_name = request.POST.get('assets_name')
            t[0].sponsers = request.POST.get('sponsers')
            t[0].asset_distributor = request.POST.get('asset_distributor')
            t[0].add_assetslink = request.POST.get('add_assetslink')
            if t[0].assets_type:
                t[0].assets_type = update_assets(
                    request, t[0].assets, ast.literal_eval(t[0].assets_type))
            else:
                file_dict = saving_assets(request, t[0].assets)
                t[0].assets_type = file_dict
            t[0].save()
            data = {'status_code': 1}
            return JsonResponse(data)
        else:
            data = {'status_code': 2, 'message': 'Camapign Not Found'}
            return JsonResponse(data)
    data = {'status_code': 2, 'message': 'Please Fill the detail'}
    return JsonResponse(data)


def remove_asset(request):
    """ remove links from campaign assets"""
    term_data = Terms.objects.get(campaign_id=request.POST.get('camp_id'))
    asset_type = request.POST.get('asset_type')
    data = ast.literal_eval(term_data.assets_type)
    if data:
        if data[asset_type]['link']:
            if request.POST.get('asset') in data[asset_type]['link']:
                data[asset_type]['link'].remove(request.POST.get('asset'))
                new_list = data[asset_type]['link']
                if len(new_list) > 0:
                    data[asset_type].update({'link': new_list})
                    term_data.assets_type = data
                    term_data.save()
                else:
                    if bool(data[asset_type]):
                        data[asset_type].pop('link',None)
                        if not bool(data[asset_type]):
                            data.pop(asset_type,None)
                    else:
                        data.pop(asset_type,None)
                    term_data.assets_type = data
                    term_data.save()
                data = {'status_code': 1, 'message': 'asset removed'}
            else:
                data = {'status_code': 1, 'message': 'asset remove error'}
    return JsonResponse(data)


def remove_file_asset(request):
    """ remove files from campaign assets"""
    term_data = Terms.objects.get(campaign_id=request.POST.get('camp_id'))
    asset_type = request.POST.get('asset_type')
    data = ast.literal_eval(term_data.assets_type)
    if data:
        if len(data[asset_type]['files']) > 0:
            for file_dict in data[asset_type]['files']:
                if request.POST.get('asset') == file_dict['url']:
                    data[asset_type]['files'].remove(file_dict)
                    new_list = data[asset_type]['files']
                    if len(new_list) > 0:
                        data[asset_type].update({'files': new_list})
                        term_data.assets_type = data
                        term_data.save()
                    else:
                        if bool(data[asset_type]):
                            data[asset_type].pop('files',None)
                            if not bool(data[asset_type]):
                                data.pop(asset_type,None)
                        else:
                            data.pop(asset_type,None)
                        term_data.assets_type = data
                        term_data.save()
            data = {'status_code': 1, 'message': 'asset removed'}
        else:
            data = {'status_code': 1, 'message': 'asset remove error'}
    return JsonResponse(data)


def script_submit(request):
    """ to submit scripts for campaign """
    camp_id = Scripts.objects.get_or_create(
        campaign_id=request.POST.get('campaign'))
    if request.FILES:
        myfile = request.FILES['client_script']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        camp_id[0].client_script = filename
        camp_id[0].save()
        data = {'status': 1}
        return JsonResponse(data)
    data = {'status': 2}
    return JsonResponse(data)


def vendor_script_submit(request):
    """ upload vendor scripts """
    camp_id = Scripts.objects.get_or_create(
        campaign_id=request.POST.get('campaign'))
    if request.FILES:
        myfile = request.FILES['client_script']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        camp_id[0].client_script = filename
        camp_id[0].save()
        data = {'status': 1}
        return JsonResponse(data)
    data = {'status': 2}
    return JsonResponse(data)


def get_asset_specs(request):
    """ to fetch uploaded assets """
    asset = Terms.objects.get(campaign_id=request.POST.get('id'))
    data = {
        'name':asset.campaign.name,
        'assets_name': asset.assets_name if asset.assets_name else 'None',
        'assets': asset.assets if asset.assets else 'None',
        'sponsers': asset.sponsers if asset.sponsers else 'None',
        'assets_type': ast.literal_eval(asset.assets_type) if asset.assets_type else 'None',
        'asset_distributor': asset.asset_distributor if asset.asset_distributor else 'None',
        'add_assetslink': asset.add_assetslink if asset.add_assetslink else 'None',
    }
    return JsonResponse(data)


def get_scripts(request):
    """ return uploaded scripts """
    term_data = Scripts.objects.filter(campaign_id=request.POST.get('id'))
    data = {}
    if term_data:
        data = {
            'url': term_data[0].client_script.url if term_data[0].client_script.url else 'None', }
    print(data)
    return JsonResponse(data)


def get_agreements(request):
    pass


@login_required
def campaign_notebook(request):
    """ return all campaigns to the campaign notebook """
    counter = Campaign.objects.filter(
        user_id=request.session['userid']).count()
    data = []
    if counter > 0:
        campaign_details = Campaign.objects.filter(
            user_id=request.session['userid'])
        pending_camp_count = Campaign.objects.filter(
            user_id=request.session['userid'], status=3).count()
        live_camp_count = Campaign.objects.filter(
            user_id=request.session['userid'], status=1).count()
        assigned_camp_count = Campaign.objects.filter(
            user_id=request.session['userid'], status=5).count()
        complete_camp_count = Campaign.objects.filter(
            user_id=request.session['userid'], status=4).count()
        return render(request, 'campaign/campaign_notebook.html', {'camps': campaign_details, 'pending_count': pending_camp_count,
                                                                   'live_count': live_camp_count, 'assigned_count': assigned_camp_count, 'complete_count': complete_camp_count})
    else:
        return render(request, 'campaign/campaign_notebook.html', {})


def get_camp_data(request):

    """ return campaign data to display on campaign notebook """
    camp_details = Campaign.objects.get(id=request.POST.get('id'))
    mapping = Mapping.objects.get(campaign_id=request.POST.get('id'))
    aggrement = data_assesment.objects.get(user_id=request.session['userid'])
    data = {
        'name': camp_details.name,
        'cpl': camp_details.cpl,
        'volume': camp_details.target_quantity,
        'camp_io':camp_details.io_number,
        'rfq': camp_details.rfq,
        'status': camp_details.status,
        'rfq_timer': camp_details.rfq_timer,
        'start_date': camp_details.start_date,
        'end_date': camp_details.end_date,
        'desc': camp_details.description,
        'camp_id': request.POST.get('id'),
        'sender_id': request.session['userid'],
        'special_instr': mapping.special_instructions,
        'nda': aggrement.nda_aggrement,
        'msa': aggrement.msa_aggrement,
        'gdpr': aggrement.gdpr_aggrement,
        'dpa': aggrement.dpa_aggrement,
        'io': aggrement.io_aggrement,
    }
    return JsonResponse(data)


def get_vendor_list(request):
    """ return assigned vendor list """
    camp_details = Campaign.objects.get(id=request.POST.get('camp_id'))
    vendor_list = campaign_allocation.objects.filter(
        campaign_id=camp_details.id, status__in=[1,4,5]).distinct()
    vendor_id = []
    vendor_data = []
    for vendor in vendor_list:
        if vendor.client_vendor_id not in vendor_id:
            vendor_id.append(vendor.client_vendor_id)
            vendor_data.append({
                'id': vendor.client_vendor_id,
                'vendor_name': vendor.client_vendor.user_name
            })
    return JsonResponse(vendor_data, safe=False)


@login_required
def all_lead_display(request, camp_id):
    """ return all uploaded leads for a campaign """
    all_list = []
    all_header = []
    all_lead_header = []
    submitLead = 0
    rejectedLead = 0
    camp_alloc = campaign_allocation.objects.filter(campaign_id=camp_id)
    if camp_alloc.count() > 0:
        header = create_custom_header(camp_id, request.session['userid'])
        campaign_details = Campaign.objects.get(id=camp_id)
        for row in camp_alloc:
            submitLead = submitLead + int(row.submited_lead)
            rejectedLead = rejectedLead+int(row.return_lead)
            data = {'camp_id': camp_id, 'camp_alloc_id': camp_id, 'camp_name': campaign_details.name, 'cpl': campaign_details.cpl,
                    'lead': campaign_details.target_quantity, 'submited_lead': submitLead, 'return_lead': rejectedLead}
            if row.upload_leads != None:
                list = ast.literal_eval(row.upload_leads)
                if len(header) == 0:
                    for dict in list[0]:
                        all_header.append(dict)
                        all_lead_header.append(dict)
                    all_header = create_header(all_header)
                else:
                    all_header = header
                    for dict in list[0]:
                        all_lead_header.append(dict)
                    all_header = create_header(all_header)
                all_list.extend(list)

    return render(request, 'campaign/client_lead_upload.html', {'campaigns': data, 'leadlist': all_list, 'all_lead_header': all_lead_header, 'all_header': all_header, 'header': header, 'camp_id': camp_id})


def get_rfq_cpl(request):
    """ return rfq and cpl sent by superadmin """
    campaign = Campaign_rfq.objects.get(campaign_id=request.POST.get('camp_id'))
    data = {'cpl': campaign.cpl, 'volume': campaign.volume}
    return JsonResponse(data)


def update_status_rfq(request):
    """ process actions on rfq resopnce """
    camp_id = request.POST.get('camp_id')
    cpl = request.POST.get('cpl')
    volume = request.POST.get('volume')
    choose = request.POST.get('choose')
    user_id = request.session['userid']
    superadmin = user.objects.get(usertype_id=4)
    if choose == '1':
        accept_rfq_cpl_by_client(camp_id, cpl, volume, user_id, superadmin.id)
    elif choose == '2':
        remark = request.POST.get('remark')
        counter_rfq_cpl_by_client(
            camp_id, cpl, volume, user_id, remark, superadmin.id)
    elif choose == '3':
        rejected_rfq_cpl_by_client(
            camp_id, cpl, volume, user_id, superadmin.id)
    data = {'success': 1, 'msg': 'Action Submitted Successfully!...'}
    return JsonResponse(data)


def accept_rfq_cpl_by_client(camp_id, cpl, volume, user_id, superadmin_id):
    """ accept cpl and volume sent form superadmin """

    # changes for rfq datatable
    campaign = Campaign_rfq.objects.get(campaign_id=camp_id)
    campaign.status = 3
    campaign.save()

    campaign = Campaign.objects.get(id=camp_id)
    name = campaign.name
    campaign.cpl = cpl
    campaign.target_quantity = volume
    campaign.raimainingleads = volume
    campaign.rfq_status = 1
    campaign.save()
    title = 'Accept RFQ CPL'
    desc = 'Accept RFQ CPL Request by client on '+str(name)
    # noti_via_mail(superadmin_id, title, desc, 1)
    RegisterNotification(user_id, superadmin_id, desc,
                         title, 1, campaign, None)
    return True


def counter_rfq_cpl_by_client(camp_id, cpl, volume, user_id, remark, superadmin_id):
    """ counter cpl or volume to superadmin """
    campaign = Campaign_rfq.objects.get(campaign_id=camp_id)
    name = campaign.campaign.name
    campaign.old_cpl = campaign.cpl
    campaign.old_volume = campaign.volume
    campaign.cpl = cpl
    campaign.volume = volume
    campaign.remark = remark
    campaign.status = 2
    campaign.save()
    campaign = Campaign.objects.get(id=camp_id)
    campaign.rfq_status = 2
    campaign.save()
    title = 'Counter RFQ CPL'
    desc = 'Counter RFQ CPL  by client on '+str(name)
    # noti_via_mail(sender_id,title, desc, 1)
    RegisterNotification(user_id, superadmin_id, desc,
                         title, 1, campaign, None)
    return True


def rejected_rfq_cpl_by_client(camp_id, cpl, volume, user_id, superadmin_id):
    """ reject cpl and volume sent from superadmin """
    campaign = Campaign_rfq.objects.get(campaign_id=camp_id)
    campaign.status = 4
    campaign.save()
    campaign = Campaign.objects.get(id=camp_id)
    name = campaign.name
    title = 'Reject RFQ CPL'
    desc = 'Reject RFQ CPL  by client on '+str(name)
    # noti_via_mail(sender_id, title, desc, 1)
    RegisterNotification(user_id, superadmin_id, desc,
                         title, 1, campaign, None)
    return True


@login_required
def RFQ_Campaign(request, camp_id):
    """ to request rfq suggestion from external vendors """
    campaign_details = Campaign.objects.get(id=camp_id)
    data = {
        'cpl': campaign_details.cpl,
        'targat_quantity': campaign_details.target_quantity,
        'ramaining_quantity': campaign_details.raimainingleads,
        'camp_id': camp_id,
        'camp_name': campaign_details.name,
        'client_name': campaign_details.user.user_name,
    }
    list = []
    vendor_list_details = []
    user_id = request.session['userid']
    marketing_method = source_touches.objects.filter(is_active=1)
    cpl_counter = campaign_allocation.objects.filter(
        campaign_id=camp_id, status=3, cpl=0, volume=-1).count()
    cpl_list = campaign_allocation.objects.filter(
        campaign_id=camp_id, status=3, cpl=0, volume=-1)
    vendor_list = external_vendor.objects.filter()
    for row in vendor_list:
        print(row.user_id)
        list = ast.literal_eval(row.client_id)
        if user_id in list:
            user_details = user.objects.get(id=row.user_id)
            vendor_list_details.append(
                {'userid': row.user_id, 'email': user_details.email, 'user_name': user_details.user_name})
    return render(request, 'campaign/client_rfq_campaign.html', {'cpl_counter': cpl_counter, 'cpl_list': cpl_list, 'data': data, 'vendor_list': vendor_list_details})


def rfq_vendor_allocation(request):
    """ to send request to external vendors """
    ids = request.POST.getlist('ids[]')
    camp_id = request.POST.get('camp_id')
    userid = request.session['userid']
    title = "New RFQ Campaign Allocated By"
    desc = "Client"
    for id in ids:
        counter = campaign_allocation.objects.filter(
            campaign_id=camp_id, client_vendor_id=id, cpl=-1, volume=-1, status=3).count()
        if counter != 1:
            campaign_allocation.objects.create(
                campaign_id=camp_id, client_vendor_id=id, cpl=-1, volume=-1, status=3)
        from client.utils import noti_via_mail
        noti_via_mail(id, title, desc, mail_noti_new_campaign)
        RegisterNotification(userid, id, desc, title, 2,None, campaign_allocation.objects.latest('id'))
    data = {'success': 1}
    return JsonResponse(data)


def update_rfq_cpl(request):
    """ update rfq and cpl """
    t = Campaign.objects.get(id=request.POST.get('camp_id'))
    t.cpl = request.POST.get('cpl')
    t.save()
    data = {'success': 1, 'msg': 'CPL updated Successfully!...'}
    return JsonResponse(data)


def counter_action_on_cpl(request):
    """ counter cpl """
    vendor_id = request.POST.get('vendor_id')
    camp_alloc_id = request.POST.get('camp_alloc_id')
    id = request.POST.get('id')
    userid = request.session['userid']
    cpl = request.POST.get('cpl')
    if id == '1':
        counter_action_accept_vendor(camp_alloc_id, vendor_id, userid, cpl)
        data = {'success': 1, 'msg': 'Counter Request accepted...'}
    elif id == '2':
        counter_action_reject_vendor(camp_alloc_id, vendor_id, userid)
    data = {'success': 1, 'msg': 'Counter Request Rejected...'}
    return JsonResponse(data)


def counter_action_accept_vendor(camp_alloc_id, vendor_id, userid, cpl):
    """ accept counter by external vendor """
    camp = campaign_allocation.objects.get(id=camp_alloc_id)
    name = camp.campaign.name
    camp.cpl = cpl
    camp.counter_status = 2
    camp.save()
    title = "Accept Counter by superadmin"
    desc = "Accept CPL Counter on " + str(name)
    from client.utils import noti_via_mail
    noti_via_mail(vendor_id, title, desc, mail_noti_vendor_action_on_camp_request)
    RegisterNotification(userid, vendor_id, desc, title, 1, None, camp)
    return True


def counter_action_reject_vendor(camp_alloc_id, vendor_id, userid):
    """ reject counter request """
    camp = campaign_allocation.objects.get(id=camp_alloc_id)
    name = camp.campaign.name
    camp.counter_status = 2
    camp.save()
    title = "Reject Counter by superadmin"
    desc = "Reject CPL Counter on " + str(name)
    from client.utils import noti_via_mail
    noti_via_mail(vendor_id, title, desc, mail_noti_vendor_action_on_camp_request)
    RegisterNotification(userid, vendor_id, desc, title, 1, None, camp)
    return True


def get_camp_specs(request):
    """ get all campaign specifications """
    camp_id = request.POST.get('id')
    camp_data = Campaign.objects.get(id=camp_id)
    # print(camp_data.__dict__)
    term_data = Terms.objects.get(campaign_id=camp_id)
    delivary_data = Delivery.objects.get(campaign_id=camp_id)
    mapping_data = Mapping.objects.get(campaign_id=camp_id)
    spec_data = Specification.objects.get(campaign_id=camp_id)

    # use as text mapping
    useAsTxtMapping = []
    txt_mapping_exist = UseAsTxtMapping.objects.count()
    if(txt_mapping_exist):  # if records exist
        useAsTxtMapping = UseAsTxtMapping.objects.filter(
            campaign=camp_data).values()  # list of dicts
        print("useAsTxtMapping : ", useAsTxtMapping.values())

    context = {
        'campaign_id': camp_data.id,
        'stat': camp_data.status,
        'target_quantity': camp_data.target_quantity if camp_data.target_quantity else '',
        'campaign_type': camp_data.get_type_display() if camp_data.type else '',
        'outrich_method': camp_data.method.all().values_list('type',flat=True) if camp_data.method.all() else '',
        'indursty_type': mapping_data.industry_type if mapping_data.industry_type else '',
        'job_title': mapping_data.job_title if mapping_data.job_title else '',
        'job_level': mapping_data.job_level if mapping_data.job_level else '',
        'assets': term_data.assets if term_data.assets else '',
        'delivery_method': delivary_data.delivery_method if delivary_data.delivery_method else '',
        'country': mapping_data.country if mapping_data.country else '',
        'company_size': mapping_data.company_size if mapping_data.company_size else '',
        'revenue': mapping_data.revenue_size if mapping_data.revenue_size else '',
        'data_field': delivary_data.data_header if delivary_data.data_header else '',
        'custom_data_fields':delivary_data.custom_header if delivary_data.custom_header else '',
        'tc_header_status':delivary_data.tc_header_status,
        'custom_header_status':delivary_data.custom_header_status,
        'pacing': spec_data.campaign_pacing if spec_data.campaign_pacing else '',
        'instructions': mapping_data.special_instructions if mapping_data.special_instructions else '',
        'useAsTxtMapping': useAsTxtMapping,
        'rfq_status': camp_data.rfq,
        'campaign':camp_data,
        'mapping':mapping_data,
        'Custom_question_status':mapping_data.custom_status,
        'usertype':request.session['usertype']
    }
    # return JsonResponse(data)
    html = render_to_response('campaign/show_campaign_specs.html', context)
    print("html :", html)
    return html


@login_required
def rejected_reason_list(request):
    """ return reject lead reasons """
    user_id = request.session['userid']
    # global_reason=leads_rejected_reson.objects.filter(status=0)
    client_reason = leads_rejected_reson.objects.filter(
        status=1, user_id=user_id)
    return render(request, 'lead/rejected_reason_list.html', {'reason': client_reason})


@login_required
def rectify_reason_list(request):
    """ return rectify lead reasons """
    user_id = request.session['userid']
    client_reason = Leads_Rectify_Reason.objects.filter(
        status=1, user_id=user_id)
    return render(request, 'lead/rectify_reason_list.html', {'reason': client_reason})


@login_required
def individual_campaign_notebook(request, camp_id):
    """ individual campaign notebook """
    campaign_details = Campaign.objects.filter(id=camp_id)
    live_camp_count = Campaign.objects.filter(id=camp_id, status=3).count()
    print(live_camp_count)
    vendor_list = get_vendor_list_of_campaign(camp_id)
    if campaign_details:
        return render(request, 'campaign/individual_campaign_notebook.html', {'camps': campaign_details, 'vendor_list': vendor_list,
                                                                              })
    else:
        return render(request, 'campaign/individual_campaign_notebook.html', {})

# updating campaign end date from campaign notebook


@login_required
def update_campaign_end_date(request):
    """ update campaign end date """
    if Campaign.objects.filter(id=request.POST.get('camp_id')).update(end_date=request.POST.get('date')):
        data = {'status': 1, 'message': 'date change successfully'}
    else:
        data = {'status': 2, 'message': 'date change failed'}
    return JsonResponse(data)


@login_required
def update_campaign_start_date(request):
    """ update campaign end date """
    if Campaign.objects.filter(id=request.POST.get('camp_id')).update(start_date=request.POST.get('date')):
        data = {'status': 1, 'message': 'date change successfully'}
    else:
        data = {'status': 2, 'message': 'date change failed'}
    return JsonResponse(data)


@login_required
def TC_vendor_list(request):
    """ TC vendor list """
    vendor_list_details = []
    user_id = request.session['userid']
    campaigns = Campaign.objects.filter(user=user_id)
    vendor_list = campaign_allocation.objects.filter(
        campaign_id__in=campaigns, status__in=[1, 5, 4])
    for row in vendor_list:
        user_details = client_vendor.objects.filter(
            user_id=row.client_vendor.id)
        if user_details:
            if user_details[0] not in vendor_list_details:
                vendor_list_details.append(user_details[0])
    return render(request, 'vendor1/TC_vendor_list.html', {'vendor_list': vendor_list_details})


def existing_vendor_list(request):
    """ TC vendor who are currently working with client """
    vendor_list_details = []
    user_id = request.session['userid']
    campaigns = Campaign.objects.filter(user=user_id)
    vendor_list = campaign_allocation.objects.filter(
        campaign_id__in=campaigns, status=1)
    for row in vendor_list:
        user_details = user.objects.filter(id=row.client_vendor.id)
        if user_details:
            if user_details[0] not in vendor_list_details:
                vendor_list_details.append(user_details[0])
    return render(request, 'vendor1/existing_vendor_list.html', {'vendor_list': vendor_list_details})


def get_cpl_list(request):
    """ return cpl list to superadmin """
    camp_id = request.GET.get('camp_id')
    user_id = request.session['userid']
    get_details = collect_campaign_details(camp_id)
    vendor_list = []
    tc_quote = []
    vendor_list_id = get_external_vendors(user_id)
    ext_vendor_list = campaign_allocation.objects.filter(campaign_id=camp_id,client_vendor_id__in=vendor_list_id, status=3, cpl__in=[-1,0], volume=-1)
    for vendor in ext_vendor_list:

        vendor_list.append({
            'id':vendor.client_vendor_id,
            'cpl':vendor.rfqcpl,
            'volume':vendor.rfqvolume,
            'name':vendor.client_vendor.user_name,

        })

    campaign = Campaign_rfq.objects.filter(campaign_id=camp_id)
    for vendor in campaign:
        if vendor.status == 1:
            tc_quote.append({
                'id':vendor.campaign_id,
                'cpl':vendor.cpl,
                'volume':vendor.volume,
                'name':'TC TEAM',
            })
    vendor_data = []
    vendorlist = campaign_allocation.objects.filter(campaign_id=camp_id, status=3,cpl=0)
    for vendor in vendorlist:
        vendor_data.append({
            'id': vendor.client_vendor_id,
            'vendor_name': vendor.client_vendor.user_name
        })
    rfq_timer = Campaign.objects.get(id=camp_id)
    rfq_timer = rfq_timer.rfq_timer

    # print(vendor_data)
    data = {'rfq_timer': rfq_timer,'success': 1,'ext_vendor_list':vendor_list,'details':get_details,'tc_quote':tc_quote,'vendor_data':vendor_data }
    return JsonResponse(data)


@login_required
def client_user_access(request):
    """ return user access modules to client """
    usertypes = usertype.objects.filter(type="external_vendor")
    users = []
    user_id = request.session['userid']
    vendor_list = external_vendor.objects.filter()
    for row in vendor_list:
        list = ast.literal_eval(row.client_id)
        if user_id in list:
            user_details = user.objects.get(id=row.user_id)
            users.append(user_details)
    groups = Client_User_Group.objects.filter(group_owner_id=user_id)
    return render(request, 'dashboard/client_user_access.html', {'type':usertypes,'groups':groups,'users':users})


@login_required
def get_user_access(request):
    """ return selected user access """
    current_user = user.objects.get(id=request.POST.get('userid'))
    if request.POST.get('groupid'):
        roles = User_Configuration.objects.filter(is_client =True,group__in=[request.POST.get('groupid')]).order_by('position')
        access = []
        for role in roles:
            if current_user in role.user.all():
                access.append({
                    'id': role.id,
                    'name': role.name,
                    'url': role.url,
                    'parent': role.parent.id if role.parent else None,
                    'checked': 1,
                    'groupname':role.group.filter(id=request.POST.get('groupid'))[0].group_name,
                    'groupid':role.group.filter(id=request.POST.get('groupid'))[0].id,
                })
            else:
                access.append({
                    'id': role.id,
                    'name': role.name,
                    'url': role.url,
                    'parent': role.parent.id if role.parent else None,
                    'checked': 0,
                    'groupname':role.group.filter(id=request.POST.get('groupid'))[0].group_name,
                    'groupid':role.group.filter(id=request.POST.get('groupid'))[0].id,
                })
        data = {'success': 1, 'user_roles': access}
    else:
        roles = User_Configuration.objects.filter(is_client =True,user_type__in=request.POST.get('usertype_id')).order_by('position')
        access = []
        for role in roles:
            if current_user in role.user.all():
                access.append({
                    'id': role.id,
                    'name': role.name,
                    'url': role.url,
                    'parent': role.parent.id if role.parent else None,
                    'checked': 1,
                    'usertype':role.user_type.filter(id=request.POST.get('usertype_id'))[0].type if request.POST.get('usertype_id') else None,
                })
            else:
                access.append({
                    'id': role.id,
                    'name': role.name,
                    'url': role.url,
                    'parent': role.parent.id if role.parent else None,
                    'checked': 0,
                    'usertype':role.user_type.filter(id=request.POST.get('usertype_id'))[0].type if request.POST.get('usertype_id') else None,
                })
        data = {'success': 1, 'user_roles': access}
    return JsonResponse(data)

def user_and_groups(request):
    """ display create group page """
    groups = Client_User_Group.objects.filter(group_owner_id=request.session['userid'])
    roles = User_Configuration.objects.filter(is_client =True,user=request.session['userid']).order_by('position')
    return render(request,'client/user_groups.html',{'groups':groups,'roles':roles})

def add_group(request):
    """ group add by client """
    client_id = user.objects.get(id=request.session['userid'])
    group_type = Client_User_Group.objects.create(group_name=request.POST.get('group'),group_owner=client_id)
    data = {'success': 1}
    return JsonResponse(data)

def delete_group(request):
    """ group delete by client """
    client_id = user.objects.get(id=request.session['userid'])
    group_type = Client_User_Group.objects.get(id=request.POST.get('group_id'),group_owner=client_id).delete()
    data = {'success': 1}
    return JsonResponse(data)

def edit_group(request):
    """ group add by client """
    client_id = user.objects.get(id=request.session['userid'])
    if request.method == 'POST':
        client_grp = Client_User_Group.objects.get(id=request.POST.get('group_id'),group_owner=client_id)
        if client_grp:
            client_grp.group_name = request.POST.get('group')
            client_grp.save()
        data = {'success': 1}
    else:
        client_grp = Client_User_Group.objects.get(id=request.GET.get('group_id'),group_owner=client_id)
        if client_grp:
            data = {'success': 1,'group_name':client_grp.group_name}
        else:
            data = {'success': 2}
    return JsonResponse(data)



def password_check(passwd):
    SpecialSym =['$', '@', '#', '%', '^', '&', '*', '+', '-', '!']
    if len(passwd) < 8:
        return False
    if not any(char.isdigit() for char in passwd):
        return False
    if not any(char.isupper() for char in passwd):
        return False
    if not any(char.islower() for char in passwd):
        return False
    if not any(char in SpecialSym for char in passwd):
        return False
    else:
        return True


def add_user_to_group(request):
    """ add user to group """
    username = request.POST.get('username')
    email = request.POST.get('email').lower()
    pwd = request.POST.get('password')
    site_url = settings.BASE_URL
    group_id = request.POST.get('group')
    client_id = user.objects.get(id=request.session['userid'])
    client_group = Client_User_Group.objects.get(id=group_id,group_owner=client_id)
    if client_group:
        email_check = email_domain_check(email)
        t = password_check(pwd)
        if t is True:
            if email_check['status'] == 1:
                if user.objects.filter(email=email).count() == 0:
                    new_user = user.objects.create(email=email, user_name=username,password=pwd, is_active=1, usertype_id=6)
                    client_group.group_users.add(new_user)
                    client_group.save()
                    data = {'success': 1,'msg':f'{new_user.user_name} added to {client_group.group_name}'}
                    subject = "Invitation From Techconnetr"
                    html_message = render_to_string('email_templates/external_user_register_template.html', {
                                                    'username': email, 'client':client_id.user_name,'site_url': site_url, 'password': pwd})
                    plain_message = strip_tags(html_message)
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [email]
                    if send_mail(subject, plain_message, from_email, to_list, fail_silently=True,html_message=html_message):
                        print('sent mail')
                else:
                    data = {'success': 2,'msg':f'User already exists'}
            else:
                data = email_check
        else:
            data = {'success': 0,'msg': 'Password should be greater than 8 characters and a combination of upper and lowercase characters, special symbols and numbers!!'}
    else:
        data = {'success': 1,'msg':'Group does not exists'}
    return JsonResponse(data)

@login_required
def get_group_access(request):
    """ return selected user access """
    user_group = Client_User_Group.objects.get(id=request.POST.get('groupid'),group_owner=request.session['userid'])
    roles = User_Configuration.objects.filter(is_client =True,user=request.session['userid']).order_by('position')
    access = []
    for role in roles:
        if user_group in role.group.all():
            access.append({
                'id': role.id,
                'name': role.name,
                'url': role.url,
                'parent': role.parent.id if role.parent else None,
                'checked': 1,
                'usertype':request.session['usertype'],
            })
        else:
            access.append({
                'id': role.id,
                'name': role.name,
                'url': role.url,
                'parent': role.parent.id if role.parent else None,
                'checked': 0,
                'usertype':request.session['usertype'],
            })
    data = {'success': 1, 'user_roles': access}
    return JsonResponse(data)


def grant_group_access(request):
    """ grant access to user """
    data = request.POST.getlist('access_id[]')
    usergroup = Client_User_Group.objects.get(id=request.POST.get('groupid'),group_owner=request.session['userid'])
    for access_id in data:
        access = User_Configuration.objects.get(id=access_id)
        if (access.parent == None):
            child = User_Configuration.objects.filter(parent_id=access_id)
            if child.count() > 0:
                if request.POST.get('parent_value') == 'true':
                    for role in child:
                        role.group.add(usergroup)
                        role.save()
                        print(role)
                        if User_Configuration.objects.filter(parent_id=role.id).count() > 0:
                            grand_child_access_call(role,access_id,usergroup,data,access)
                else:
                    for role in child:
                        role.group.remove(usergroup)
                        role.save()
                        if User_Configuration.objects.filter(parent_id=role.id).count() > 0:
                            grand_child_access_call(role,access_id,usergroup,data,access)
                # import pdb;pdb.set_trace()
                if User_Configuration.objects.filter(parent_id=access_id,group__in=[usergroup]).count() == 0:
                    access.group.remove(usergroup)
                else:
                    access.group.add(usergroup)
                access.save()
            else:
                if usergroup not in access.group.all():
                    access.group.add(usergroup)
                else:
                    access.group.remove(usergroup)
                access.save()
    data = {'success':1,'msg':f'Access Permission Changed For {usergroup.group_name}'}
    return JsonResponse(data)

def grant_child_group_access(request):
    """ child grant access to user """
    data = request.POST.getlist('access_id[]')
    usergroup = Client_User_Group.objects.get(id=request.POST.get('groupid'),group_owner=request.session['userid'])
    for access_id in data:
        access = User_Configuration.objects.get(id=access_id)
        if (access.parent == None):
            child = User_Configuration.objects.filter(parent_id=access_id)
            for role in child:
                if str(role.id) in data:
                    if usergroup not in role.group.all():
                        role.group.add(usergroup)
                    else:
                        role.group.remove(usergroup)
                    role.save()
                if User_Configuration.objects.filter(parent_id=role.id).count() > 0:
                    grand_child_access_call(role,access_id,usergroup,data,access)
            if User_Configuration.objects.filter(parent_id=access_id,group__in=[usergroup]).count() == 0:
                access.group.remove(usergroup)
            else:
                access.group.add(usergroup)
            access.save()
    data = {'success':1,'msg':f'Access Permission Changed For {usergroup.group_name}'}
    return JsonResponse(data)


def grant_grand_child_access(request):
    """ grant grand child access permision to the group """
    data = request.POST.getlist('access_id[]')
    usergroup = Client_User_Group.objects.get(id=request.POST.get('groupid'),group_owner=request.session['userid'])
    for access_id in data:
        access = User_Configuration.objects.get(id=access_id)
        if (access.parent == None):
            child = User_Configuration.objects.filter(parent_id=access_id)
            for sub_menu in child:
                if str(sub_menu.id) in data:
                    grand_child = User_Configuration.objects.filter(parent_id=sub_menu.id)
                    for grand_menu in grand_child:
                        if str(grand_menu.id) in data:
                            if usergroup not in grand_menu.group.all():
                                grand_menu.group.add(usergroup)
                            else:
                                grand_menu.group.remove(usergroup)
                            grand_menu.save()
                    if User_Configuration.objects.filter(parent_id=sub_menu.id,group__in=[usergroup]).count() == 0:
                        sub_menu.group.remove(usergroup)
                    else:
                        sub_menu.group.add(usergroup)
            if User_Configuration.objects.filter(parent_id=access_id,group__in=[usergroup]).count() == 0:
                access.group.remove(usergroup)
            else:
                access.group.add(usergroup)
            access.save()
    data = {'success':1,'msg':f'Access Permission Changed For {usergroup.group_name}'}
    return JsonResponse(data)


def get_group_users(request):
    """ return members in a group """
    group_users = []
    group = Client_User_Group.objects.get(id=request.GET.get('group_id'),group_owner=request.session['userid'])
    for users in group.group_users.all():
        group_users.append({
            'userid': users.id,
            'name': users.user_name,
            'email': users.email,
            'status':users.is_active,
        })
    data = {'success':1,'group_users':group_users}
    return JsonResponse(data)

def remove_group_user(request):
    """ remove user from group and platform """
    user.objects.get(id=request.POST.get('user_id')).delete()
    data = {'success':1}
    return JsonResponse(data)

def action_on_camp_by_client(status, lead_list, campaign_id, vendor_id, vendor, reason=None, status_code=None):

    if CampaignTrack.objects.filter(campaign_id=campaign_id).exists():
        camp_alloc = campaign_allocation.objects.get(campaign_id=campaign_id, client_vendor_id=vendor_id)
        track = CampaignTrack.objects.get(campaign_id=campaign_id)
        if status == 1:
            status = 'approved'
        elif status == 2:
            status = 'rejected'
        elif status == 3:
            status = 'rectify'

        if track.client_action_count > 0:
            list = eval(track.client_action)

            d = {}
            d['type'] = 'action'
            d['vendor_id'] = vendor_id
            d['vendor'] = vendor
            d['status'] = status
            d['lead_id'] = lead_list
            t = datetime.datetime.now()
            d['date'] = t.isoformat()
            d['reason'] = reason
            d['status_code'] = status_code
            d['vendor_percentage'] = vendorper(camp_alloc.id)
            d['client_percentage'] = percentage(campaign_id)
            list.append(d)
            track.client_action = list
            track.client_action_count += 1
            track.save()
            # print(list)
            # print('hello')
        else:
            list = []
            d = {}
            d['type'] = 'action'
            d['vendor_id'] = vendor_id
            d['vendor'] = vendor
            d['status'] = status
            d['lead_id'] = lead_list
            t = datetime.datetime.now()
            d['date'] = t.isoformat()
            d['reason'] = reason
            d['status_code'] = status_code
            d['vendor_percentage'] = vendorper(camp_alloc.id)
            d['client_percentage'] = percentage(campaign_id)
            list.append(d)
            track.client_action = list
            track.client_action_count += 1
            track.save()
