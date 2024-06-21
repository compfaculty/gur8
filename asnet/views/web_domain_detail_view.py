import logging

from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.views import generic

from asnet.forms import ScanWebDomainForm
from asnet.models import ScanWebDomainJob, WebDomain
from asnet.tasks import process_job  # Import your dramatiq task

logger = logging.getLogger(__name__)


class WebDomainDetailView(generic.DetailView):
    model = WebDomain
    template_name = "asnet/web_domain_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ScanWebDomainForm()
        context["scan_jobs"] = ScanWebDomainJob.objects.filter(site=self.object).order_by("-created_at")
        context["recent_scans"] = context["scan_jobs"].filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=1))
        return context

    def post(self, request, pk, *args, **kwargs):
        self.object = self.get_object()  # Retrieve the WebDomain object
        form = ScanWebDomainForm(request.POST)

        if form.is_valid():
            try:
                selected_scans = form.cleaned_data["scans"]

                # Check for existing pending or running jobs and remove them from selected scans
                running_scans = ScanWebDomainJob.objects.filter(
                    site=self.object, scan__in=selected_scans,
                    status__in=(ScanWebDomainJob.STATUS_PENDING, ScanWebDomainJob.STATUS_RUNNING)
                ).values_list("scan", flat=True)

                selected_scans = [scan for scan in selected_scans if scan not in running_scans]

                if running_scans:
                    messages.warning(request,
                                     f"Some of the selected scans ({', '.join(running_scans)}) are already in progress.")

                # Create jobs and initiate scans for the remaining scans
                for scan in selected_scans:
                    job = ScanWebDomainJob.objects.create(site=self.object, scan=scan)
                    process_job.send(job.pk, "ScanWebDomainJob")  # Adjust arguments as needed
                    messages.info(request, f"Scan {scan} initiated for Web Domain {self.object.url}.")

            except Exception as e:
                messages.error(request, "An error occurred while initiating the scan. Please try again later.")
                logger.exception("Error initiating scan: %s", e)

        return redirect("asnet:web_domain_detail", pk=pk)  # Redirect to the same detail page

# from django.views import generic
#
# from asnet.forms import ScanWebDomainForm
# from asnet.models import WebDomain
#
#
# class WebDomainDetailView(generic.DetailView):
#     model = WebDomain
#     template_name = "asnet/web_domain_detail.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         form = ScanWebDomainForm()
#         context['form'] = form
#         return context
