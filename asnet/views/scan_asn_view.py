import logging

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from asnet.models import ScanCIDRBlockJob, AutonomousSystem
from asnet.tasks import process_job

logger = logging.getLogger(__name__)


@method_decorator(require_POST, name="dispatch")  # Restrict to POST requests
class ScanASN(View):
    def get_queryset(self):
        return ScanCIDRBlockJob.objects.select_related("cidr_block__autonomous_system")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add relevant context variables for the template, if needed
        return context

    def get(self, request, pk, *args, **kwargs):
        # Redirect to a more appropriate view for GET requests
        return redirect("asnet:asn_detail", pk=pk)

    def post(self, request, pk, *args, **kwargs):
        try:
            asn = get_object_or_404(AutonomousSystem, pk=pk)

            # Check for existing pending or running jobs efficiently
            if self.get_queryset().filter(
                    cidr_block__in=asn.cidr_blocks.all(),
                    status__in=(ScanCIDRBlockJob.STATUS_PENDING, ScanCIDRBlockJob.STATUS_RUNNING),
            ).exists():
                logger.warning(f"Scan already in progress for ASN {asn.asn}")
                messages.warning(request, "A scan is already in progress for this ASN.")
                return redirect("asnet:asn_detail", pk=pk)

            # Create or retrieve jobs for CIDR blocks with optimized querysets
            for cidr_block in asn.cidr_blocks.all():
                job, _ = ScanCIDRBlockJob.objects.get_or_create(cidr_block=cidr_block)
                process_job.send(job.pk, "ScanCIDRBlockJob")

            messages.success(request, "ASN scan initiated. Results will be available shortly.")
            return redirect("asnet:asn_detail", pk=pk)  # Redirect to the ASN detail page

        except Exception as e:
            logger.exception("Error initiating ASN scan: %s", e)
            messages.error(request, "An error occurred while initiating the scan. Please try again later.")
            return redirect("asnet:asn_detail", pk=pk)

# class ScanASN(View):
#     def get(self, request, pk, *args, **kwargs):
#         # Trigger the dramatiq task
#         print(f"PK: {pk}")
#         asn = get_object_or_404(AutonomousSystem, pk=pk)
#         jobs = ScanCIDRBlockJob.objects.filter(cidr_block__in=asn.cidr_blocks.all()).all()
#         if jobs:
#             for job in jobs:
#                 if job.status in (ScanCIDRBlockJob.STATUS_PENDING, ScanCIDRBlockJob.STATUS_RUNNING):
#                     logger.warning(f"Scan already in progress for ASN {asn.asn}")
#             return redirect('asnet:index')
#         for cidr_block in asn.cidr_blocks.all():
#             # ScanCIDRBlockJob.objects.create(cidr_block=cidr_block.pk)
#             job, _ = ScanCIDRBlockJob.objects.get_or_create(cidr_block=cidr_block)
#             process_job.send(job.pk, "ScanCIDRBlockJob")
#
#         # Inform the user that the scan has started
#         messages.info(request, "ASN scan initiated. Results will be available shortly.")
#
#         # Redirect to a relevant page or render a response
#         return redirect('asnet:asn_detail', pk=pk)
#         # or return render(request, 'some_template.html', context)
