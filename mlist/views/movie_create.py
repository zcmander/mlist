import json

from django.urls import reverse
from django.views.generic import FormView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from mlist.forms import MovieForm
from mlist.models import (
    Movie,
    MovieInCollection,
    Collection,
    IMDBMovie,
    TMDBMovie,
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
        imdb_movie = None
        try:
            if imdb_id:
                movie = Movie.objects.get(imdb_id=imdb_id)
            else:
                movie = Movie.objects.get(title=title)
        except Movie.DoesNotExist:
            movie = Movie()
            movie.title = title
            movie.imdb_id = None
            movie.save()

        if not movie or not movie.imdb_id or not IMDBMovie.objects.filter(imdb_id=movie.imdb_id).all():

            try:
                if imdb_id:
                    imdb_movie = IMDBMovie.create(imdb_id=imdb_id)
                else:
                    imdb_movie = IMDBMovie.create(title=title)
            except Exception as exc:
                messages.error(self.request, u"<strong>Error while fetching IMDB information:</strong>" + exc.__class__.__name__ + u":" + str(exc), extra_tags='safe')

            if imdb_movie and imdb_movie.imdb_id:
                try:
                    movie = Movie.objects.get(imdb_id=imdb_movie.imdb_id)
                except Movie.DoesNotExist:
                    pass

            if imdb_movie and not IMDBMovie.objects.filter(imdb_id=imdb_movie.imdb_id).all():
                imdb_movie.save()

                if movie and not movie.imdb_id:  # If movie without IMDB ID then update it
                    movie.imdb_id = imdb_movie.imdb_id
                    movie.save()

        if movie.imdb_id and not TMDBMovie.objects.filter(imdb_id=movie.imdb_id).all():
            try:
                tmdb_movie = TMDBMovie.create(movie.get_title(), imdb_id=movie.imdb_id)
                tmdb_movie.save()
            except Exception as exc:
                messages.error(self.request, u"<strong>Error while fetching TMDB information:</strong>" + str(exc.__class__.__name__) + u":" + str(exc), extra_tags='safe')

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
        tags.append({'tag': str(tag)})
    content = {'tags': tags}
    return HttpResponse(json.dumps(content), content_type="application/json")
