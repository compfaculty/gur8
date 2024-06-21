from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

# from asnet.models import AutonomousSystem, IpHost, WebService


class WebDomain(models.Model):
    """
    describes Web Domain instance
    """
    url = models.URLField(verbose_name="URL", default="", max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, verbose_name="Description", default="")
    published = models.DateTimeField("date published", auto_now_add=True)
    is_alive = models.BooleanField(default=False, auto_created=True, verbose_name="Is Alive")
    is_scanned = models.BooleanField(default=False, auto_created=True)
    last_scanned = models.DateTimeField(blank=True, null=True, verbose_name="Last Scanned")

    # Self-referential ForeignKey to represent parent domain
    parent_domain = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subdomains',
        verbose_name="Parent Domain"
    )

    autonomous_system = models.ForeignKey('AutonomousSystem', related_name='web_domains', on_delete=models.SET_NULL,
                                          blank=True, null=True, verbose_name="Autonomous System")

    ip_hosts = models.ManyToManyField('IpHost', blank=True, related_name='web_domains', verbose_name="Host IPs")

    services = models.ManyToManyField('WebService', blank=True, related_name='web_domains',
                                      verbose_name="Network Services")

    def __str__(self):
        return f"{self.url} - {self.description} - {self.published}"

    class Meta:
        ordering = ['url', 'last_scanned', 'published']
        verbose_name = "Web Domain"
        verbose_name_plural = "Web Domains"

    def save(self, *args, **kwargs):

        if self.pk is not None:  # Check if the object is already in the database
            # Fetch the existing object from the database
            original = WebDomain.objects.get(pk=self.pk)
            # Check if the 'published' field has been changed
            if original.published != self.published:
                raise ValidationError("The 'published' date cannot be modified.")
        super(WebDomain, self).save(*args, **kwargs)

    def update_last_scanned(self):
        self.last_scanned = datetime.now()
        self.save()

    def get_related_ip_hosts(self) -> str:
        hosts = []
        for service in self.ip_hosts.all():
            hosts.append(service.port)
        return ",".join((str(host) for host in hosts))

    def add_subdomain(self, url):
        subdomain, created = WebDomain.objects.get_or_create(url=url)
        if created:
            subdomain.parent_domain = self
            subdomain.save()

