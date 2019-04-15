from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from breed.authentication.forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'signup.html',
                          {'form': form})

        else:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            job_title = form.cleaned_data.get('job_title')
            password = form.cleaned_data.get('password')
            first_name = form.cleaned_data.get('first_name')
            location = form.cleaned_data.get('location')
            last_name = form.cleaned_data.get('last_name')
            User.objects.create_user(username=username, password=password,
                                     email=email, first_name=first_name, last_name=last_name)
            user = authenticate(username=username, password=password)
            user.profile.job_title = job_title
            user.profile.location = location
            login(request, user)
            return redirect('/settings/')

    else:
        return render(request, 'signup.html',
                      {'form': SignUpForm()})
