from django.conf import settings

from mlist.omdbapi import BackendOMDB
import tmdbsimple as tmdb


def configure_backends():
    """
    Configures all backends.

    Fetches nessessary information of the backend on
    application startup. This usually means available
    poster sizes and URL of the image cache server(s).
    """
    tmdb.API_KEY = settings.TMDB_APIKEY
    BackendOMDB.APIKEY = settings.OMDB_APIKEY


def get_tmdb_configuration():
    return tmdb.Configuration().info()
