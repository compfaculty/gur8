import logging

from django.db import models
from taggit.managers import TaggableManager
from asnet.models.autonomous_system import AutonomousSystem

logger = logging.getLogger(__name__)


class CIDRBlock(models.Model):
    """
      Represents a Classless Inter-Domain Routing (CIDR) block, a range of IP addresses.

      Each CIDR block is associated with a specific autonomous system (AS).
      """

    cidr = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CIDR Block",
        help_text="The CIDR notation representing the IP address range (e.g., 192.168.0.0/24)",
    )

    autonomous_system = models.ForeignKey(
        AutonomousSystem,
        related_name='cidr_blocks',
        on_delete=models.CASCADE,
        verbose_name="Autonomous System",
        help_text="The autonomous system that owns or manages this CIDR block",
    )

    published = models.DateTimeField(
        "Published",
        auto_now_add=True,
        help_text="Timestamp when the CIDR block was first created in the database",
    )

    is_scanned = models.BooleanField(
        default=False,
        auto_created=True,
        help_text="Indicates whether the CIDR block has been scanned for network assets",
    )

    tags = TaggableManager()

    def __str__(self):
        return f"{self.cidr}, {self.autonomous_system}"

    class Meta:
        verbose_name = "CIDRBlock"
        verbose_name_plural = "CIDRBlocks"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # logger.info("going to create host ips")
        # create_ip_hosts_for_cidr.send(self.pk, self.cidr)

    def live_hosts_in_cidr(self) -> int:
        return self.ip_hosts.count()
