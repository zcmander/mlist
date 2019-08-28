import logging

from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager

from taggit.managers import TaggableManager

from mlist.apps import MListAppConfig

app_config = apps.get_app_config(MListAppConfig.name)

logger = logging.getLogger(__name__)


class IMDBMovie(models.Model):
    imdb_id = models.CharField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    year = models.IntegerField(null=True)
    rated = models.CharField(max_length=255, null=True)
    released = models.DateField(null=True)
    runtime = models.CharField(max_length=255, null=True)
    director = models.TextField(null=True)
    writer = models.TextField(null=True)
    actors = models.TextField(null=True)
    plot = models.TextField(null=True)
    votes = models.IntegerField(null=True)
    rating = models.FloatField(null=True)
    genre = models.TextField(null=True)

    poster_url = models.CharField(max_length=255, null=True)

    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u"{0} [{1}]".format(self.title, self.imdb_id)


class TMDBMovie(models.Model):
    imdb_id = models.CharField(max_length=255, unique=True, db_index=True)
    tmdb_id = models.CharField(max_length=255, unique=True)

    original_title = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    popularity = models.IntegerField(null=True)
    adult = models.NullBooleanField()
    spoken_languages = models.CharField(max_length=255)
    homepage = models.TextField(null=True)
    overview = models.TextField(null=True)
    vote_average = models.IntegerField(null=True)
    vote_count = models.IntegerField(null=True)
    runtime = models.IntegerField(null=True)
    budget = models.IntegerField(null=True)
    revenue = models.IntegerField(null=True)
    genres = models.TextField(null=True)
    production_companies = models.TextField(null=True)
    productions_countries = models.TextField(null=True)
    poster_path = models.TextField(null=True)
    backdrop_path = models.TextField(null=True)
    tagline = models.TextField(null=False)

    update_date = models.DateTimeField(auto_now=True)

    def get_poster_url(self, size):
        TMDB_CONFIG = app_config.TMDB_CONFIG

        base_url = TMDB_CONFIG["images"]["secure_base_url"]
        assert size in TMDB_CONFIG["images"]["poster_sizes"]
        return base_url + size + self.poster_path

    def get_backdrop_url(self, size):
        TMDB_CONFIG = app_config.TMDB_CONFIG

        base_url = TMDB_CONFIG["images"]["secure_base_url"]
        assert size in TMDB_CONFIG["images"]["backdrop_sizes"]
        return base_url + size + self.backdrop_path

    @property
    def thumbnail_poster_url(self):
        return self.get_poster_url("w185")

    @property
    def large_poster_url(self):
        return self.get_poster_url("w500")

    @property
    def backdrop_url(self):
        return self.get_backdrop_url('w780')

    @property
    def backdrop_orginal_url(self):
        return self.get_backdrop_url('original')

    def __str__(self):
        return u"{0} [{1}]".format(self.title, self.imdb_id)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    imdb_id = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        permissions = (
            ("update_movie", "Can update movie"),
        )

    def __str__(self):
        return u'{0} [{1}]'.format(self.title, self.imdb_id)

    @property
    def has_imdb(self):
        return IMDBMovie.objects.filter(imdb_id=self.imdb_id).first()

    @property
    def has_tmdb(self):
        return TMDBMovie.objects.filter(imdb_id=self.imdb_id).first()

    @property
    def thumbnail(self):
        if self.imdb_id:
            movie = TMDBMovie.objects.filter(imdb_id=self.imdb_id)[:1]
            if movie:
                return movie.get().thumbnail_poster_url

    @property
    def year(self):
        if self.imdb_id:
            movie = IMDBMovie.objects.filter(imdb_id=self.imdb_id)[:1]
            if movie:
                return movie.get().year
        return ''

    def get_title(self):
        if self.imdb_id:
            movie = IMDBMovie.objects.filter(imdb_id=self.imdb_id)[:1]
            if movie:
                return movie.get().title
        return self.title


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

    def add_int(self, key, value):
        BackendMovieIntAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_string(self, key, value):
        BackendMovieStringAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_date(self, key, value):
        BackendMovieDateAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_datetime(self, key, value):
        BackendMovieDateTimeAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_float(self, key, value):
        BackendMovieFloatAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)

    def add_json(self, key, value):
        BackendMovieJSONAttribute(backend_movie=self, key=key, value=value).save(force_insert=True)


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


class BackendMovieJSONAttribute(BackendMovieAttribute):
    value = models.TextField(blank=False, null=False)
