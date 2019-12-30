import ast
import datetime
from user.models import *

from django.conf import settings
from django.core import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve
from django.core.files.storage import FileSystemStorage
from campaign.models import *
from client.models import *
from client_vendor.models import *
from setupdata.models import *
from setupdata.serializer import *


def get_campaign_chat(request):
    """ get campaign chat  """
    data = {'success': 1}
    camp_id = request.POST.get('camp_id')    
    if Campaign_chats.objects.filter(campaign_id=camp_id).count() > 0:
        chats = Campaign_chats.objects.filter(campaign_id=camp_id)
        data = get_chats_into_dict(chats, request.session['userid'])
        return JsonResponse(data, safe=False)
    return JsonResponse(data)


def get_chats_into_dict(chats, userid):
    """ insert chat data into dict """
    chat_data = []
    for msg in chats:
        data = ast.literal_eval(msg.data)
        for chat_msg in data:
            if userid in chat_msg['receiver_ids']:
                chat_data.append({
                    'profilepic': chat_msg['profilepic'],
                    'sender_id': chat_msg['sender_id'],
                    'message': chat_msg['message'],
                    'time': chat_msg['time'],
                    'date': chat_msg['date'],
                    'media':chat_msg['media'],
                    'title':chat_msg['title'],
                })
    return chat_data


def campaign_chat_screen(request, camp_id):
    """ opens chat screen  """
    chat_list = []
    camp = Campaign.objects.get(id=camp_id)
    camp_list = get_user_live_campaign(camp.user_id, camp)
    vendor_list = get_vendor_list_of_campaign(camp_id)
    if Campaign_chats.objects.filter(campaign_id=camp_id).count() > 0:
        chats = Campaign_chats.objects.get(campaign_id=camp_id)
        chat_list = ast.literal_eval(chats.data)
    return render(request, 'campaign_chat/chat_screen.html', {'campaign_list': camp_list, 'sender_id': request.session['userid'], 'chat': chat_list, 'vendor_list': vendor_list, 'campaign': camp})


def get_user_live_campaign(userid, camp):
    """ return users live campaign list """
    camp_id = []
    camp_list = []
    camp = Campaign.objects.filter(user_id=userid, status=1)
    camp_allc = campaign_allocation.objects.filter(
        campaign_id__in=camp, status=1)
    for row in camp_allc:
        if row.campaign_id not in camp_id:
            camp_id.append(row.campaign_id)
            camp_list.append({
                'id': row.campaign_id,
                'name': row.campaign
            })
    return camp_list


def get_vendor_list_of_campaign(camp_id):
    """ return working vendor list on campaign """
    vendor_id = []
    vendor_data = []
    vendor_list = campaign_allocation.objects.filter(
        campaign_id=camp_id, status__in=[1,4,5])
    for vendor in vendor_list:
        if vendor.client_vendor_id not in vendor_id:
            vendor_id.append(vendor.client_vendor_id)
            vendor_data.append({
                'id': vendor.client_vendor_id,
                'vendor_name': vendor.client_vendor
            })
    return vendor_data


def send_msg(request):
    """ send messages """
    ids = []
    media=""
    title=""
    sender_name=request.session['username']
    msg = request.POST.get('message')
    camp_id = request.POST.get('camp_id')
    receiver_ids = list(campaign_allocation.objects.filter(campaign_id=camp_id, status__in=[1,4,5]).values_list('client_vendor', flat=True).distinct())
    superadmin_id = user.objects.get(usertype_id=usertype.objects.filter(
        type='superadmin').values_list('id')[0])
    if len(request.POST.getlist('vendor_names')) == 0:
        ids.append(superadmin_id.id)
        ids.append(request.session['userid'])
        ids.extend(receiver_ids)
        result = store_msg(request.session['userid'], ids, msg,media,title, camp_id,sender_name)
        if result['status'] == 'true':
            data = {'success': 1,'time':result['time'],'msg':request.POST}
    else:
        ids = list(map(int, request.POST.getlist('vendor_names')))
        ids.append(superadmin_id.id)
        ids.append(request.session['userid'])
        result = store_msg(request.session['userid'], ids, msg,media,title, camp_id,sender_name)
        if result['status'] == 'true':
            data = {'success': 1,'time':result['time'],'msg':request.POST}
    return JsonResponse(data)


