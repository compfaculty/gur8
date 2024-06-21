import logging
from datetime import datetime

# import nmap
from django.db import models

from asnet.models.ip_host import IpHost
from asnet.models.jobs.abstract_job import AbstractJob
from asnet.models.jobs.vars import TOP_PORTS

logger = logging.getLogger(__name__)


class ScanIpHostJob(AbstractJob):
    SCAN_TYPES = [
        ('nmap', 'Nmap'),
        ('scan2', 'Scan Type 2'),
        ('scan3', 'Scan Type 3'),
        # Add more scan types as needed
    ]

    ip = models.ForeignKey(IpHost, related_name='jobs',
                           on_delete=models.CASCADE, verbose_name="IP Host")
    scan = models.CharField(max_length=50, choices=SCAN_TYPES, verbose_name="Scan Type", default='nmap')

    class Meta:
        verbose_name = "Scan IP Target Job"

    def __str__(self):
        return f"{self.id} - {self.ip} - {self.scan} - {self.created_at} - {self.status}"

    # def process(self):
    #     ip_address = self.ip.ip
    #     # send ip to nmap and return services information
    #     import subprocess

    def process(self):
        url = None
        ip_addr = self.ip.ip
        # send ip to nmap and return services information
        # result = subprocess.run(
        #     ["nmap", "-p", ",".join((str(port) for port in TOP_PORTS)), "-T4", "-sCV", "-oG", "-", ip_addr],
        #     capture_output=True, text=True)
        print(self.scan)
        match self.scan:
            case "nmap":
                print("nmap")

            case "Python":
                print("You can become a Data Scientist")

            case "PHP":
                print("You can become a backend developer")

            case "Solidity":
                print("You can become a Blockchain developer")

            case "Java":
                print("You can become a mobile app developer")
            case _:
                print("The language doesn't matter, what matters is solving problems.")

        # nm = nmap.PortScanner()
        try:
            ports = ",".join((str(port) for port in TOP_PORTS))
            # nm.scan(hosts=ip_addr, arguments=f'-Pn -sS -p {ports} --open')
            # for port in nm[ip_addr]['tcp'].keys():
            #     if nm[ip_addr].tcp(port)['name'] == 'http':
            #         self.ip.http_title, url = nmap_get_title(ip_addr, port)
            #     if nm[ip_addr].tcp(port)['name'] == 'https':
            #         self.ip.https_title, url = nmap_get_title(ip_addr, port)
            #     if url:
            #         self.ip.host_domain = url

        except Exception as e:
            logger.error(f"An error {ip_addr} occurred: {e}")
        finally:
            self.ip.last_scanned = datetime.now()
            self.ip.save()
