import logging

from mlist.models import IMDBMovie, TMDBMovie, BackendMovie

from mlist.omdbapi import BackendOMDB
import tmdbsimple as tmdb

logger = logging.getLogger(__name__)


def fetch_imdb_info(movie):
    # Movie must have IMDB Id before fetching IMDB info
    if not movie.imdb_id:
        return

    # IMDB info is already fetched
    if IMDBMovie.objects.filter(imdb_id=movie.imdb_id).first():
        return

    result = BackendOMDB().get_data(imdb_id=movie.imdb_id)

    imdb_movie = IMDBMovie()
    imdb_movie.imdb_id = result.get('imdb_id')
    imdb_movie.title = result.get('title')
    imdb_movie.year = result.get('year')[:4]
    imdb_movie.rated = result.get('rated')
    imdb_movie.released = result.get('released')
    imdb_movie.runtime = result.get('runtime')
    imdb_movie.director = result.get('director')
    imdb_movie.writer = result.get('writer')
    imdb_movie.actors = result.get('actors')
    imdb_movie.plot = result.get('plot')
    imdb_movie.votes = result.get('votes')
    imdb_movie.rating = result.get('rating')
    imdb_movie.genre = result.get('genre')
    imdb_movie.poster_url = result.get('poster_url')
    imdb_movie.save()

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

    return imdb_movie


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
    if TMDBMovie.objects.filter(imdb_id=movie.imdb_id).first():
        return

    tmdb_movie = TMDBMovie()

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

    tmdb_movie.imdb_id = info["imdb_id"]
    tmdb_movie.tmdb_id = info["id"]
    tmdb_movie.original_title = info["original_title"]
    tmdb_movie.title = info["title"]
    tmdb_movie.popularity = info["popularity"]
    tmdb_movie.adult = info["adult"]
    tmdb_movie.spoken_languages = ','.join(spoken_language_names)
    tmdb_movie.homepage = info["homepage"]
    tmdb_movie.overview = info["overview"]
    tmdb_movie.vote_average = info["vote_average"]
    tmdb_movie.vote_count = info["vote_count"]
    tmdb_movie.runtime = info["runtime"]
    tmdb_movie.budget = info["budget"]
    tmdb_movie.revenue = info["revenue"]
    tmdb_movie.genres = ','.join(genre_names)
    tmdb_movie.production_companies = ','.join(production_company_names)
    tmdb_movie.productions_countries = ','.join(productions_country_names)
    tmdb_movie.poster_path = info["poster_path"]
    tmdb_movie.backdrop_path = info["backdrop_path"]
    tmdb_movie.tagline = info["tagline"]

    tmdb_movie.save()

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

    return tmdb_movie
