import logging
from datetime import datetime

from django.db import models

from asnet.models import WebDomain
from asnet.models.jobs.abstract_job import AbstractJob
# from asnet.external_api.urlscanio import urlscanio_main
logger = logging.getLogger(__name__)


class ScanWebDomainJob(AbstractJob):
    SCAN_TYPES = [
        ('nuclei', 'nuclei'),
        ('urlscanio', 'urlscan.io'),
        ('scan3', 'Scan Type 3'),
        # Add more scan types as needed
    ]

    site = models.ForeignKey(WebDomain, related_name='jobs',
                             on_delete=models.CASCADE, verbose_name="Web Domain Host")
    scan = models.CharField(max_length=50, choices=SCAN_TYPES, verbose_name="Scan Type", default='nuclei')

    class Meta:
        verbose_name = "Scan Web Domain Job"

    def __str__(self):
        return f"{self.id} - {self.site} - {self.scan} - {self.created_at} - {self.status}"

    # def process(self):
    #     ip_address = self.ip.ip
    #     # send ip to nmap and return services information
    #     import subprocess

    def process(self):
        site_url = self.site.url
        try:
            match self.scan:
                case "nuclei":
                    print("nuclei")
                case "urlscanio":
                    # report = urlscanio_main(site_url)
                    report = None
                    if report:
                        print(report)
                        self.site.report_urlscanio = report
                        self.site.save()

                case _:
                    print("The language doesn't matter, what matters is solving problems.")

        except Exception as e:
            logger.error(f"An error {site_url} occurred: {e}")
        finally:
            self.site.last_scanned = datetime.now()
            self.site.save()
