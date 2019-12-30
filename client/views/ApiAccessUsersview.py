from client.models import *
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from client.decorators import is_client
from user.models import user
from techconnectr.settings import BASE_URL
from techconnectr import settings
import hashlib
import json
from django.utils.html import strip_tags
from campaign.models import campaign_allocation
from django.http import HttpResponseRedirect


def apilink(request):

    if request.method == 'POST':

        campaign_id = request.POST['campaign_id']
        clientid = request.POST['client_id']
        email = request.POST['email']
        dic = []
        user = ApiAccessUsers.objects.get(email=email)
        access = user.ApiAccess.all()
        if campaign_allocation.objects.filter(campaign_id=campaign_id).exists():

            if campaign_allocation.objects.filter(campaign_id=campaign_id, campaign__user=clientid).exists():
                camp_objects = campaign_allocation.objects.filter(campaign_id=campaign_id, campaign__user=clientid)
                for camp in camp_objects:
                    if type(camp.upload_leads) == 'str':
                        dic.append(eval(camp.upload_leads))
                    else:
                        dic.append(camp.upload_leads)

                # for lead in camp.upload_leads:

                context = {
                    'client_id': clientid,
                    'access': access,
                    'content': json.dumps(dic)
                }
                return render(request, 'api-export/json.html', context)
            else:
                context = {
                    'client_id': clientid,
                    'access': access,
                    'content': 'No leads are present',
                }
                return render(request, 'api-export/json.html', context)
        else:
            # campaign id does not exists
            context = {
                'client_id': clientid,
                'access': access,
                'content': 'Invalid ID'
            }
            return render(request, 'api-export/json.html',context)

    else:
        # Something's Wrong
        return HttpResponseRedirect('export-login')


@is_client
def ApiAccessUserView(request):
    if request.method == 'POST':

        userid = user.objects.get(id=request.POST['user'])
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        links = request.POST.getlist('apis')

        if password == password2:
            email_list = HeadersValidation.objects.all()
            email_splited = email.split('@')
            if email_splited[1] in eval(email_list[0].email_list):
                data = {'success': 0, 'msg': 'Only Bussiness Domains are allowed!'}
                return JsonResponse(data)
            # token generation
            # URL
            url = str(BASE_URL) + 'client/export-login'
            mystring = str(password)+str(email)
            hash_object = hashlib.md5(mystring.encode())
            token = hash_object.hexdigest()
            if ApiAccessUsers.objects.filter(email=email).exists():
                data1 = ApiAccessUsers.objects.filter(client_id=userid, email=email, password=password, token=token)
                if data1:
                    # email already exists user below form to send link to reciever
                    for link in links:
                        data2 = ApiAccessUsers.objects.get(client_id=userid, email=email, password=password, token=token)
                        data2.ApiAccess.add(ApiLinks.objects.get(id=link))
                        data2.save()
                    data = {'success': 1, 'msg': 'Done'}
                    # mail has been sent to appopriate receiver
                    return JsonResponse(data)
                else:
                    data = {'success': 0, 'msg': 'User is already associated with other client'}
                    return JsonResponse(data)
            else:
                instance = ApiAccessUsers(client_id=userid, email=email, password=password, token=token)
                instance.save()
                for link in links:
                    instance.ApiAccess.add(ApiLinks.objects.get(id=link))
                instance.save()
                html_message = render_to_string('email_templates/leads_export.html', {
                                                'username': email, 'password': password, 'site_url': url, 'token':token})
                plain_message = strip_tags(html_message)

                from_email = settings.EMAIL_HOST_USER
                to_list = [email]

                send_mail(
                    'Link for api of leads',
                    plain_message,
                    from_email,
                    to_list,
                    fail_silently=True,
                )
                data = {'success': 1, 'msg': 'Done'}
                # mail has been sent to appopriate receiver
                return JsonResponse(data)
        else:
            # password and Confirm password do not match
            data = {'success': 0, 'msg': 'Sorry, Password Do Not Match!'}
            return JsonResponse(data)
    else:
        # something wrong!!
        data = {'success': 0, 'msg': 'Error, Something Is Wrong!'}
        return JsonResponse(data)


def ApiAccessUserLogin(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        code = request.POST['code']

        if email is not None and password is not None and code is not None:
            email = email.lower()
            if ApiAccessUsers.objects.filter(email=email, password=password, token=code).exists():
                # link to api
                user = ApiAccessUsers.objects.get(email=email, password=password, token=code)
                # print(user)
                request.session['email'] = user.email
                access = user.ApiAccess.all()
                context1 = {
                    'access': access,
                    'email': email,
                    'client_id': user.client_id.id,
                }
                return render(request, 'api-export/json.html', context1)
            else:
                # Invalid credentials
                error = 'Invalid Credentials!!'
                return render(request, 'api-export/ApiAccessLogin.html', {'error':error})
        else:
            error = 'All fields required!! '
            return render(request, 'api-export/ApiAccessLogin.html', {'error':error})
    else:
        # Something Wrong. Try Again!
        error = "Sorry, Something's Wrong, Please Login Again!"
        return render(request, 'api-export/ApiAccessLogin.html', {'error':error})

def apilogout(request):
    if request.session:
        if 'email' in request.session:
            login = ApiAccessUsers.objects.get(email=request.session['email'])
            login.is_login = 0
            login.save()
    for key in list(request.session.keys()):
        del request.session[key]
    return HttpResponseRedirect('export-login')
