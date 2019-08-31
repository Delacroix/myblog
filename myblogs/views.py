from django.shortcuts import render
from .models import Topic, Entry
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from .forms import TopicForm, EntryForm, ServiceForm
from django.contrib.auth.decorators import login_required
from kubernetes import client, config

# Create your views here.


def index(request):
    return render(request, 'myblogs/index.html')


@login_required
def service_info(request):
   config.load_kube_config()
   v1 = client.CoreV1Api()
   service_info = v1.list_service_for_all_namespaces(watch=False)
   return render(request, 'myblogs/service_info.html', {'service_info': service_info})


def deploy_list(request):
    config.load_kube_config()
    extension = client.ExtensionsV1beta1Api()
    deploy_list = extension.list_deployment_for_all_namespaces(watch=False)
    return render(request, 'myblogs/deploy_list.html', {'deploy_list': deploy_list})


def node_list(request):
    config.load_kube_config()
    node = client.V1NodeList()
    node_list = node.list_deployment_for_all_namespaces(watch=False)
    return render(request, 'myblogs/node_list.html', {'node_list': node_list})


@login_required
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'myblogs/topics.html', context)


@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'myblogs/topic.html', context)


@login_required
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('myblogs:topics'))

    context = {'form': form}
    return render(request, 'myblogs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('myblogs:topic',
                                                args=[topic_id]))

    context = {'topic': topic, 'form': form}
    return render(request, 'myblogs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myblogs:topic',
                                                args=[topic.id]))

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'myblogs/edit_entry.html', context)


def new_service(request):
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    service = client.V1Service()
    service.api_version = "v1"
    service.kind = "Service"
    service.metadata = client.V1ObjectMeta(name='my-service')
    spec = client.V1ServiceSpec()
    spec.selector = {"app": 'MyApps'}
    spec.ports = [client.V1ServicePort(protocol='TCP',
                                       port=80,
                                       target_port=8080)]
    service.spec = spec
    api_instance.create_namespaced_service(namespace="default", body=service)
    return render(request, 'service_info.html', {'service_info': service_info})
