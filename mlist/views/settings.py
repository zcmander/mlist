from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response
from django.db.models import Count

from mlist.models import Movie, BackendMovie


@login_required()
def settings_view(request):
    sqs = Movie.objects.values_list('imdb_id', flat=True)
    sqs = sqs.annotate(count_imdb=Count("imdb_id"))
    sqs = sqs.filter(count_imdb__gt=1)

    duplicate_imdb_ids = sqs.distinct()
    duplicate_movies = []

    for imdb_id in duplicate_imdb_ids:
        sqs = Movie.objects
        sqs = sqs.filter(imdb_id=imdb_id)
        sqs = sqs.annotate(mic_count=Count("movieincollection"))
        sqs = sqs.order_by("-mic_count")
        duplicate_movies.append(sqs.all())

    imdb_ids = [x.imdb_id for x in BackendMovie.objects.filter(backend="imdb").all()]
    no_imdb_info = Movie.objects.exclude(imdb_id__in=imdb_ids)

    tmdb_ids = [x.imdb_id for x in BackendMovie.objects.filter(backend="tmdb").all()]
    no_tmdb_info = Movie.objects.exclude(imdb_id__in=tmdb_ids)

    render_dict = {
        'movies_no_imdb_id': Movie.objects.filter(imdb_id=None),
        'movies_no_imdb_info': no_imdb_info,
        'movies_no_tmdb_info': no_tmdb_info,
        'movies_duplicate_imdb': duplicate_movies,
        'collections': request.user.collection_set,
        'user': request.user,
    }
    return render_to_response("mlist/settings.html", render_dict)


@login_required
def merge_movie_view(request, pk):
    to_movie = Movie.objects.get(pk=pk)
    other_movies = Movie.objects \
        .filter(imdb_id=to_movie.imdb_id) \
        .exclude(pk=pk) \
        .all()

    for movie in other_movies:
        for mic in movie.movieincollection_set.all():
            mic.movie = to_movie
            mic.save()
        movie.delete()

    return redirect(reverse("settings"))
