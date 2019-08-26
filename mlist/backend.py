from mlist.models import IMDBMovie, TMDBMovie


def fetch_imdb_info(movie):
    # Movie must have IMDB Id before fetching IMDB info
    if not movie.imdb_id:
        return

    # IMDB info is already fetched
    if IMDBMovie.objects.filter(imdb_id=movie.imdb_id).first():
        return

    imdb_movie = IMDBMovie.create(imdb_id=movie.imdb_id)
    imdb_movie.save()

    return imdb_movie


def fetch_tmdb_info(movie):
    title = movie.get_title()

    # Movie must have title before fetching
    if not title:
        return

    # Movie must have IMDB Id before fetching TMDB info
    if not movie.imdb_id:
        return

    # TMDB info already fetched
    if TMDBMovie.objects.filter(imdb_id=movie.imdb_id).first():
        return

    tmdb_movie = TMDBMovie.create(
        movie.get_title(),
        imdb_id=movie.imdb_id)
    tmdb_movie.save()

    return tmdb_movie
