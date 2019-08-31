from django.db import models
from django.contrib.auth.models import User
from kubernetes import client, config

# Create your models here.


class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=None)

    def __str__(self):
        return self.text


class Entry(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return self.text[:50] + "..."


class Service(models.Model):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    svc_name = models.CharField(max_length=32, default='my-service')
    protocol = models.CharField(max_length=32, default='TCP')
    spec_selector = models.CharField(max_length=32, default='MyApps')
    svc_type = models.CharField(max_length=20, default='ClusterIP')
    port = models.CharField(max_length=32, default='80')
    target_port = models.CharField(max_length=32, default='8080')
    node_port = models.CharField(max_length=10)

    svc_conf = [svc_name, protocol, spec_selector,
                svc_type, port, target_port, node_port]

    def __str__(self):
        return self.svc_conf
