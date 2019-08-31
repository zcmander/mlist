import logging

from django.db import models
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager

from taggit.managers import TaggableManager

from mlist.poster import get_poster_url
from mlist.backdrop import get_backdrop_url

logger = logging.getLogger(__name__)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    imdb_id = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        permissions = (
            ("update_movie", "Can update movie"),
        )

    def __str__(self):
        return u'{0} [{1}]'.format(self.title, self.imdb_id)

    def has_backend(self, name):
        return BackendMovie.objects \
            .filter(movie=self) \
            .filter(backend=name) \
            .first() is not None

    @property
    def attributes(self):
        # TODO: Order by backend priority
        return BackendMovieAttribute.objects \
            .filter(backend_movie__movie=self) \
            .select_subclasses()

    def get_attribute(self, key, default=None):
        attribute = self.attributes.filter(key=key).first()
        if attribute:
            return attribute.value
        return default

    @property
    def has_imdb(self):
        return self.has_backend("imdb")

    @property
    def has_tmdb(self):
        return self.has_backend("tmdb")

    @property
    def thumbnail_url(self):
        return get_poster_url(self, 'LIST')

    @property
    def poster_url(self):
        return get_poster_url(self, 'DETAIL')

    @property
    def backdrop_url(self):
        return get_backdrop_url(self)

    def get_imdb_id(self):
        return self.get_attribute("imdb_id", self.imdb_id)

    def get_title(self):
        return self.get_attribute("title", self.title)

    def get_year(self):
        return self.get_attribute("year")


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    movies = models.ManyToManyField(
        Movie,
        through='MovieInCollection',
        blank=True)

    def __str__(self):
        return u"{0} ({1})".format(self.title, self.movies.count())


class MovieInCollection(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    date = models.DateTimeField()
    tags = TaggableManager(blank=True)

    def __str__(self):
        return u'[{0}, {1}] {2}'.format(
            self.collection.user,
            self.date,
            self.movie.title)


class BackendMovie(models.Model):
    """
    Represent a movie in a external system.
    """
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="backend_movie")

    # Backend idenfitier
    backend = models.CharField(max_length=100, null=False)

    fetched = models.DateTimeField(null=False, auto_now=True)

    @property
    def imdb_id(self):
        attribute = BackendMovieAttribute.objects \
            .select_subclasses() \
            .filter(backend_movie=self, key="imdb_id") \
            .first()
        if attribute:
            return attribute.value

    def add_int(self, key, value):
        if not value:
            return
        BackendMovieIntAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_string(self, key, value):
        if not value:
            return
        BackendMovieStringAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_date(self, key, value):
        if not value:
            return
        BackendMovieDateAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_datetime(self, key, value):
        if not value:
            return
        BackendMovieDateTimeAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_float(self, key, value):
        if not value:
            return
        BackendMovieFloatAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_json(self, key, value):
        if not value:
            return
        BackendMovieJSONAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_boolean(self, key, value):
        if not value:
            return
        BackendMovieBooleanAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)


class BackendMovieAttribute(models.Model):
    """
    A single pice of infomation of the backend movie.
    """
    backend_movie = models.ForeignKey(
        BackendMovie,
        on_delete=models.CASCADE,
        related_name='attributes')

    key = models.CharField(max_length=200)

    objects = InheritanceManager()

    class Meta:
        unique_together = (('backend_movie', 'key'),)


class BackendMovieIntAttribute(BackendMovieAttribute):
    value = models.IntegerField(blank=False, null=False)
    unit = models.CharField(max_length=200)


class BackendMovieFloatAttribute(BackendMovieAttribute):
    value = models.FloatField(blank=False, null=False)
    unit = models.CharField(max_length=200)


class BackendMovieStringAttribute(BackendMovieAttribute):
    value = models.TextField(blank=False, null=False)


class BackendMovieDateAttribute(BackendMovieAttribute):
    value = models.DateField(blank=False, null=False)


class BackendMovieDateTimeAttribute(BackendMovieAttribute):
    value = models.DateTimeField(blank=False, null=False)


class BackendMovieBooleanAttribute(BackendMovieAttribute):
    value = models.BooleanField(blank=False, null=False)


class BackendMovieJSONAttribute(BackendMovieAttribute):
    value = models.TextField(blank=False, null=False)
