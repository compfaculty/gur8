from datetime import datetime

from django.db import models
from taggit.managers import TaggableManager

from asnet.models.cidr_block import CIDRBlock
from asnet.models.network_services.network_service import NetworkService


class IpHost(models.Model):
    """
       Represents an individual IP host within a network.

       Stores various information about the host, including its IP address,
       hostname, services, and status.
       """

    ip = models.GenericIPAddressField(
        verbose_name="IP",
        help_text="The IP address of the host",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Name",
        default="",
        help_text="The hostname or descriptive name of the host",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description",
        default="",
        help_text="Additional details or information about the host",
    )

    published = models.DateTimeField(
        "Published",
        auto_now_add=True,
        help_text="Timestamp when the host was first created in the database",
    )

    services_info = models.TextField(
        blank=True,
        verbose_name="Services Info",
        default="",
        help_text="Textual information about services running on the host",
    )

    http_title = models.CharField(
        max_length=512,
        blank=True,
        verbose_name="HTTP Title",
        default="",
        help_text="The title of the HTTP response if a web server is running on port 80",
    )

    https_title = models.CharField(
        max_length=512,
        blank=True,
        verbose_name="HTTP SSL Title",
        default="",
        help_text="The title of the HTTPS response if a web server is running on port 443",
    )

    host_domain = models.CharField(
        max_length=512,
        blank=True,
        verbose_name="Host Domain",
        default="",
        help_text="The domain name associated with the host, if applicable",
    )

    is_alive = models.BooleanField(
        default=False,
        auto_created=True,
        verbose_name="Is Alive",
        help_text="Indicates whether the host is currently responsive",
    )

    last_scanned = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Last Scanned",
        help_text="Timestamp of the last time the host was scanned for updates",
    )

    cidr = models.ForeignKey(
        CIDRBlock,
        related_name='ip_hosts',
        on_delete=models.CASCADE,
        verbose_name="CIDR Block",
        help_text="The CIDR block that this host belongs to",
    )

    services = models.ManyToManyField(
        NetworkService,
        blank=True,
        related_name='ip_hosts',
        verbose_name="Network Services",
        help_text="The network services running on this host",
    )

    tags = TaggableManager()

    def __str__(self):
        return f"{self.ip} - {self.description} - {self.published}"

    class Meta:
        unique_together = ('ip', 'cidr',)
        ordering = ['last_scanned', 'published']
        verbose_name = "IP Host"
        verbose_name_plural = "IP Hosts"

    def update_last_scanned(self):
        self.last_scanned = datetime.now()
        self.save()

    def get_discovered_services(self) -> str:
        ports = []
        for service in self.services.all():
            ports.append(service.port)
        return ",".join((str(port) for port in ports))

    def get_services_short_info(self) -> dict[int, str]:
        info = {}
        for service in self.services.all():
            info[
                service.port] = f"{service.product}::{service.version}::{service.http_server_header}::{service.http_title}"
        return info
