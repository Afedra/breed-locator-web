import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, render, reverse
from django.template.context_processors import csrf
from django.template.loader import render_to_string

from breed.activities.models import Activity
from breed.decorators import ajax_required
from .models import Breed

BREEDS_NUM_PAGES = 10


@login_required
def add(request):
    if request.method == "GET":
        return render(request, 'breeds.html', {})
    else:
        user = request.user
        breeds = Breed()
        breeds.user = user
        post = request.POST['description']
        post = post.strip()
        if len(post) > 0:
            breeds.breed = post[:255]
            breeds.sex = request.POST['sex']
            breeds.photo = request.FILES['picture']
            breeds.save()
            return breed(request, breeds.id)
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Failed to add animal.')

            return render(request, 'breeds.html', {})


def breed(request, pk):
    breed = get_object_or_404(Breed, pk=pk)
    return render(request, 'breed.html', {'breed': breed})

def statistics(request):
    return render(request, 'statistics.html', {})

def find(request, pk):
    breed = get_object_or_404(Breed, pk=pk)
    if breed.sex == "Male":
        sex = "Female"
    else:
        sex = "Male"
    breeds = Breed.objects.filter(sex=sex, breed_type=breed.breed_type).exclude(pk=breed.pk)
    return render(request, 'find.html', {'breeds': breeds, "currentbreed": breed})

@login_required
@ajax_required
def match(request):
    breed_id = request.POST['breed']
    currentbreed_id = request.POST['currentbreed']
    breed = Breed.objects.get(pk=breed_id)
    user = request.user
    match = Activity.objects.filter(activity_type=Activity.MATCH, breed=breed_id,
                                   user=user, currentbreed=currentbreed_id)
    if match:
        user.profile.unotify_matched(breed)
        match.delete()

    else:
        match = Activity(activity_type=Activity.MATCH, breed=breed_id, currentbreed=currentbreed_id, user=user)
        match.save()
        user.profile.notify_matched(breed)

    currentbreed_id = request.POST['currentbreed']
    Breed.objects.get(pk=currentbreed_id).calculate_matches()
    return HttpResponse(breed.calculate_matches())

@login_required
@ajax_required
def load(request):
    from_breed = request.GET.get('from_breed')
    page = request.GET.get('page')
    breed_source = request.GET.get('breed_source')
    all_breeds = Breed.get_breeds(from_breed)
    if breed_source != 'all':
        all_breeds = all_breeds.filter(user__id=breed_source)
    paginator = Paginator(all_breeds, BREEDS_NUM_PAGES)
    try:
        breeds = paginator.page(page)
    except PageNotAnInteger:
        return HttpResponseBadRequest()
    except EmptyPage:
        breeds = []
    html = ''
    csrf_token = (csrf(request)['csrf_token'])
    for breed in breeds:
        html = '{0}{1}'.format(html,
                               render_to_string('partial_breed.html',
                                                {
                                                    'breed': breed,
                                                    'user': request.user,
                                                    'csrf_token': csrf_token
                                                    }))

    return HttpResponse(html)


def _html_breeds(last_breed, user, csrf_token, breed_source='all'):
    breeds = Breed.get_breeds_after(last_breed)
    if breed_source != 'all':
        breeds = breeds.filter(user__id=breed_source)
    html = ''
    for breed in breeds:
        html = '{0}{1}'.format(html,
                               render_to_string('partial_breed.html',
                                                {
                                                    'breed': breed,
                                                    'user': user,
                                                    'csrf_token': csrf_token
                                                    }))

    return html

@login_required
@ajax_required
def load_new(request):
    last_breed = request.GET.get('last_breed')
    user = request.user
    csrf_token = (csrf(request)['csrf_token'])
    html = _html_breeds(last_breed, user, csrf_token)
    return HttpResponse(html)


@login_required
@ajax_required
def check(request):
    last_breed = request.GET.get('last_breed')
    breed_source = request.GET.get('breed_source')
    breeds = Breed.get_breeds_after(last_breed)
    if breed_source != 'all':
        breeds = breeds.filter(user__id=breed_source)
    count = breeds.count()
    return HttpResponse(count)



@login_required
@ajax_required
def comment(request):
    if request.method == 'POST':
        breed_id = request.POST['breed']
        breed = Breed.objects.get(pk=breed_id)
        post = request.POST['post']
        post = post.strip()
        if len(post) > 0:
            post = post[:255]
            user = request.user
            breed.comment(user=user, breed=post)
            user.profile.notify_commented(breed)
            user.profile.notify_also_commented(breed)
        return render(request, 'partial_breed_comments.html',
                      {'breed': breed})

    else:
        breed_id = request.GET.get('breed')
        breed = Breed.objects.get(pk=breed_id)
        return render(request, 'partial_breed_comments.html',
                      {'breed': breed})


@login_required
@ajax_required
def update(request):
    first_breed = request.GET.get('first_breed')
    last_breed = request.GET.get('last_breed')
    breed_source = request.GET.get('breed_source')
    breeds = Breed.get_breeds().filter(id__range=(last_breed, first_breed))
    if breed_source != 'all':
        breeds = breeds.filter(user__id=breed_source)
    dump = {}
    for breed in breeds:
        dump[breed.pk] = {'matches': breed.matches, 'comments': breed.comments}
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')


@login_required
@ajax_required
def track_comments(request):
    breed_id = request.GET.get('breed')
    breed = Breed.objects.get(pk=breed_id)
    return render(request, 'partial_breed_comments.html', {'breed': breed})


@login_required
@ajax_required
def remove(request):
    try:
        breed_id = request.POST.get('breed')
        breed = Breed.objects.get(pk=breed_id)
        if breed.user == request.user:
            matches = breed.get_matches()
            parent = breed.parent
            for match in matches:
                match.delete()
            breed.delete()
            if parent:
                parent.calculate_comments()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception:
        return HttpResponseBadRequest()
