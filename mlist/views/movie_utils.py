from django.urls import reverse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from mlist.models import Movie
from mlist.resolver import resolve_imdb_id_by_title
from mlist.backend import fetch_imdb_info, fetch_tmdb_info


@login_required()
def fetch_imdb_view(request, pk):
    movie = Movie.objects.get(pk=int(pk))

    # Resolve IMDB ID if possible
    if not movie.imdb_id:
        imdb_id = resolve_imdb_id_by_title(movie.get_title())
        if imdb_id:
            movie.imdb_id = imdb_id

    movie.save()

    try:
        fetch_imdb_info(movie)
    except Exception as exc:
        messages.error(
            request,
            "<strong>Error while fetching IMDB information:</strong>" +
            exc.__class__.__name__ + u":" + str(exc),
            extra_tags='safe')
    else:
        messages.success(request, 'IMDB information fetched.')

    return redirect(reverse("list-movies"))


@login_required()
def fetch_tmdb_view(request, pk):
    movie = Movie.objects.get(pk=int(pk))
    if not movie.imdb_id:
        messages.error(
            request, 'TMDB information requires IMDB id before fetch.')
        return redirect(reverse("list-movies"))

    try:
        fetch_tmdb_info(movie)
    except Exception as exc:
        messages.error(
            request,
            "<strong>Error while fetching TMDB information:</strong>" +
            str(exc.__class__.__name__) + u":" + str(exc),
            extra_tags='safe')
    else:
        messages.success(request, 'TMDB information fetched.')

    return redirect(reverse("list-movies"))
