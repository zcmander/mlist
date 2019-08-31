from django.apps import apps
from mlist.apps import MListAppConfig

app_config = apps.get_app_config(MListAppConfig.name)


def _get_tmdb_backdrop_url(movie):
    # size = "w780"
    size = "original"

    backdrop_path = movie.get_attribute("tmdb.backdrop_path")
    if not backdrop_path:
        return

    TMDB_CONFIG = app_config.TMDB_CONFIG

    base_url = TMDB_CONFIG["images"]["secure_base_url"]
    assert size in TMDB_CONFIG["images"]["backdrop_sizes"]
    return base_url + size + backdrop_path


def get_backdrop_url(movie):
    return _get_tmdb_backdrop_url(movie)
