import logging

from mlist.models import IMDBMovie, TMDBMovie

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
        movie = tmdb.Movies(result["id"])
        result_imdb_id = movie.external_ids()["imdb_id"]

        if result_imdb_id == imdb_id:
            found = movie
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

    return tmdb_movie
