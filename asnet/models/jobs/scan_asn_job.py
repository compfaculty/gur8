from django.db import models
from django.utils import timezone

from asnet.models import AutonomousSystem
from asnet.models.jobs.abstract_job import AbstractJob
from asnet.tasks import create_cidr_blocks_for_asn


class ScanAsnJob(AbstractJob):
    asn = models.ForeignKey(
        AutonomousSystem,
        related_name="jobs",
        on_delete=models.CASCADE,
        verbose_name="Autonomous System",
    )

    class Meta:
        verbose_name = "Scan Autonomous System Job"

    def __str__(self):
        return f"{self.id} - {self.asn} - {self.created_at} - {self.status}"

    def process(self):
        self.status = self.STATUS_PENDING
        self.start_time = timezone.now()  # Track job start time
        self.save()
        create_cidr_blocks_for_asn.send(self.pk, self.asn)

# from django.db import models
#
# from asnet.models import AutonomousSystem
# from asnet.models.jobs.abstract_job import AbstractJob
# from asnet.tasks import create_cidr_blocks_for_asn
#
#
# class ScanAsnJob(AbstractJob):
#     asn = models.ForeignKey(AutonomousSystem, related_name='jobs',
#                             on_delete=models.CASCADE, verbose_name="Autonomous System")
#
#     class Meta:
#         verbose_name = "Scan Autonomous System Job"
#
#     def __str__(self):
#         return f"{self.id} - {self.asn} - {self.created_at} - {self.status}"
#
#     def process(self):
#         create_cidr_blocks_for_asn.send(self.pk, self.asn)
