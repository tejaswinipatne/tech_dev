import ast
from campaign.models import *
from client.models import *
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from setupdata.models import (Notification, Notification_Reciever,
                              notification_type, countries1 as countries_list)
from superadmin.models import *
from superadmin.views.views import topVendorList
from vendors.models import *
from django.conf import settings
from datetime import datetime
from django.core.mail import send_mail
from user.models import user
from setupdata.models import MailNotification

def check_all_data_available_in_post(data, post):
    """ check all data available in post request """
    missing_parameters = []

    if data:
        for parameter in data:
            # check is exist in post
            if parameter not in post:
                missing_parameters.append(parameter)

        if missing_parameters:
            success = False
            message = "Missing parameters in request are : " + \
                (', '.join(missing_parameters))
        else:
            success = True
            message = "All parameters are available in post"
    else:
        success = False
        message = "No data supplied to check in post"

    response = {
        "success": success,
        "message": message,
    }
    return response


def saving_assets(request, assets):
    ''' saaving assets into data base '''
    asset_dict = {}
    file_list = []
    files = request.FILES
    if files:
        for asset in assets.split(','):
            if asset in request.FILES:
                for file_name in request.FILES.getlist(asset):
                    file_list.append(save_asset_file(file_name))
                    if request.POST.get(asset):
                        links = request.POST.getlist(asset)
                        links.remove('') if ('') in links else links
                        asset_dict[asset] = {'files':file_list,'link': links}
                    else:
                        asset_dict[asset] = {'files':file_list}
    for asset in assets.split(","):
        if request.POST.get(asset):
            links = request.POST.getlist(asset)
            links.remove('') if ('') in links else links
            if asset not in asset_dict:
                asset_dict[asset] = {'link': links}
            else:
                asset_dict[asset].update({'link': links})

    return asset_dict

def save_asset_file(file_name):
    myfile = file_name
    fs = FileSystemStorage()
    filename = fs.save('campaign_assets/'+myfile.name, myfile)
    uploaded_file_url = fs.url(filename)
    return {'filename': filename.lstrip('campaign_assets/'), 'url': uploaded_file_url}

def update_assets(request, assets, assets_type):
    """ update assets """
    files = request.FILES
    if files:
        for asset in assets.split(','):
            if asset in request.FILES:
                for file_name in request.FILES.getlist(asset):
                    file_list = []
                    file_list.append(save_asset_file(file_name))
                    if asset in assets_type:
                        if 'files' in assets_type[asset]:
                            newlist = assets_type[asset]['files']+file_list
                            assets_type[asset].update({'files':newlist})
                        else:
                            assets_type[asset].update({'files': file_list})
                    else:
                        if request.POST.get(asset):
                            links = request.POST.getlist(asset)
                            links.remove('') if ('') in links else links
                            assets_type[asset] = {'files':file_list,'link': links}
                        else:
                            assets_type[asset] = {'files':file_list}
    for asset in assets.split(","):
        if request.POST.get(asset):
            links = request.POST.getlist(asset)
            links.remove('') if ('') in links else links
            if asset in assets_type:
                if 'link' in assets_type[asset]:
                    newlist = assets_type[asset]['link']+links
                    assets_type[asset].update({'link': newlist})
                else:
                    assets_type[asset].update({'link': links})
            else:
                assets_type[asset] = {'link': links}

    return assets_type


def client_top_vendor(userid):
    """ retrn client top vendors working on campaigns """

    vendordetail = []
    cpl = 0
    volume = 0
    camps = Campaign.objects.filter(user_id=userid)
    for row in camps:
        campaignallocationdetails = campaign_allocation.objects.filter(
            campaign_id=row.id, status__in=[1, 4])
        for row1 in campaignallocationdetails:
            revenue = 0
            cpl += int(row1.cpl) if row1.cpl else 0
            volume += row1.volume if row1.volume else 0
            revenue += int(cpl * volume) if row1.cpl and row1.volume else 0

            if client_vendor.objects.filter(user_id=row1.client_vendor_id).count() == 1:
                clientvendordetail = client_vendor.objects.get(
                    user_id=row1.client_vendor_id)
                country = countries_list.objects.filter(
                    id=clientvendordetail.user.country)
                # country = countries.objects.filter(
                #     id=clientvendordetail.user.country)
                speciality = industry_speciality.objects.filter(
                    id=clientvendordetail.industry_speciality_id)
                for i in vendordetail:
                    if i['id'] == clientvendordetail.user.id:
                        cpl += i['CPL']
                        volume += i['leads']
                        revenue += i['revenue']
                        vendordetail.remove(i)
                vendordetail.append({
                    "id": clientvendordetail.user.id,
                    "vendorname": clientvendordetail.user.user_name,
                    "website": clientvendordetail.website,
                    "country": country[0] if country else '',
                    "lead": clientvendordetail.lead_per_month,
                    "speciality": speciality[0] if speciality else '',
                    "revenue": revenue,
                    "CPL": cpl,
                    "leads": volume,
                })
        revenue = 0
        cpl = 0
        volume = 0
    # L = []
    # for i in vendordetail:
    #     for j in vendordetail:
    #         if vendordetail.index(i) == vendordetail.index(j):
    #             pass
    #         elif i['id'] == j['id']:
    #             L.append(vendordetail.index(j))
    #             i["revenue"] += j["revenue"]
    # L1 = []
    # for i in L:
    #     if i not in L1:
    #         L1.append(i)
    #
    # for i in L:
    #     del vendordetail[i]
    return vendordetail


