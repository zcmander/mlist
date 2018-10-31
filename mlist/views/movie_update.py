from django.urls import reverse
from django.views.generic import UpdateView
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from mlist.forms import MovieEditForm
from mlist.models import MovieInCollection

from .mixins import MessageMixin


@method_decorator(
    permission_required('mlist.can_update_movie'),
    name='dispatch')
class MovieUpdate(UpdateView, MessageMixin):
    model = MovieInCollection
    template_name = "mlist/movie_update.html"
    form_class = MovieEditForm
    success_message = "Updated movie successfully!"

    def get_success_url(self):
        return reverse('detail-movie', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        kwargs = super(MovieUpdate, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.movie.title = form.cleaned_data['title']
        instance.movie.imdb_id = form.cleaned_data['imdb_id']
        instance.movie.save()
        instance.tags.set(*form.cleaned_data['tags'])
        instance.save()
        form.save_m2m()
        return super(MovieUpdate, self).form_valid(form)
