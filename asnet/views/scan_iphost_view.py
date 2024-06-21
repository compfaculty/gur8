import logging

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from asnet.forms import ScanIpHostForm
from asnet.models import IpHost, ScanIpHostJob
from asnet.tasks import process_job

logger = logging.getLogger(__name__)


@method_decorator(require_POST, name="dispatch")  # Restrict to POST requests
class ScanIpHost(View):
    def get_queryset(self):
        return ScanIpHostJob.objects.select_related("ip")

    def post(self, request, pk, *args, **kwargs):
        try:
            host = get_object_or_404(IpHost, pk=pk)
            form = ScanIpHostForm(request.POST)
            if form.is_valid():
                selected_scans = form.cleaned_data["scans"]

                # Check for existing pending or running jobs and remove them from selected scans
                running_scans = self.get_queryset().filter(
                    ip=host, scan__in=selected_scans,
                    status__in=(ScanIpHostJob.STATUS_PENDING, ScanIpHostJob.STATUS_RUNNING)
                ).values_list("scan", flat=True)

                selected_scans = [scan for scan in selected_scans if scan not in running_scans]

                if running_scans:
                    logger.warning(f"Some scans are already in progress for IP host {host.ip}")
                    messages.warning(request,
                                     f"Some of the selected scans ({', '.join(running_scans)}) are already in progress.")

                # Proceed with creating jobs for the remaining scans
                for scan in selected_scans:
                    # Create and process the scan job
                    job = ScanIpHostJob.objects.create(ip=host, scan=scan)
                    process_job.send(job.pk, "ScanIpHostJob")  # Adjust arguments as needed
                    messages.info(request, f"Scan {scan} initiated for IP Host {host.ip}.")

            # if form.is_valid():
            #     selected_scans = form.cleaned_data["scans"]
            #
            #     # Check for existing pending or running jobs efficiently
            #     if self.get_queryset().filter(
            #             ip=host, scan__in=selected_scans,
            #             status__in=(ScanIpHostJob.STATUS_PENDING, ScanIpHostJob.STATUS_RUNNING)
            #     ).exists():
            #         logger.warning(f"Some scans are already in progress for IP host {host.ip}")
            #         messages.warning(request, f"Some of the selected scans are already in progress for this IP host.")
            #     else:
            #         # Create jobs and initiate scans for selected scans
            #         for scan in selected_scans:
            #             job = ScanIpHostJob.objects.create(ip=host, scan=scan)
            #             process_job.send(job.pk, "ScanIpHostJob")  # Adjust arguments as needed
            #             messages.info(request, f"Scan {scan} initiated for IP Host {host.ip}.")

            else:
                messages.error(request, "Invalid scan selection. Please try again.")

        except Exception as e:
            logger.exception("Error initiating scan: %s", e)
            messages.error(request, "An error occurred while initiating the scan. Please try again later.")

        return redirect("asnet:ip_host_detail", pk=pk)

# import logging
#
# from django.contrib import messages
# from django.shortcuts import redirect, get_object_or_404
# from django.views import View
#
# from asnet.forms import ScanIpHostForm
# from asnet.models import IpHost, ScanIpHostJob
# from asnet.tasks import process_job  # Import your dramatiq task
#
# logger = logging.getLogger(__name__)
#
#
# class ScanIpHost(View):
#     def get(self, request, pk, *args, **kwargs):
#         host = get_object_or_404(IpHost, pk=pk)
#         jobs = ScanIpHostJob.objects.filter(ip=host.pk).all()
#         if jobs:
#             for job in jobs:
#                 if job.status in (ScanIpHostJob.STATUS_PENDING, ScanIpHostJob.STATUS_RUNNING):
#                     logger.warning(f"Scan already in progress for IP host {host.ip}")
#             messages.info(request, f"IP Host scan {host.ip} already in progress...")
#             return redirect('asnet:ip_host_detail', pk=pk)
#         job = ScanIpHostJob.objects.create(ip=host)
#         process_job.send(job.pk, "ScanIpHostJob")
#
#         # Inform the user that the scan has started
#         messages.info(request, f"IP Host scan {host.ip} initiated. Results will be available shortly.")
#
#         return redirect('asnet:ip_host_detail', pk=pk)
#
#     def post(self, request, pk, *args, **kwargs):
#         host = get_object_or_404(IpHost, pk=pk)
#         form = ScanIpHostForm(request.POST)
#
#         if form.is_valid():
#             selected_scans = form.cleaned_data['scans']
#
#             for scan in selected_scans:
#                 # Create and process the scan job
#                 job = ScanIpHostJob.objects.create(ip=host, scan=scan)
#                 process_job.send(job.pk, "ScanIpHostJob")
#
#                 messages.info(request, f"Scan {scan} initiated for IP Host {host.ip}.")
#
#         return redirect('asnet:ip_host_detail', pk=pk)
#         # # Check which scans were selected
#         # selected_scans = request.POST.getlist('scans')  # 'scans' is the name of your input field
#         #
#         # for scan in selected_scans:
#         #     job = ScanIpHostJob.objects.create(ip=host, scan_type=scan)
#         #     process_job.send(job.pk, scan)  # Adjust the arguments as needed for your task
#         #
#         #     messages.info(request, f"Scan {scan} initiated for IP Host {host.ip}.")
#         #
#         # return redirect('asnet:ip_host_detail', pk=pk)
