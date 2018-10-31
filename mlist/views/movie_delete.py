from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mlist.models import MovieInCollection

from .mixins import MessageMixin


@method_decorator(login_required, name='dispatch')
class MovieDelete(DeleteView, MessageMixin):
    model = MovieInCollection
    success_message = "Movie deleted successfully!"
    success_url = reverse_lazy('list-movies')
    template_name = "mlist/movie_delete.html"
    context_object_name = 'mic'

    def get_queryset(self):
        qs = super(MovieDelete, self).get_queryset()
        return qs.filter(collection__user=self.request.user)
