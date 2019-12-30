import os
from django.urls import path, include, re_path
from . import views
from vendors import views as vendor_views
from client.views import *
from form_builder import views as form_view
from django.urls import path
from client.views.ApiAccessUsersview import *
from client.utils import *

# from rest_framework.urlpatterns import format_suffix_patterns
from django.views.generic import TemplateView

urlpatterns = [
    # path('api/<pk>', clientDetailAPIView.as_view(), name='clientlist'),
    # path('obtaintoken', obtain_auth_token, name='api-token'),

    path('', views.cdashboard),
    path('dashboard/', views.cdashboard),
    path('ajax/loadstates/', views.loadstates, name='loadstates'),
    path('loadstates/', views.loadstates, name='loadstates'),
    path('ajax/loadcity/', views.loadstates, name='loadstates'),
    path('onBording/', views.onBording, name='onBording'),
    path('ChangePwd/', views.ChangePwd, name='ChangePwd'),

    path('create-campaign/', views.create_campaign, name='createcampaign'),
    # path('create_campaign_new/',views.create_campaign_new, name='create_campaign_new'),
    path('add_campaign_spec/<int:id>',views.add_campaign_spec, name='add_campaign_spec'),
    path('change_campaign_status/<int:id>',views.change_campaign_status, name='change_campaign_status'),

    path('save_lead_validation/',views.save_lead_validation, name='save_lead_validation'),
    path('save_specifications/',views.save_specifications, name='save_specifications'),
    path('save_mapping/',views.save_mapping, name='save_mapping'),
    path('save_terms/',views.save_terms, name='save_terms'),
    path('save_delivery/',views.save_delivery, name='save_delivery'),
    path('save_delivery_method_comments/',views.save_delivery_method_comments, name='save_delivery_method_comments'),
    path('save_alternative_text',views.save_alternative_text, name='save_alternative_text'),
    path('save_volume_and_cpl',views.save_volume_and_cpl, name='save_volume_and_cpl'),
    path('delete_volume_and_cpl',views.delete_volume_and_cpl, name='delete_volume_and_cpl'),

    path('save_selected_components/',views.save_selected_components, name='save_selected_components'),
    path('remove_selected_component/',views.remove_selected_component, name='remove_selected_component'),

    path('edit_campaign/<int:campaign_id>',views.edit_campaign, name='edit_campaign'),
    path('edit_rfq_campaign/<int:campaign_id>',rfq_views.edit_rfq_campaign, name='edit_rfq_campaign'),

    path('clone-campaign/<int:campaign_id>',views.clone_campaign, name='clonecampaign'),
    path('update_c_mandatory_fields/<int:campaign_id>',views.update_c_mandatory_fields, name='update_c_mandatory_fields'),

    path('upload_single_file/',views.upload_single_file, name='upload_single_file'),

    path('test_ajax/',views.test_ajax, name='test_ajax'),

    path('add_default/',views.add_default, name='add_default'),
    path('remove_default/',views.remove_default, name='remove_default'),

    path('changepassword/',views.ChangePwd,name='changepassword'),
    path('view_campaign_details/<int:campaign_id>', views.view_campaign_details, name='view_campaign_details'),
    path('manage-campaign/',views.client_manage_campaign, name='managecampaign'),

    path('live-campaign/',views.client_live_campagin, name='client_live_campagin'),
    path('pause-campaign/',views.client_paused_campagin, name='client_paused_campagin'),
    path('pending-campaign/',views.client_pending_campaign, name='client_pending_campaign'),
    path('completed-campaign/',views.client_completed_campagin, name='client_completed_campagin'),
    path('draft-campaign/',views.client_draft_campagin, name='client_draft_campagin'),
    path('assigned-campaign/',views.client_assigned_campagin, name='client_assigned_campagin'),

	path('client-activity/',views.client_activity, name='client_activity'),
	path('vendor-comparison/',views.vendor_comparison, name='vendor_comparison'),
	path('leads/',views.leads, name='leads'),
	path('campaign-reports/',views.campaignreports, name='campaignreports'),
    path('schedule-reports/',views.schedulereports, name='schedulereports'),
    path('account/',views.account, name='account'),
    path('raise-ticket/',views.raise_ticket, name='raise_ticket'),
    path('contact-us/',views.contactus, name='contactus'),
    path('faq/',views.faq, name='faq'),
    path('terms/',views.terms, name='terms'),
    path('campaigndesc/<int:camp_id>',views_1.campaingdesc,name='campaigndesc'),
    path('vendor-profile/<int:vendor_id>',vendor_views.vendorprofile,name='vendorprofile'),
    path('vendor-list/',views_1.vendor_list,name='vendor_list'),
    path('leadlist/<int:camp_id>/<int:status>',views_1.leadlist,name='leadlist'),
    path('ajax/lead_approve/',views_1.lead_approve,name='lead_approve'),
    path('ajax/lead_rejected/',views_1.lead_rejected,name='lead_approve'),
    path('ajax/lead_rectify/',views_1.lead_rectify,name='lead_rectify'),
    path('ajax/Suggest/',views_1.Suggest,name='Suggest'),
    path('create-demo-campaign/',views_1.create_demo_campaign,name='create-campaign'),
    path('campaign-vendor-list/<int:camp_id>',views_1.campaign_vendor_list,name='campaign-vendor-list'),
    path('ajax/add-vendor/',views_1.add_venodr,name='client-add-vendor'),
    path('vendor-allocation/<int:camp_id>',views_1.vendor_allocation,name='client-vendor-allocation'),
    path('lead_list/<int:camp_id>/<int:status>',views_1.client_lead_list,name='client-lead-upload'),
    path('client_lead_list/<int:camp_id>/<int:status>',views_1.client_lead_list,name='client_lead_list'),
    path('insert_lead/<int:camp_id>/<int:camp_alloc_id>/',views_1.insert_lead,name='client-insert-lead'),
    path('all_lead_display/<int:camp_id>/',views_1.all_lead_display,name='client-display-Alllead'),
    path('campaign-notebook/',views_1.campaign_notebook,name='campaign-notebook'),

    path('script_submit/',views_1.script_submit,name='script_submit'),
    path('ajax/get_scripts/',views_1.get_scripts,name='get_scripts'),
    path('vendor-script-submit/',views_1.vendor_script_submit,name='vendor_script_submit'),

    path('ajax/get_agreements/',views_1.get_agreements,name='get_agreements'),

    path('asset_submit/',views_1.asset_submit,name='asset_submit'),
    path('remove_asset/',views_1.remove_asset,name='remove_asset'),
    path('remove_file_asset/',views_1.remove_file_asset,name='remove_file_asset'),
    path('ajax/get_asset_specs/',views_1.get_asset_specs,name='get_asset_specs'),

    path('ajax/get_camp_data/',views_1.get_camp_data,name='camp_data'),
    path('get-vendor-list/',views_1.get_vendor_list,name='get_vendor_list'),
    path('ajax/get_camp_specs/',views_1.get_camp_specs,name='camp_specs'),
    path('chat-app/<int:camp_id>/',chat_view.campaign_chat_screen,name='chat'),
    path('chat-app/send-msg/',chat_view.send_msg,name='chat'),
    path('get-campaign-chat/',chat_view.get_campaign_chat,name='chat'),
    path('chat-read-notification/',chat_view.chat_read_notification,name='chat'),
    path('get_rfq_cpl/',views_1.get_rfq_cpl,name='get_rfq_cpl'),
    path('update_status_rfq/',views_1.update_status_rfq,name='update_status_rfq'),
    path('RFQ-Campaign/<int:camp_id>/',views_1.RFQ_Campaign,name='RFQ_Campaign'),
    path('rfq_vendor_allocation/',views_1.rfq_vendor_allocation,name='rfq_vendor_allocation'),
    path('update_rfq_cpl/',views_1.update_rfq_cpl,name='update_rfq_cpl'),
    path('counter_action_on_cpl/',views_1.counter_action_on_cpl,name='counter_action_on_cpl'),
    path('individual-campaing-notebook/<int:camp_id>',views_1.individual_campaign_notebook,name="individual_campaign_notebook"),
    path('Rejected-Reason-List/',views_1.rejected_reason_list,name="rejected_reason_list"),
    path('Rectify-Reason-List/',views_1.rectify_reason_list,name="rectify_reason_list"),
    path('client-Bording/',vendor_views.client_Bording,name="client_Bording"),
    path('update-campaign-end-date/', views_1.update_campaign_end_date, name='update_campaign_end_date'),
    path('update-campaign-start-date/', views_1.update_campaign_start_date, name='update_campaign_start_date'),
    path('custom_question/<int:camp_id>', form_view.custom_question, name='custom_question'),
    path('feedback/',views_1.feedback,name='feedback'),

    #path('export_data/<int:camp_id>/<int:vendor_id>/<int:status>/',views_1.export_data,name="export_data"),
    path('create-rfq-campaign/',rfq_views.create_rfq_campaign, name='createcampaign'),
    path('TC-vendor-list/',views_1.TC_vendor_list,name="TC_vendor_list"),
    path('existing-vendor-list/',views_1.existing_vendor_list,name="existing_vendor_list"),

    path('campaign_type/',views.campaigntype,name="campaigntype"),
    path('rfq_vendor_allocation/<int:camp_id>',rfq_views.rfq_vendor_allocation,name="campaigntype"),
    path('get_cpl_list/',views_1.get_cpl_list,name="get_cpl_list"),

    path('client_user_access/',views_1.client_user_access,name="client_user_access"),
    path('get_user_access/',views_1.get_user_access,name="get_user_access"),
    path('grant_group_access/',views_1.grant_group_access,name="grant_group_access"),
    path('grant_child_group_access/',views_1.grant_child_group_access,name="grant_child_group_access"),
    path('grant_grand_child_access/',views_1.grant_grand_child_access,name="grant_grand_child_access"),

    path('json', apilink, name='json'),
    path('leads-export', ApiAccessUserView, name='api-access-user'),
    path('export-login',
         TemplateView.as_view(template_name='api-export/ApiAccessLogin.html')),
    path('exlogout', apilogout, name='apilogout'),
    path('exlogin', ApiAccessUserLogin, name='api-access-user-login'),

    path('user_and_groups/',views_1.user_and_groups,name="user_and_groups"),
    path('ajax/add-group/',views_1.add_group,name='client-add-group'),
    path('ajax/delete-group/',views_1.delete_group,name='client-delete-group'),
    path('ajax/edit-group/',views_1.edit_group,name='client-edit-group'),
    path('ajax/add-user-to-group/',views_1.add_user_to_group,name='add_user_to_group'),
    path('get_group_access/',views_1.get_group_access,name="get_group_access"),
    path('get_group_users/',views_1.get_group_users,name="get_group_users"),
    path('remove_group_user/',views_1.remove_group_user,name="remove_group_user"),

    path('save_lead_limit_cmp',views.save_lead_limit_cmp,name="save_lead_limit_cmp"),
    path('timeout', timeout, name='timeout'),
    path('update-campaign-expiry-date/', rfq_views.update_campaign_expiry_date, name='update-campaign-expiry-date'),
    path('campaign_lifecycle/<int:camp_id>', views.campaign_lifecycle, name='campaign_lifecycle'),
    path('client_invoice/', client_invoice.client_invoice1, name='client_invoice'),
    path('reports', views.reports, name="reports"),

    #history of uploaded lead_data
    path('upload_with_rejected_lead/<int:camp_id>/<int:camp_alloc_id>/',views_1.upload_with_rejected_lead_web,name="lead_error_list"),
    path('upload_without_rejected_lead/<int:camp_id>/<int:camp_alloc_id>/',views_1.upload_without_rejected_lead_web,name="lead_error_list"),
    path('lead_error_list/<int:camp_id>/<int:camp_alloc_id>/',views_1.lead_error_list,name="lead_error_list"),
    #report-lead
    path('leadreports', report_view.leadreports, name="leadreports"),
    path('ajax/get_vendor_list_campaign/', report_view.get_vendor_list_campaign, name="leadreports"),
    path('ajax/get_geo_list_campaign/', report_view.get_geo_list_campaign, name="leadreports"),
    path('ajax/lead_report_table_data/', report_view.lead_report_table_data, name="leadreports"),

    #send attachament
    path('ajax/send_attchment/', chat_view.send_attchment, name="send_attchment"),
    path('vendors_comparison', views.vendors_comparison, name='vendors_comparison'),
    path('custom-datafields/<int:camp_id>/', views.custom_datafield, name='custom_datafields'),
    path('ajax/get-custom-header-csv/', views.get_custom_header_csv, name='get-custom-header-csv'),
    path('ajax/save-custom-header/',views.save_custom_header, name='save-custom-header'),
    path('client_mail_noti', views.noti_via_mail_page, name='client_noti'),
    path('ajax/save_mail_choice/', views.save_mail_choice, name='mail_choice'),
    path('sign/', views.sign, name="sign"),
    path('save_header_choice/',views.save_header_choice, name='save_header_choice'),

    path('check_io/',views.check_io, name='check_io'),
    path('campaign_status', views.new_all_campaigns, name='campaign_status')
]

# urlpatterns = format_suffix_patterns(urlpatterns)
