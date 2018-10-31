from django.urls import reverse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from mlist.models import Movie, IMDBMovie, TMDBMovie


@login_required()
def fetch_imdb_view(request, pk):
    movie = Movie.objects.get(pk=int(pk))
    imdb_movie = IMDBMovie.create(title=movie.title, imdb_id=movie.imdb_id)
    if not IMDBMovie.objects.filter(imdb_id=imdb_movie.imdb_id).all():
        imdb_movie.save()
        if not movie.imdb_id:  # If movie without IMDB ID then update it
            movie.imdb_id = imdb_movie.imdb_id
            movie.save()
    elif not movie.imdb_id:  # If movie without IMDB ID then update it
        movie.imdb_id = imdb_movie.imdb_id
        movie.save()

    messages.success(request, 'IMDB information fetched.')
    return redirect(reverse("list-movies"))


@login_required()
def fetch_tmdb_view(request, pk):
    movie = Movie.objects.get(pk=int(pk))
    if not movie.imdb_id:
        messages.error(
            request, 'TMDB information requires IMDB id before fetch.')
        return redirect(reverse("list-movies"))

    tmdb_movie = TMDBMovie.create(title=movie.title, imdb_id=movie.imdb_id)
    if not TMDBMovie.objects.filter(imdb_id=tmdb_movie.imdb_id).all():
        tmdb_movie.save()

    messages.success(request, 'TMDB information fetched.')
    return redirect(reverse("list-movies"))
