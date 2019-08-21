from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mlist.models import MovieInCollection, IMDBMovie, TMDBMovie


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
        return context
