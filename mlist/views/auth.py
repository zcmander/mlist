import csv
import json
import codecs
import datetime

from six import StringIO

from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, FormView, DeleteView, UpdateView, CreateView
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.db.models import Count

from haystack.views import SearchView
from haystack.query import SearchQuerySet
from haystack.inputs import Raw

from mlist.forms import MovieForm, ImportForm, MovieEditForm, CollectionForm
from mlist.models import Movie, MovieInCollection, Collection, IMDBMovie, TMDBMovie


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