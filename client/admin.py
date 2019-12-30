from django.contrib import admin
from django.apps import apps
from .models import *

@admin.register(UseAsTxtMapping)
class UseAsTxtMappingAdmin(admin.ModelAdmin):
	list_display = ("campaign", "original_txt", "alternative_txt")


@admin.register(ComponentsList)
class ComponentsListAdmin(admin.ModelAdmin):
	list_display = ("label", "invoke_div", "position", "is_default", "category", "extra_css_class")


@admin.register(SelectedComponents)
class SelectedComponentsAdmin(admin.ModelAdmin):
	list_display = ("campaign", "component")

@admin.register(external_vendor)
class ExternalVendorAdmin(admin.ModelAdmin):
	list_display = ("client_id", "user")

@admin.register(SetDefault)
class SetDefaultAdmin(admin.ModelAdmin):
	list_display = ("field", "values", "user")

@admin.register(ApiAccessUsers)
class ApiAccessUsersAdmin(admin.ModelAdmin):
	list_display = ("client_id", "email", "token")

@admin.register(ApiLinks)
class ApiLinkadmin(admin.ModelAdmin):
	list_display = ('id', 'links')
	list_display_links = ('links',)


@admin.register(LeadValidationComponents)
class LeadValidationComponents(admin.ModelAdmin):
	list_display = ('label','function_name','position','is_default')

@admin.register(SelectedLeadValidation)
class SelectedLeadValidation(admin.ModelAdmin):
	list_display = ("campaign", "component_list")

@admin.register(HeaderSpecsValidation)
class HeaderSpecsValidation(admin.ModelAdmin):
	list_display = ("campaign", "company_limit")

@admin.register(HeadersValidation)
class HeadersValidation(admin.ModelAdmin):
	list_display = ("email_list","company_limit")

@admin.register(CampaignTrack)
class CampaignTrackAdmin(admin.ModelAdmin):
	list_display = ("campaign",)

@admin.register(Document)
class Document(admin.ModelAdmin):
	list_display = ("description",)