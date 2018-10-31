from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.shortcuts import redirect, render_to_response


def authenticate_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect(reverse('list-movies'))
        else:
            messages.error(request, 'Disabled user.')
            return redirect(reverse('login'))
    else:
        messages.error(request, 'Invalid username or password.')
        return redirect(reverse('login'))


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))


def login_view(request):
    if request.user and request.user.is_authenticated:
        return redirect(reverse('list-movies'))
    return render_to_response("mlist/login.html")
