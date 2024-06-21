from django.contrib import admin

from asnet.models import CIDRBlock, AutonomousSystem, IpHost, ScanCIDRBlockJob, ScanIpHostJob, WebDomain
from asnet.models.jobs.scan_asn_job import ScanAsnJob
from asnet.models.jobs.scan_web_domain_job import ScanWebDomainJob


# Register your models here.

class CIDRBlocksInLine(admin.StackedInline):
    model = CIDRBlock
    extra = 2


class AutonomousSystemAdmin(admin.ModelAdmin):
    list_display = ('asn', 'name', 'description', 'published')  # Fields to display

    # fieldsets = [
    #     (None, {"fields": ["asn"]}),
    #     ("ANS Information", {"fields": ["name", "description"]}),
    #     ("Published", {"fields": ["published"], "classes": ["collapse"]}),
    # ]
    inlines = [CIDRBlocksInLine]


class CIDRBlockAdmin(admin.ModelAdmin):
    list_display = ('cidr', 'autonomous_system', 'published', 'is_scanned', 'live_hosts_in_cidr')  # Added method


class IpHostAdmin(admin.ModelAdmin):
    list_display = ('ip', 'name', 'description', 'cidr', 'published')  # Fields to display


class WebDomainAdmin(admin.ModelAdmin):
    list_display = ('url', 'description', 'published')  # Fields to display


class ScanCIDRBlockJobAdmin(admin.ModelAdmin):
    list_display = ('status', 'cidr_block', 'error_message', 'created_at')


class ScanAsnJobAdmin(admin.ModelAdmin):
    list_display = ('status', 'asn', 'error_message', 'created_at')


class ScanIpHostJobAdmin(admin.ModelAdmin):
    list_display = ('status', 'ip', 'error_message', 'created_at')


class ScanWebDomainJobAdmin(admin.ModelAdmin):
    list_display = ('status', 'site', 'error_message', 'created_at')


# ASN
admin.site.register(AutonomousSystem, AutonomousSystemAdmin)
admin.site.register(ScanAsnJob, ScanAsnJobAdmin)
# CIDR
admin.site.register(CIDRBlock, CIDRBlockAdmin)
admin.site.register(ScanCIDRBlockJob, ScanCIDRBlockJobAdmin)
# IPHost
admin.site.register(IpHost, IpHostAdmin)
admin.site.register(ScanIpHostJob, ScanIpHostJobAdmin)

# WebDomain
admin.site.register(WebDomain, WebDomainAdmin)
admin.site.register(ScanWebDomainJob, ScanWebDomainJobAdmin)
