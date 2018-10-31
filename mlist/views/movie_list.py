from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mlist.models import MovieInCollection, Collection


@method_decorator(login_required, name='dispatch')
class MovieList(ListView):
    model = MovieInCollection

    context_object_name = 'movies'
    template_name = 'mlist/movie_list.html'
    paginate_by = 6 * 6

    def get_queryset(self):
        collection = Collection.objects \
            .filter(
                user=self.request.user,
                title=self.kwargs['collection']
            )[:1].get()

        return collection.movieincollection_set \
            .order_by('-date') \
            .select_related() \
            .all()

    def get_context_data(self, **kwargs):
        context = super(MovieList, self).get_context_data(**kwargs)
        context['collection_name'] = self.kwargs['collection']
        return context
