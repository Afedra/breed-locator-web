from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render

from breed.breeds.models import Breed
from breed.questions.models import Question


@login_required
def search(request):
    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()
        if len(querystring) == 0:
            return redirect('/search/')

        try:
            search_type = request.GET.get('type')
            if search_type not in ['breed', 'questions', 'users']:
                search_type = 'breed'

        except Exception:
            search_type = 'breed'

        count = {}
        results = {}
        results['breed'] = Breed.objects.filter(breed__icontains=querystring,
                                              parent=None)
        results['questions'] = Question.objects.filter(
            Q(title__icontains=querystring) | Q(
                description__icontains=querystring))
        results['users'] = User.objects.filter(
            Q(username__icontains=querystring) | Q(
                first_name__icontains=querystring) | Q(
                    last_name__icontains=querystring))
        count['breed'] = results['breed'].count()
        count['questions'] = results['questions'].count()
        count['users'] = results['users'].count()

        return render(request, 'results.html', {
            'hide_search': True,
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        })
    else:
        return render(request, 'search.html', {'hide_search': True})
