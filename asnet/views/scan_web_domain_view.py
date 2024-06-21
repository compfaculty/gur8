import logging

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from asnet.forms import ScanWebDomainForm
from asnet.models import ScanWebDomainJob, WebDomain
from asnet.tasks import process_job

logger = logging.getLogger(__name__)


@method_decorator(require_POST, name="dispatch")  # Restrict to POST requests
class ScanWebDomain(View):
    def get_queryset(self):
        return ScanWebDomainJob.objects.select_related("site")

    def post(self, request, pk, *args, **kwargs):
        try:
            web_domain = get_object_or_404(WebDomain, pk=pk)
            form = ScanWebDomainForm(request.POST)
            if form.is_valid():
                selected_scans = form.cleaned_data["scans"]

                # Check for existing pending or running jobs and remove them from selected scans
                running_scans = self.get_queryset().filter(
                    site=web_domain, scan__in=selected_scans,
                    status__in=(ScanWebDomainJob.STATUS_PENDING, ScanWebDomainJob.STATUS_RUNNING)
                ).values_list("scan", flat=True)

                selected_scans = [scan for scan in selected_scans if scan not in running_scans]

                if running_scans:
                    logger.warning(f"Some scans are already in progress for web domain {web_domain.url}")
                    messages.warning(request,
                                     f"Some of the selected scans ({', '.join(running_scans)}) are already in progress.")

                # Proceed with creating jobs for the remaining scans
                for scan in selected_scans:
                    # Create and process the scan job
                    job = ScanWebDomainJob.objects.create(site=web_domain, scan=scan)
                    process_job.send(job.pk, "ScanWebDomainJob")  # Adjust arguments as needed
                    messages.info(request, f"Scan {scan} initiated for Web Domain {web_domain.url}.")
            # if form.is_valid():
            #     selected_scans = form.cleaned_data["scans"]
            #
            #     # Check for existing pending or running jobs efficiently
            #     if self.get_queryset().filter(
            #             site=web_domain, scan__in=selected_scans,
            #             status__in=(ScanWebDomainJob.STATUS_PENDING, ScanWebDomainJob.STATUS_RUNNING)
            #     ).exists():
            #         logger.warning(f"Some scans are already in progress for web domain {web_domain.url}")
            #         messages.warning(request,
            #                          f"Some of the selected scans are already in progress for this web domain.")
            #     else:
            #         # Create jobs and initiate scans for selected scans
            #         for scan in selected_scans:
            #             job = ScanWebDomainJob.objects.create(site=web_domain, scan=scan)
            #             process_job.send(job.pk, "ScanWebDomainJob")  # Adjust arguments as needed
            #             messages.info(request, f"Scan {scan} initiated for Web Domain {web_domain.url}.")

            else:
                messages.error(request, "Invalid scan selection. Please try again.")

        except Exception as e:
            logger.exception("Error initiating scan: %s", e)
            messages.error(request, "An error occurred while initiating the scan. Please try again later.")

        return redirect("asnet:web_domain_detail", pk=pk)

# import logging
#
# from django.contrib import messages
# from django.shortcuts import redirect, get_object_or_404
# from django.views import View
#
# from asnet.forms import ScanWebDomainForm
# from asnet.models import ScanWebDomainJob, WebDomain
# from asnet.tasks import process_job  # Import your dramatiq task
#
# logger = logging.getLogger(__name__)
#
#
# class ScanWebDomain(View):
#     @staticmethod
#     def get(request, pk, *args, **kwargs):
#         web_domain = get_object_or_404(WebDomain, pk=pk)
#         jobs = ScanWebDomainJob.objects.filter(site=web_domain.pk).all()
#         if jobs:
#             for job in jobs:
#                 if job.status in (ScanWebDomainJob.STATUS_PENDING, ScanWebDomainJob.STATUS_RUNNING):
#                     logger.warning(f"Scan already in progress for web domain {web_domain.url}")
#             messages.info(request, f"Web domain scan {web_domain.url} already in progress...")
#             return redirect('asnet:web_domain_detail', pk=pk)
#         job = ScanWebDomainJob.objects.create(site=web_domain, scan="default")
#         process_job.send(job.pk, "ScanWebDomainJob")
#
#         # Inform the user that the scan has started
#         messages.info(request, f"Web domain scan {web_domain.url} initiated. Results will be available shortly.")
#
#         return redirect('asnet:web_domain_detail', pk=pk)
#
#     @staticmethod
#     def post(request, pk, *args, **kwargs):
#         web_domain = get_object_or_404(WebDomain, pk=pk)
#         form = ScanWebDomainForm(request.POST)
#
#         if form.is_valid():
#             selected_scans = form.cleaned_data['scans']
#
#             for scan in selected_scans:
#                 # Create and process the scan job
#                 job = ScanWebDomainJob.objects.create(site=web_domain, scan=scan)
#                 process_job.send(job.pk, "ScanWebDomainJob")
#
#                 messages.info(request, f"Scan {scan} initiated for Web Domain {web_domain.url}.")
#
#         return redirect('asnet:web_domain_detail', pk=pk)
