from django.apps import AppConfig

from mlist.configuration import configure_backends, get_tmdb_configuration


class MListAppConfig(AppConfig):
    name = 'mlist'
    verbose_name = "MList"

    _TMDB_CONFIG = None

    @property
    def TMDB_CONFIG(self):
        if self._TMDB_CONFIG is None:
            self._TMDB_CONFIG = get_tmdb_configuration()
        return self._TMDB_CONFIG

    """
    Application startup. Called only once per installed application.
    """
    def ready(self):
        configure_backends()
