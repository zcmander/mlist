from django.apps import apps
from mlist.apps import MListAppConfig

app_config = apps.get_app_config(MListAppConfig.name)

TARGETS = [
    'LIST',
    'DETAIL'
]


def _get_tmdb_poster_url(movie, target):
    tmdb_poster_path = movie.get_attribute("tmdb.poster_path")

    if not tmdb_poster_path:
        return

    size = None

    if target == "LIST":
        size = "w185"
    elif target == "DETAIL":
        size = "w500"

    TMDB_CONFIG = app_config.TMDB_CONFIG

    base_url = TMDB_CONFIG["images"]["secure_base_url"]
    assert size in TMDB_CONFIG["images"]["poster_sizes"]

    return base_url + size + tmdb_poster_path


def _get_imdb_poster_url(movie, target):
    return movie.get_attribute('imdb.poster_url')


def get_poster_url(movie, target):
    assert target in TARGETS

    poster_url = _get_tmdb_poster_url(movie, target)
    if not poster_url:
        poster_url = _get_imdb_poster_url(movie, target)
    return poster_url
