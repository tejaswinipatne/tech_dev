from django.urls import path
from . import views

app_name = "client_users"
urlpatterns = [
    path('',views.user_dashboard, name='user_dashboard'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    # campaign side menu links
]