def tc_top_vendors_types():
    """ TC top vendors """
    vendor = user.objects.filter(usertype_id=2)
    topvendor = topVendorList(vendor)
    for tc_vendor in topvendor:
        if client_vendor.objects.filter(user_id=tc_vendor['id']).count() == 1:
            vendor_details = data_assesment.objects.get(
                user_id=tc_vendor['id'])
            if vendor_details.vendor_type:
                for cvid in ast.literal_eval(vendor_details.vendor_type):
                    v_type = VendorType.objects.get(id=int(cvid))
                    if 'vendor_type' not in tc_vendor.keys():
                        tc_vendor.update({'vendor_type': [v_type.type]})
                    else:
                        tc_vendor['vendor_type'].append(v_type.type)
    return topvendor


def RegisterNotification(sender_id, receiver_id, desc, title, notification_type_id, campaign, camp_alloc):
    """ raise notifications for venodrs and superadmins """
    try:
        Notification.objects.create(title=title, description=desc, notification_type_id=notification_type_id,
                                    sender_id=sender_id, campaign_id=campaign, camp_alloc=camp_alloc)
    except:
        if camp_alloc:
            Notification.objects.create(title=title, description=desc,
                                        notification_type_id=notification_type_id, sender_id=sender_id, camp_alloc=camp_alloc)
        if campaign:
            Notification.objects.create(title=title, description=desc,
                                        notification_type_id=notification_type_id, sender_id=sender_id, campaign_id=campaign)

    Nlast_id = Notification.objects.latest('id')
    Notification_Reciever.objects.create(
        status='0', Notification_id=Nlast_id.id, receiver_id=receiver_id)


def get_external_vendors(user_id):
    vendor_list_id = []
    extr_vendors = external_vendor.objects.filter()
    for row in extr_vendors:
        list = ast.literal_eval(row.client_id)
        if user_id in list:
            user_details = user.objects.get(id=row.user_id)
            vendor_list_id.append(row.user_id)
    return vendor_list_id


def check_is_logged_in(request):
    """ logout when session get expire  """
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


def grand_child_access_call(sub_menu, access_id, usergroup, data, access):
    ''' grant grand child menu access of sub menu '''
    grand_child = User_Configuration.objects.filter(parent_id=sub_menu.id)
    for grand_menu in grand_child:
        if str(grand_menu.id) in data:
            if usergroup not in grand_menu.group.all():
                grand_menu.group.add(usergroup)
            else:
                grand_menu.group.remove(usergroup)
            grand_menu.save()
    # for sub menu
    if User_Configuration.objects.filter(parent_id=sub_menu.id, group__in=[usergroup]).count() == 0:
        sub_menu.group.remove(usergroup)
    else:
        sub_menu.group.add(usergroup)
    # # form main menu
    # if User_Configuration.objects.filter(parent_id=access_id,group__in=[usergroup]).count() == 0:
    #     access.group.remove(usergroup)
    # else:
    #     access.group.add(usergroup)
    # access.save()
    return True


def send_speces_fill_reminder():
    campaigns = Campaign.objects.filter(status=5)
    message_content = []
    for camp in campaigns:
        specification_data = Specification.objects.get(campaign_id=camp)
        delivery_data = Delivery.objects.get(campaign_id=camp)
        mapping_data = Mapping.objects.get(campaign_id=camp)
        temp_dict ={}

        if specification_data:
            temp_dict.update({'abm_status':specification_data.abm_count,'suppression_status':specification_data.suppression_count})

        if delivery_data:
            temp_dict.update({'data_header':len(delivery_data.data_header.split(',')) if delivery_data.data_header else 0})

        if mapping_data:
            temp_dict.update({'industry':len(mapping_data.industry_type.split(',')) if mapping_data.industry_type else 0})
            temp_dict.update({'industry':len(mapping_data.job_level.split(',')) if mapping_data.job_level else 0})
            temp_dict.update({'job_title':len(mapping_data.job_title) if mapping_data.job_title else 0})
            temp_dict.update({'custom_status':0})

        # print(temp_dict)
        if datetime.strptime(camp.start_date,"%Y-%m-%d") >= datetime.now():
            diff = datetime.strptime(camp.start_date,"%Y-%m-%d") - datetime.now()
            if diff.days <= 5:
                subject='Campaign Specification Pending'
                from_email = settings.EMAIL_HOST_USER
                to=[camp.user.email]
                html_message = render_to_string('email_templates/campaign_specs_reminder.html', {'data':temp_dict,'username':camp.user.user_name,'campaign':camp})
                plain_message = strip_tags(html_message)
                send_mail(subject,plain_message,from_email,to,fail_silently=True,html_message=html_message)

    return True

def email_domain_check(email):
    """ to check email is only bussiness domain """
    email_list = HeadersValidation.objects.all()
    email_splited = email.split('@')
    if email_splited[1] in eval(email_list[0].email_list):
        data = {'status':0,'msg':"Only Bussiness Domains are allowed."}
    else:
        data = {'status':1,'msg':"Successful"}
    return data

def percentage(camp_id):

    campaign = campaign_allocation.objects.filter(campaign_id=camp_id)
    percentage_val = 0
    for camp in campaign:
        if camp.approve_leads is not None and camp.campaign.target_quantity is not None:
            percentage_val = percentage_val + (camp.approve_leads/camp.campaign.target_quantity)*100
    return int(percentage_val)


def noti_via_mail(userid, subject, description, type):
    
    user1 = user.objects.get(id=userid)
    mail = MailNotification.objects.filter(user__id=userid)
    if mail:
        for m in mail:
            if type == m.id:
                print('sent')
                print(user1.user_name)
                send_mail(
                    subject,
                    description,
                    settings.EMAIL_HOST_USER,
                    [user1.email],
                    fail_silently=False,
                )
