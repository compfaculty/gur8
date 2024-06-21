import logging

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from asnet.models import CIDRBlock, ScanCIDRBlockJob
from asnet.tasks import process_job

logger = logging.getLogger(__name__)


@method_decorator(require_POST, name="dispatch")  # Restrict to POST requests
class ScanCIDR(View):
    def get_queryset(self):
        return ScanCIDRBlockJob.objects.select_related("cidr_block")

    def post(self, request, pk, *args, **kwargs):
        try:
            cidr = get_object_or_404(CIDRBlock, pk=pk)

            # Check for existing pending or running jobs efficiently
            if self.get_queryset().filter(
                    cidr_block=cidr, status__in=(ScanCIDRBlockJob.STATUS_PENDING, ScanCIDRBlockJob.STATUS_RUNNING)
            ).exists():
                logger.warning(f"Scan already in progress for CIDR {cidr.cidr}")
                messages.warning(request, "A scan is already in progress for this CIDR block.")
                return redirect("asnet:cidr_detail", pk=pk)

            # Create the job and initiate the scan
            job = ScanCIDRBlockJob.objects.create(cidr_block=cidr)
            process_job.send(job.pk, "ScanCIDRBlockJob")

            messages.success(request, "CIDR scan initiated. Results will be available shortly.")
            return redirect("asnet:cidr_detail", pk=pk)  # Redirect to the CIDR detail page

        except Exception as e:
            logger.exception("Error initiating CIDR scan: %s", e)
            messages.error(request, "An error occurred while initiating the scan. Please try again later.")
            return redirect("asnet:cidr_detail", pk=pk)

# import logging
#
# from django.contrib import messages
# from django.shortcuts import redirect, get_object_or_404
# from django.views import View
#
# from asnet.models import CIDRBlock, ScanCIDRBlockJob
# from asnet.tasks import process_job  # Import your dramatiq task
#
# logger = logging.getLogger(__name__)
#
#
# class ScanCIDR(View):
#     def get(self, request, pk, *args, **kwargs):
#         # Trigger the dramatiq task
#         print(f"PK: {pk}")
#         cidr = get_object_or_404(CIDRBlock, pk=pk)
#         # jobs = ScanCIDRBlockJob.objects.filter(pk=pk).all()
#         # if jobs:
#         #     for job in jobs:
#         #         if job.status in (ScanCIDRBlockJob.STATUS_PENDING, ScanCIDRBlockJob.STATUS_RUNNING):
#         #             logger.warning(f"Scan already in progress for CIDR {cidr.cidr}")
#         #     return redirect('asnet:cidr_detail', pk=pk)
#         job = ScanCIDRBlockJob.objects.create(cidr_block=cidr)
#         process_job.send(job.pk, "ScanCIDRBlockJob")
#
#         # Inform the user that the scan has started
#         messages.info(request, "CIDR scan initiated. Results will be available shortly.")
#
#         # Redirect to a relevant page or render a response
#         return redirect('asnet:index')
#         # or return render(request, 'some_template.html', context)
