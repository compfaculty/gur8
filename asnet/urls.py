from django.urls import path

from asnet.views import AutonomousSystemDetailView, IndexView, CIDRBlockDetailView, CIDRBlockListView, \
    IpHostDetailView, IpHostListView, ScanCIDR, ScanIpHost, ScanASN, AutonomousSystemListView, ScanWebDomain, \
    WebDomainDetailView, WebDomainListView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("asn/<int:pk>", AutonomousSystemDetailView.as_view(), name="asn_detail"),
    path("asn/<int:pk>/scan", ScanASN.as_view(), name="asn_scan"),
    path("asn/", AutonomousSystemListView.as_view(), name="asn_list_view"),

    path("cidr/<int:pk>", CIDRBlockDetailView.as_view(), name="cidr_detail"),
    path("cidr/<int:pk>/scan", ScanCIDR.as_view(), name="cidr_scan"),
    path("cidr/", CIDRBlockListView.as_view(), name="cidr_list"),

    path("iphost/<int:pk>/scan", ScanIpHost.as_view(), name="ip_host_scan"),
    path("iphost/<int:pk>", IpHostDetailView.as_view(), name="ip_host_detail"),
    path("iphost/", IpHostListView.as_view(), name="ip_host_list"),

    path("web/<int:pk>/scan", ScanWebDomain.as_view(), name="web_domain_scan"),
    path("web/<int:pk>", WebDomainDetailView.as_view(), name="web_domain_detail"),
    path("web/", WebDomainListView.as_view(), name="web_domain_list"),
]

app_name = "asnet"
