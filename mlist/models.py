from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

from mlist.omdbapi import BackendOMDB

from .tmdb import configure, Core, Movies, config

configure("492ffa13c4f4eedb4599ee3a803487de")

core = Core()
core.update_configuration()


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

    @classmethod
    def create(cls, title=None, imdb_id=None):
        self = cls()
        if title or imdb_id:
            result = BackendOMDB().get_data(title, imdb_id)
            self.imdb_id = result.get('imdb_id')
            self.title = result.get('title')
            self.year = result.get('year')[:4]
            self.rated = result.get('rated')
            self.released = result.get('released')
            self.runtime = result.get('runtime')
            self.director = result.get('director')
            self.writer = result.get('writer')
            self.actors = result.get('actors')
            self.plot = result.get('plot')
            self.votes = result.get('votes')
            self.rating = result.get('rating')
            self.genre = result.get('genre')
            self.poster_url = result.get('poster_url')
        return self

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

    @classmethod
    def create(cls, title, imdb_id=None):
        self = cls()

        tmdb_movies = Movies(title=title, limit=True)
        tmdb_movie = None

        if tmdb_movies.get_total_results() > 0:
            if imdb_id:
                for movie in tmdb_movies:
                    print(movie.get_imdb_id(), imdb_id)
                    if movie.get_imdb_id() == imdb_id:
                        tmdb_movie = movie
            else:
                tmdb_movie = iter(tmdb_movies).next()

            if not tmdb_movie:
                raise Exception("Movie not found! (TMDB)")

            spoken_language_names = [
                x['name'] for x in tmdb_movie.get_spoken_languages()
            ]

            production_company_names = [
                x['name'] for x in tmdb_movie.get_production_companies()
            ]

            productions_country_names = [
                x['name'] for x in tmdb_movie.get_productions_countries()
            ]

            genre_names = [
                x['name'] for x in tmdb_movie.get_genres()
            ]

            self.imdb_id = tmdb_movie.get_imdb_id()
            self.tmdb_id = tmdb_movie.get_id()
            self.original_title = tmdb_movie.get_original_title()
            self.title = tmdb_movie.get_title()
            self.popularity = tmdb_movie.get_popularity()
            self.adult = tmdb_movie.is_adult()
            self.spoken_languages = ','.join(spoken_language_names)
            self.homepage = tmdb_movie.get_homepage()
            self.overview = tmdb_movie.get_overview()
            self.vote_average = tmdb_movie.get_vote_average()
            self.vote_count = tmdb_movie.get_vote_count()
            self.runtime = tmdb_movie.get_runtime()
            self.budget = tmdb_movie.get_budget()
            self.revenue = tmdb_movie.get_revenue()
            self.genres = ','.join(genre_names)
            self.production_companies = ','.join(production_company_names)
            self.productions_countries = ','.join(productions_country_names)
            self.poster_path = tmdb_movie.get_poster_path()
            self.backdrop_path = tmdb_movie.get_backdrop_path()
            self.tagline = tmdb_movie.get_tagline()

        return self

    @property
    def thumbnail_poster_url(self):
        return config.get('api', {}).get('base.url') + \
               core.poster_sizes('m') + \
               self.poster_path

    @property
    def large_poster_url(self):
        return config.get('api', {}).get('base.url') + \
               core.poster_sizes('l') + \
               self.poster_path

    @property
    def backdrop_url(self):
        return config.get('api', {}).get('base.url') + \
               core.backdrop_sizes('s') + \
               self.backdrop_path

    @property
    def backdrop_orginal_url(self):
        return config.get('api', {}).get('base.url') + \
               core.backdrop_sizes('o') + \
               self.backdrop_path

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
        try:
            return IMDBMovie.objects.filter(imdb_id=self.imdb_id).get()
        except IMDBMovie.DoesNotFound:
            return False

    @property
    def has_tmdb(self):
        try:
            return TMDBMovie.objects.filter(imdb_id=self.imdb_id).get()
        except TMDBMovie.DoesNotFound:
            return False

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
