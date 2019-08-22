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


class ListService(models.Model):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    service_info = v1.list_service_for_all_namespaces(watch=False)

    def __str__(self):
        return self.service_info
