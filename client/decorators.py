from django.shortcuts import redirect,render
from functools import wraps
from django.contrib import messages
from superadmin.models import *

def login_required(function):
    """  Check is user logged in
    If user_id not available in session
    Then it will be redirected to root url
    """
    def wrap(request=None, *args, **kwargs):
        if request:
            if "is_login" in request.session:
                if request.session['is_login'] == True:
                    return function(request, *args, **kwargs)
            else:
                messages.error(request, 'Login required.')
                return redirect("/login/")
        else:
            print("Request data is empty while processing login required decorator")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_client(function):
    """ Check is user type is client or not
        usertypes :
            * 1 - client
            * 2 - vendor
            * 3 - Superadmin
            * 5 - for external vendor

    """
    def wrap(request, *args, **kwargs):
        if request.session['usertype'] == 1 or request.session['usertype'] == 6:
            print(request.get_full_path())
            if request.get_full_path() != '/client/':
                if User_Configuration.objects.filter(url=request.get_full_path()).exists():
                    try:
                        client_access = User_Configuration.objects.filter(user__in=[request.session['userid']],url=request.get_full_path())
                        print(client_access.count())
                        access = client_access.filter(user=request.session['ext_userid'])
                    except Exception as e:
                        access = User_Configuration.objects.filter(user__in=[request.session['userid']],url=request.get_full_path())
                    if access.count() == 1:
                        return function(request, *args, **kwargs)
                    else:
                        return render(request,'errors/client_permission_denied.html',{})
                else:
                    return function(request, *args, **kwargs)
            else:
                return function(request, *args, **kwargs)
            # return function(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Not a valid user type to access requested data.')
            # return redirect("/client/create-campaign/")
            return redirect("/logout/")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_superadmin(function):
    """ Check is user type is client or not
    usertypes :
        * 1 - client
        * 2 - vendor
        * 3 - client_vendor
        * 4 - Superadmin
        * 5 - for external vendor

    """
    def wrap(request, *args, **kwargs):
        if request.session['usertype'] == 4:
            return function(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Not a valid user type to access requested data.')
            # return redirect("/client/create-campaign/")
            return redirect("/logout/")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_vendor(function):
    """
    Check is user type is client or not
    usertypes :
        * 1 - client
        * 2 - vendor
        * 3 - client_vendor
        * 4 - Superadmin
        * 5 - for external vendor

    """
    def wrap(request, *args, **kwargs):
        if request.session['usertype'] == 2 or request.session['usertype'] == 5:
            # return function(request, *args, **kwargs)
            print(request.get_full_path())
            if request.get_full_path() != '/vendor/':
                if User_Configuration.objects.filter(url=request.get_full_path()).exists():
                    # try:
                    #     client_access = User_Configuration.objects.filter(user__in=[request.session['userid']],url=request.get_full_path())
                    #     print(client_access.count())
                    #     access = client_access.filter(user=request.session['ext_userid'])
                    # except Exception as e:
                    access = User_Configuration.objects.filter(user__in=[request.session['userid']],url=request.get_full_path())
                    if access.count() == 1:
                        return function(request, *args, **kwargs)
                    else:
                        return render(request,'errors/vendor_permission_denied.html',{})
                else:
                    return function(request, *args, **kwargs)
            else:
                return function(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Not a valid user type to access requested data.')
            # return redirect("/client/create-campaign/")
            return redirect("/logout/")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
