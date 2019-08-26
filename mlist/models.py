import logging

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

from mlist.apps import MListAppConfig

from django.apps import apps

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


admin.site.register(TMDBMovie)
admin.site.register(IMDBMovie)
