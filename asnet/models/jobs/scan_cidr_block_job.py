import logging
import time

# import nmap
from django.db import models, transaction
from django.utils import timezone

from asnet.models import IpHost, NetworkService
from asnet.models.cidr_block import CIDRBlock
from asnet.models.jobs.abstract_job import AbstractJob
from asnet.models.jobs.vars import TOP_PORTS, USER_AGENT

logger = logging.getLogger(__name__)


class ScanCIDRBlockJob(AbstractJob):
    cidr_block = models.ForeignKey(
        CIDRBlock,
        related_name="jobs",
        on_delete=models.CASCADE,
        verbose_name="CIDR Block",
    )

    class Meta:
        verbose_name = "Scan CIDR Block Job"

    def __str__(self):
        return f"{self.id} - {self.cidr_block} - {self.created_at} - {self.status}"

    def process(self):
        start_time = time.time()  # Track job execution time
        self.status = self.STATUS_PENDING
        self.start_time = timezone.now()  # Track job start time
        self.save()

        try:
            pass
            # with transaction.atomic():  # Ensure database consistency
            #     ports = ",".join((str(port) for port in TOP_PORTS))
            #     nm = nmap.PortScanner()
            #
            #     # Performing a stealthy ping scan
            #     nm.scan(
            #         hosts=self.cidr_block.cidr,
            #         arguments=f'-Pn -sCV -p {ports} --open --script-args useragent="{USER_AGENT},max-redirects=10"',
            #     )
            #
            #     # Efficiently create IpHost and NetworkService instances
            #     hosts_and_services = []
            #     for host in nm.all_hosts():
            #         if nm[host].state() == "up":
            #             ip_host = IpHost(
            #                 ip=host,
            #                 cidr_id=self.cidr_block.pk,
            #                 description=self.cidr_block.autonomous_system.name,
            #             )
            #             services = []
            #             for port in nm[host].all_tcp():
            #                 data = nm[host].tcp(port)
            #                 scripts = data["script"]
            #                 services.append(
            #                     NetworkService(
            #                         # ... (all fields as in the original code)
            #                     )
            #                 )
            #             hosts_and_services.append((ip_host, services))
            #
            #     IpHost.objects.bulk_create([host for host, _ in hosts_and_services])
            #     NetworkService.objects.bulk_create(
            #         [service for _, services in hosts_and_services for service in services]
            #     )
            #
            #     for ip_host, services in hosts_and_services:
            #         ip_host.services.add(*services)  # Associate services in a single query
            #
            # self.cidr_block.is_scanned = True
            # self.cidr_block.save()
            # self.status = self.STATUS_DONE
            # self.end_time = timezone.now()
            # self.duration = time.time() - start_time  # Calculate job duration
            # self.save()

        except Exception as e:
            logger.error(f"An error occurred:", e)
            self.status = self.STATUS_FAILED
            self.save()

# import logging
#
# import nmap
# from django.db import models
#
# from asnet.models import IpHost, NetworkService
# from asnet.models.cidr_block import CIDRBlock
# from asnet.models.jobs.abstract_job import AbstractJob
# from asnet.models.jobs.vars import TOP_PORTS, USER_AGENT
#
# logger = logging.getLogger(__name__)
#
#
# class ScanCIDRBlockJob(AbstractJob):
#     cidr_block = models.ForeignKey(CIDRBlock, related_name='jobs',
#                                    on_delete=models.CASCADE, verbose_name="CIDR Block")
#
#     class Meta:
#         verbose_name = "Scan CIDR Block Job"
#
#     def __str__(self):
#         return f"{self.id} - {self.cidr_block} - {self.created_at} - {self.status}"
#
#     def process(self):
#         ports = ",".join((str(port) for port in TOP_PORTS))
#         nm = nmap.PortScanner()
#         try:
#             # Performing a stealthy ping scan
#             nm.scan(hosts=self.cidr_block.cidr,
#                     arguments=f'-Pn -sCV -p {ports} --open --script-args useragent="{USER_AGENT},max-redirects=10"')
#
#             # Check if any host is up
#             for host in nm.all_hosts():
#                 # Step 1: Create and save an IpHost instance
#                 logger.info(f"Processing {host}...")
#                 if nm[host].state() == 'up':
#                     ip_host = IpHost(ip=host, cidr_id=self.cidr_block.pk,
#                                      description=self.cidr_block.autonomous_system.name)
#                     ip_host.save()
#                     # Step 2: Bulk create NetworkService instances
#                     services = []
#                     for port in nm[host].all_tcp():
#                         data = nm[host].tcp(port)
#                         scripts = data['script']
#
#                         services.append(NetworkService(
#                             name=data['name'],
#                             port=port,
#                             product=data['product'],
#                             version=data['version'],
#                             extrainfo=data['extrainfo'],
#                             conf=data['conf'],
#                             cpe=data['cpe'],
#                             http_server_header=scripts.get('http-server-header', ""),
#                             http_title=scripts.get('http-title', ""),
#                             http_favicon=scripts.get('http-favicon', ""),
#                             http_robots=scripts.get('http-robots', ""),
#                             http_methods=scripts.get('http-methods', ""),
#                             http_cookie_flags=scripts.get('http-cookie-flags', ""),
#                             fingerprint_strings=scripts.get('fingerprint', ""),
#                             ssl_date=scripts.get('ssl-date', ""),
#                             ssl_hostkey=scripts.get('ssl-hostkey', ""),
#                             ssl_cert=scripts.get('ssl-cert', ""),
#                             tls_alpn=scripts.get('tls-alpn', ""),
#                         ))
#
#                     NetworkService.objects.bulk_create(services)
#
#                     # Step 3: Retrieve the created NetworkService instances
#                     # Here, we're assuming 'service_property1' is a unique identifier for each service
#                     service_identifiers = [data.pk for data in services]
#                     created_services = NetworkService.objects.filter(pk__in=service_identifiers)
#
#                     # Step 4: Associate the NetworkService instances with the IpHost instance
#                     ip_host.services.add(*created_services)
#
#         except Exception as e:
#             logger.error(f"An error occurred:", e)
#
#         self.cidr_block.is_scanned = True
#         self.cidr_block.save()

    # def process(self):
    #     ips = is_host_up_in_cidr(self.cidr_block.cidr)
    #     for ip in ips:
    #         print(f"IP {ip} is up")
    #         IpHost.objects.create(ip=ip, cidr_id=self.cidr_block.pk, description=self.cidr_block.autonomous_system.name)
    #     self.cidr_block.is_scanned = True
    #     self.cidr_block.save()
