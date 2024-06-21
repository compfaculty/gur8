import logging

from django.db import models
from taggit.managers import TaggableManager

from asnet.tasks import create_cidr_blocks_for_asn

logger = logging.getLogger(__name__)


class AutonomousSystem(models.Model):
    """
       Represents an autonomous system (AS) in the Internet routing system.

       Each AS is identified by a unique ASN (Autonomous System Number).
       """

    asn = models.PositiveIntegerField(
        unique=True,
        verbose_name="ASN",
        help_text="The unique Autonomous System Number (ASN)",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Name",
        help_text="The name or description of the autonomous system",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description",
        default="",
        help_text="Additional details or information about the AS",
    )

    published = models.DateTimeField(
        "Published",
        auto_now_add=True,
        help_text="Timestamp when the AS was first created in the database",
    )

    tags = TaggableManager()

    def __str__(self):
        return f"AS{self.asn}, {self.name}"

    class Meta:
        verbose_name = "Autonomous System"
        verbose_name_plural = "Autonomous Systems"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.info("going to create cidr blocks")
        create_cidr_blocks_for_asn.send(self.pk, self.asn)

    def get_cidr_blocks_number(self) -> int:
        return self.cidr_blocks.count()

    def get_scanned_cidr_blocks_number(self) -> int:
        return self.cidr_blocks.filter(is_scanned=True).count()

    def get_ip_hosts_number(self) -> int:
        result = 0
        for cidr in self.cidr_blocks.all():
            result += cidr.ip_hosts.count()
        return result
