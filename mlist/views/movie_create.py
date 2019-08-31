import json
import requests

from django.conf import settings
from django.urls import reverse
from django.views.generic import FormView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from mlist.resolver import resolve_imdb_id_by_title
from mlist.backend import fetch_imdb_info, fetch_tmdb_info
from mlist.forms import MovieForm
from mlist.models import (
    Movie,
    MovieInCollection,
    Collection,
)


@method_decorator(login_required, name='dispatch')
class MovieCreate(FormView):
    form_class = MovieForm
    template_name = 'mlist/movie_form.html'
    success_message = "Movie added successfully!"

    def get_initial(self):
        collection = None

        collection_title = self.request.GET.get("collection", "watched")

        collection_query = Collection.objects.filter(user=self.request.user,
                                                     title=collection_title)
        collection = collection_query.first()

        return {
            'title': self.request.GET.get("title"),
            'imdb_id': self.request.GET.get("imdb_id"),
            'collection': collection
        }

    def get_form_kwargs(self):
        kwargs = super(MovieCreate, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        title = form.cleaned_data['title']
        tags = form.cleaned_data['tags']
        date = form.cleaned_data['date']
        imdb_id = form.cleaned_data['imdb_id']

        collection = form.cleaned_data['collection']

        movie = None

        # First, check if database already has the movie with given IMDB ID
        movie = Movie.objects.filter(imdb_id=imdb_id).first()

        # If not, create a new one
        if not movie:
            movie = Movie()
            movie.title = title
            # User provided IMDB id is only used, if it has match in any backend
            movie.imdb_id = None
            movie.save()

        # Resolve IMDB ID if possible
        if not movie.imdb_id:
            try:
                imdb_id = resolve_imdb_id_by_title(title)
                if imdb_id:
                    movie.imdb_id = imdb_id
            except Exception:
                pass

        # Fetch IMDB Info
        try:
            fetch_imdb_info(movie)
        except Exception as exc:
            messages.error(
                self.request,
                "<strong>Error while fetching IMDB information:</strong>" +
                exc.__class__.__name__ + u":" + str(exc),
                extra_tags='safe')

        # Fetch TMDB Info
        try:
            fetch_tmdb_info(movie)
        except Exception as exc:
            messages.error(
                self.request,
                "<strong>Error while fetching TMDB information:</strong>" +
                str(exc.__class__.__name__) + u":" + str(exc),
                extra_tags='safe')

        movie.save()

        mic = MovieInCollection()
        mic.movie = movie
        mic.collection = collection
        mic.date = date

        mic.save()
        mic.tags.add(*tags)

        messages.success(self.request, self.success_message)
        return redirect(reverse('detail-movie', args=[mic.id]))


@login_required()
def ajax_taglist_view(request):
    tags = []
    for tag in MovieInCollection.tags.all():
        tags.append(str(tag))
    return HttpResponse(json.dumps(tags), content_type="application/json")


@login_required()
def ajax_movie_list(request):
    response = requests.get(
        'http://www.omdbapi.com/',
        params={
            's': request.GET['s'],
            'apikey': settings.OMDB_APIKEY
        })

    return HttpResponse(response.text, content_type="application/json")