def store_msg(sender_id, receiver_ids, msg,media,title,camp_id,sender_name):
    """ store messages into dict """
    last_dict = {}
    list_count = 0
    time = datetime.now().strftime('%H:%M:%S')
    profilepic = client_vendor.objects.get(user_id=sender_id)
    if profilepic.company_logo:
        profilepic = profilepic.company_logo.url
    else:
        profilepic = '/assets/images/placeholder.jpg'
    if Campaign_chats.objects.filter(campaign_id=camp_id).count() == 1:
        chats_details = Campaign_chats.objects.get(campaign_id=camp_id)
        list = ast.literal_eval(chats_details.data)
        last_dict = list[-1]
        list.append({'sender_id': sender_id,'sender_name':sender_name, 'receiver_ids': receiver_ids, 'profilepic': profilepic,
                     'message': msg,'media':media,'title':title,'time': time,'first':1, 'date': str(datetime.today().date()), 'rank': int(last_dict['rank'])+1})
        list_count = len(list)
        chats_details.data = list
        chats_details.save()
    else:
        list = []
        list.append({'sender_id': sender_id,'sender_name':sender_name,'receiver_ids': receiver_ids, 'profilepic': profilepic,
                     'message': msg,'media':media,'title':title,'time': time,'first':0, 'date': str(datetime.today().date()), 'rank': 1})
        Campaign_chats.objects.create(campaign_id=camp_id, data=list)
    send_campaign_notification(receiver_ids, sender_id, camp_id, list_count)
    data = {'status':'true','time':time}
    return data

#send attachment to users
def send_attchment(request):
    if request.FILES:   
        sender_id=request.session['userid'] 
        sender_name=request.session['username']
        camp_id = request.POST.get('camp_id')
        title=request.POST.get('title')
        msg="0"
        receiver_ids=request.POST.getlist('ids[]')
        receiver_ids.append(sender_id)
        receiver_ids = list(map(int, receiver_ids))
        myfile = request.FILES['filename']
        fs = FileSystemStorage()
        filename = fs.save("chat_data/" + myfile.name,  myfile)
        media='media/'+filename
        store_msg(sender_id,receiver_ids,msg,media,title,camp_id,sender_name)
    return JsonResponse({'success': 1})        
            


def send_campaign_notification(receiver_ids, sender_id, camp_id, list_count):
    """ raise messages notification """
    data = []
    receiver_ids.remove(sender_id)
    user_data = user_activities.objects.filter(user_id__in=receiver_ids)
    for row1 in user_data:
        if row1.active_page != 'chat':
            if Campaign_notification.objects.filter(campaign_id=camp_id).count() > 0:
                notification = Campaign_notification.objects.get(
                    campaign_id=camp_id)
                list = ast.literal_eval(notification.data)
                userid = create_userid_list(list)
                if row1.user_id in userid:
                    for row in list:
                        row['all_msg_cnt'] = list_count
                        row['start'] = row['end']
                        row['end'] = list_count
                        row['check'] = 0
                        row['read'] = 0
                else:
                    list.append({'user_id': row1.user_id, 'all_msg_cnt': list_count,
                                 'start': 15, 'end': list_count, 'check': 0, 'read': 0})
                    notification.data = list
                    notification.save()
            else:
                data.append({'user_id': row1.user_id, 'all_msg_cnt': list_count,
                             'start': 0, 'end': list_count, 'check': 0, 'read': 0})
                Campaign_notification.objects.create(
                    campaign_id=camp_id, data=data)


def create_userid_list(list):
    """ return user id list for reciving chat """
    userid = []
    for row in list:
        userid.append(row['user_id'])
    return userid


def chat_read_notification(request):
    """ set message as read message """
    userid = request.session['userid']
    camp_id = request.POST.get('id')
    notify = Campaign_notification.objects.get(campaign_id=camp_id)
    list = ast.literal_eval(notify.data)
    for row in list:
        if row['user_id'] == userid:
            row['check'] = 1
            notify.data = list
            notify.save()
    return True
