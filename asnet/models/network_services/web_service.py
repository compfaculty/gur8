from django.core.exceptions import ValidationError
from django.db import models

from .network_service import NetworkService


class WebService(NetworkService):
    url = models.URLField(verbose_name="URL", default="", max_length=255, unique=True, db_index=True)
    server_header = models.CharField(max_length=256, blank=True, verbose_name="HTTP server header", default="")
    title = models.TextField(blank=True, verbose_name="HTTP title", default="")
    favicon = models.TextField(blank=True, verbose_name="HTTP favicon", default="")
    robots = models.TextField(blank=True, verbose_name="HTTP robots", default="")
    methods = models.TextField(blank=True, verbose_name="HTTP methods", default="")
    cookie_flags = models.TextField(blank=True, verbose_name="HTTP cookie flags", default="")
    fingerprint = models.TextField(blank=True, verbose_name="Fingerprint strings", default="")
    report_urlscanio = models.URLField(verbose_name="urlscan.io", blank=True, max_length=255, unique=True,
                                       db_index=True)

    def __str__(self):
        return (f"Service: {self.protocol} , port: {self.port}, product : {self.product}, version: {self.version} "
                f"{self.title})")

    class Meta:
        ordering = ['port', 'product', 'version', 'title', 'published']
        verbose_name = "Web Service"
        verbose_name_plural = "Web Services"

    def save(self, *args, **kwargs):

        if self.pk is not None:  # Check if the object is already in the database
            # Fetch the existing object from the database
            original = WebService.objects.get(pk=self.pk)
            # Check if the 'published' field has been changed
            if original.published != self.published:
                raise ValidationError("The 'published' date cannot be modified.")
        super(WebService, self).save(*args, **kwargs)
