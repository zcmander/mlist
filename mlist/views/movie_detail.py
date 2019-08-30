from collections import namedtuple, OrderedDict

from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mlist.models import MovieInCollection, IMDBMovie, TMDBMovie, BackendMovieAttribute

DisplayAttribute = namedtuple('DisplayAttribute', [
    'title',
    'type'
])


class MovieAttributes:
    def __init__(self, attributes):
        self._data = attributes

    def __getattr__(self, key):
        return self._data[key]

    def has(self, key):
        return key in self._data

    def get(self, key):
        return self._data.get(key)


@method_decorator(login_required, name='dispatch')
class MovieDetail(DetailView):
    model = MovieInCollection
    context_object_name = 'mic'
    template_name = 'mlist/movie_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MovieDetail, self).get_context_data(**kwargs)

        qs = self.object.movie.movieincollection_set
        qs = qs.filter(collection__user=self.request.user)
        context['watchedmics'] = qs.filter(collection__title="watched").all()
        context['collections'] = qs.exclude(collection__title="watched").all()

        context['imdb'] = IMDBMovie.objects \
            .filter(imdb_id=self.object.movie.imdb_id).first()

        context['tmdb'] = TMDBMovie.objects \
            .filter(imdb_id=self.object.movie.imdb_id).first()

        attributes = BackendMovieAttribute.objects \
            .filter(backend_movie__movie=self.object.movie).select_subclasses().all()

        # Convert to dict
        attributes_dict = {}
        for attribute in attributes:
            attributes_dict[attribute.key] = attribute.value

        if 'title' not in attributes_dict:
            attributes_dict["title"] = self.object.movie.title

        movie_attributes = MovieAttributes(attributes_dict)
        context['attributes'] = movie_attributes

        context["has_poster"] = any([
            'imdb.poster_url' in attributes_dict,
            'tmdb.poster_path' in attributes_dict
        ])
        context["has_backdrop"] = any([
            'tmdb.backdrop_path' in attributes_dict,
        ])

        context["has_overview"] = any([
            attr in attributes_dict
            for attr in [
                'released',
                'runtime',
                'genres',
                'imdb.rating',
                'tmdb.vote_average',
            ]])

        context["has_share"] = any([
            'imdb_id' in attributes_dict,
        ])

        detail_display = OrderedDict([
            ["director", DisplayAttribute("Director", 'text')],
            ["writer", DisplayAttribute("Writer", 'brlist')],
            ["actors", DisplayAttribute("Actors", 'brlist')],
            ["production_companies", DisplayAttribute("Companies", 'brlist')],
            ["spoken_languages", DisplayAttribute("Spoken languages", 'brlist')],
            ["homepage", DisplayAttribute("Homepage", 'link')],
            ["budget", DisplayAttribute("Budget", 'intcomma')],
            ["revenue", DisplayAttribute("Revenue", 'intcomma')],
        ])

        context["has_details"] = any([
            attr in attributes_dict
            for attr in detail_display.keys()])

        context['details'] = [(
            detail_display[key].title,
            movie_attributes.get(key),
            detail_display[key].type
        ) for key in detail_display.keys()]

        context['debug'] = sorted(attributes_dict.items())

        return context
