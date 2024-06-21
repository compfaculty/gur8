from django.utils import timezone
from django.views import generic

from asnet.forms import ScanIpHostForm
from asnet.models import IpHost


class IpHostDetailView(generic.DetailView):
    """
    View to display detailed information about an IP host,
    with enhancements for performance, context, interactions, and user experience.
    """

    model = IpHost
    template_name = "asnet/ip_host_detail.html"
    context_object_name = "ip_host"  # Explicitly set for clarity

    # Optimized queryset for efficiency
    def get_queryset(self):
        return IpHost.objects.select_related(
            "cidr_block", "services__vulnerabilities"
        ).prefetch_related("services", "scans").filter(published__lte=timezone.now()).order_by("-published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add extra context variables
        context["scan_form"] = ScanIpHostForm()  # Clear form variable name
        context["scan_history"] = self.object.scans.all().order_by("-started_at")  # Display scan history
        context["related_hosts"] = self.object.cidr_block.ip_hosts.exclude(pk=self.object.pk)  # Show other hosts in the CIDR block

        return context
