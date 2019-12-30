from django.urls import path
from . import views

app_name = "client_vendor"
urlpatterns = [
    path('', views.vendor_portal, name='vendor-portal'),
    path('dashboard/', views.cdashboard, name='cdashboard'),
    # campaign side menu links
    path('manage-campaign/', views.cv_manage_campaign, name='cv_manage_campaign'),
    path('live-campaign/', views.cv_vendor_live_campagin,
         name="cv_vendor_live_campagin"),
    path('paused-campaign/', views.cv_vendor_paused_campagin,
         name="cv_vendor_paused_campagin"),
    path('completed-campaign/', views.cv_vendor_completed_campagin,
         name="cv_vendor_completed_campagin"),
    path('assigned-campaign/', views.cv_vendor_assigned_campagin,
         name="cv_vendor_assigned_campagin"),
    path('pending-campaign/', views.cv_pending_campaign,
         name="cv_pending_campaign"),
    path('campaign-notebook/', views.cv_campaign_notebook,
         name="cv_campaign_notebook"),
    # accpting campaign request
    path('sendAgreeRequest/<int:camp_alloc_id>/',
         views.accpet_campaign_request, name='accpet_campaign_request'),
    path('remove_campaign_from_pending/<int:camp_id>/<int:leads>',
         views.remove_campaign_from_pending, name='remove_campaign_from_pending'),
    #     path('account/', views.cv_vendor_account, name='cv_vendor_account'),
    path('account/', views.cv_vendor_account, name='cv_vendor_account'),
    path('counter-CPL-form/', views.Counter_CPL_form, name='Counter_CPL_form'),
    path('chat-app/<int:camp_id>/', views.campaign_chat_screen, name='chat'),
    path('rfqcpl/', views.rfqcpl, name='rfqcpl'),
    path('logout/', views.logout, name='logout'),
    path('vendor_leadlist/<int:camp_id>/<int:status>/',views.vendor_leadlist, name='vendor_leadlist'),
    path('vendor_portal_leadlist/<int:camp_id>/<int:status>',views.vendor_leadlist, name='vendor_portal_leadlist'),
    path('upload_with_rejected_lead/<int:camp_id>/<int:camp_alloc_id>/',views.upload_with_rejected_lead_web,name="lead_error_list"),
    path('upload_without_rejected_lead/<int:camp_id>/<int:camp_alloc_id>/',views.upload_without_rejected_lead_web,name="lead_error_list"),


]
