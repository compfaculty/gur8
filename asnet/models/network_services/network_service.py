from django.core.exceptions import ValidationError
from django.db import models


class NetworkService(models.Model):
    PROTOCOLS = [
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
        ('ftp', 'FTP'),
        ('smtp', 'SMTP'),  # Simple Mail Transfer Protocol
        ('imap', 'IMAP'),  # Internet Message Access Protocol
        ('pop3', 'POP3'),  # Post Office Protocol 3
        ('ssh', 'SSH'),  # Secure Shell
        ('telnet', 'Telnet'),
        ('sftp', 'SFTP'),  # SSH File Transfer Protocol
        # Add more protocols as needed
        ('mysql', 'MySQL'),  # MySQL Protocol
        ('postgresql', 'PostgreSQL'),  # PostgreSQL Protocol
        ('mssql', 'MS SQL Server'),  # Microsoft SQL Server Protocol
        ('mongodb', 'MongoDB'),  # MongoDB Protocol
        ('oracle', 'Oracle Database'),  # Oracle Database Protocol
        ('sqlite', 'SQLite'),  # SQLite doesn't have a specific network protocol as it's file-based
        ('redis', 'Redis'),  # Redis Protocol
        ('memcached', 'Memcached'),  # Memcached Protocol
        ('rabbitmq', 'RabbitMQ'),  # RabbitMQ Protocol
        ('rabbitmq_management', 'RabbitMQ Management'),  # RabbitMQ Management Plugin
        ('amqp', 'AMQP'),  # Advanced Message Queuing Protocol
        ('amqps', 'AMQPS'),  # Advanced Message Queuing Protocol over TLS
        ('kafka', 'Kafka'),  # Apache Kafka Protocol
        ('kafka_management', 'Kafka Management'),  # Apache Kafka Management Plugin
        ('cassandra', 'Cassandra'),  # Cassandra Protocol
        ('couchdb', 'CouchDB'),  # CouchDB Protocol
        ('neo4j', 'Neo4j'),  # Neo4j Protocol
        ('elastic', 'Elasticsearch'),  # Elasticsearch Protocol
        ('file', 'File'),  # File Transfer Protocol
        ('rdp', 'RDP'),  # Remote Desktop Protocol
        ('vnc', 'VNC'),  # Virtual Network Computing Protocol
        ('rdp_vnc', 'RDP VNC'),  # Remote Desktop Protocol over VNC
        ('ssh_tunnel', 'SSH Tunnel'),  # SSH Tunnel
        ('mysql', 'MySQL'),  # MySQL Protocol
        ('postgresql', 'PostgreSQL'),  # PostgreSQL Protocol
        ('mssql', 'MS SQL Server'),  # Microsoft SQL Server Protocol
        ('mongodb', 'MongoDB'),  # MongoDB Protocol
        ('oracle', 'Oracle Database'),  # Oracle Database Protocol
        ('sqlite', 'SQLite'),  # SQLite doesn't have a specific network protocol as it's file-based
        ('redis', 'Redis'),  # Redis Protocol
        ('aws_api', 'AWS API (HTTPS)'),
        ('azure_api', 'Azure API (HTTPS)'),
        ('gcp_api', 'GCP API (HTTPS)'),
        ('k8s_api', 'Kubernetes API (HTTP/HTTPS)'),
        ('etcd', 'etcd (gRPC)'),

    ]

    port = models.IntegerField(verbose_name="Port")
    protocol = models.CharField(max_length=20, choices=PROTOCOLS, default='http', verbose_name="Protocol")
    product = models.CharField(max_length=128, blank=True, verbose_name="Product", default="")
    version = models.CharField(max_length=128, blank=True, verbose_name="Version", default="")
    extrainfo = models.TextField(blank=True, verbose_name="ExtraInfo", default="")
    conf = models.IntegerField(verbose_name="Conf", blank=True, default=0)
    cpe = models.CharField(max_length=128, blank=True, verbose_name="CPE", default="")

    ssl_date = models.TextField(blank=True, verbose_name="SSL date", default="")
    ssl_hostkey = models.TextField(blank=True, verbose_name="SSL hostkey", default="")
    ssl_cert = models.TextField(max_length=512, blank=True, verbose_name="SSL cert", default="")
    tls_alpn = models.TextField(max_length=64, blank=True, verbose_name="TLS alpn", default="")

    published = models.DateTimeField("date published", auto_now_add=True)
    last_scanned = models.DateTimeField(blank=True, null=True, verbose_name="Last Scanned")

    def __str__(self):
        return (f"Service: {self.protocol} , port: {self.port}, product : {self.product}, version: {self.version} "
                f"{self.extrainfo})")

    class Meta:
        ordering = ['port', 'product', 'version', 'extrainfo', 'published']
        verbose_name = "Network Service"
        verbose_name_plural = "Network Services"

    def save(self, *args, **kwargs):

        if self.pk is not None:  # Check if the object is already in the database
            # Fetch the existing object from the database
            original = NetworkService.objects.get(pk=self.pk)
            # Check if the 'published' field has been changed
            if original.published != self.published:
                raise ValidationError("The 'published' date cannot be modified.")
        super(NetworkService, self).save(*args, **kwargs)
