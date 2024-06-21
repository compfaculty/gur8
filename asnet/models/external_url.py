import logging

from django.db import models

logger = logging.getLogger(__name__)


class ExternalURL(models.Model):
    url = models.URLField("URL")

    def __str__(self):
        return self.url
