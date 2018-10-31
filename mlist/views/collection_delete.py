from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mlist.models import Collection

from .mixins import MessageMixin


@method_decorator(login_required, name='dispatch')
class CollectionDelete(DeleteView, MessageMixin):
    model = Collection
    success_message = "Collection deleted successfully!"
    success_url = reverse_lazy('settings')
    context_object_name = 'collection'

    def get_queryset(self):
        qs = super(CollectionDelete, self).get_queryset()
        return qs.filter(user=self.request.user)
