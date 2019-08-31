import logging

from mlist.models import BackendMovie

from mlist.omdbapi import BackendOMDB
import tmdbsimple as tmdb

logger = logging.getLogger(__name__)


def fetch_imdb_info(movie):
    # Movie must have IMDB Id before fetching IMDB info
    if not movie.imdb_id:
        return

    # IMDB info is already fetched
    if BackendMovie.objects.filter(backend="imdb", movie=movie).first():
        return

    result = BackendOMDB().get_data(imdb_id=movie.imdb_id)

    backend_movie = BackendMovie(movie=movie, backend="imdb")
    backend_movie.save()

    backend_movie.add_string("imdb_id", result.get('imdb_id'))
    backend_movie.add_string("title", result.get('title'))
    backend_movie.add_int("year", (int)(result.get('year')[:4]))
    backend_movie.add_string("rated", result.get('rated'))
    backend_movie.add_date("released", result.get('released'))
    backend_movie.add_string("imdb.runtime", result.get('runtime'))
    backend_movie.add_string("director", result.get('director'))
    backend_movie.add_string("writer", result.get('writer'))
    backend_movie.add_string("actors", result.get('actors'))
    backend_movie.add_string("synopsis", result.get('plot'))
    backend_movie.add_int("imdb.votes", result.get('votes'))
    backend_movie.add_float("imdb.rating", result.get('rating'))
    backend_movie.add_string("imdb.genre", result.get('genre'))
    backend_movie.add_string("imdb.poster_url", result.get('poster_url'))

    return backend_movie


def fetch_tmdb_info(movie):
    title = movie.get_title()
    imdb_id = movie.imdb_id

    # Movie must have title before fetching
    if not title:
        return

    # Movie must have IMDB Id before fetching TMDB info
    if not imdb_id:
        return

    # TMDB info already fetched
    if BackendMovie.objects.filter(backend="tmdb", movie=movie).first():
        return

    search = tmdb.Search().movie(query=title)

    found = None
    for result in search["results"]:
        result_movie = tmdb.Movies(result["id"])
        result_imdb_id = result_movie.external_ids()["imdb_id"]

        if result_imdb_id == imdb_id:
            found = result_movie
            break
    else:
        logger.error("No TMDB movie found with title {0} and IMDB Id: {1}".format(
            title,
            imdb_id
        ))
        return

    info = found.info()

    spoken_language_names = [
        x['name'] for x in info["spoken_languages"]
    ]

    production_company_names = [
        x['name'] for x in info["production_companies"]
    ]

    productions_country_names = [
        x['name'] for x in info["production_countries"]
    ]

    genre_names = [
        x['name'] for x in info["genres"]
    ]

    backend_movie = BackendMovie(movie=movie, backend="tmdb")
    backend_movie.save()

    backend_movie.add_string("imdb_id", info["imdb_id"])
    backend_movie.add_int("tmdb.id", info["id"])
    backend_movie.add_string("original_title", info["original_title"])
    backend_movie.add_string("title", info["title"])
    backend_movie.add_string("tmdb.popularity", info["popularity"])
    backend_movie.add_boolean("adult", info["adult"])
    backend_movie.add_string("spoken_languages", ','.join(spoken_language_names))
    backend_movie.add_string("homepage", info["homepage"])
    backend_movie.add_string("synopsis", info["overview"])
    backend_movie.add_int("tmdb.vote_average", info["vote_average"])
    backend_movie.add_int("tmdb.vote_count", info["vote_count"])
    backend_movie.add_int("runtime", info["runtime"])
    backend_movie.add_int("budget", info["budget"])
    backend_movie.add_int("revenue", info["revenue"])
    backend_movie.add_string("genres", ','.join(genre_names))
    backend_movie.add_string("production_companies", ','.join(production_company_names))
    backend_movie.add_string("productions_countries", ','.join(productions_country_names))
    backend_movie.add_string("tmdb.poster_path", info["poster_path"])
    backend_movie.add_string("tmdb.backdrop_path", info["backdrop_path"])
    backend_movie.add_string("tagline", info["tagline"])

    return backend_movie
