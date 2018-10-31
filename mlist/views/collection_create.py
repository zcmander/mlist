from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mlist.forms import CollectionForm
from mlist.models import Collection

from .mixins import MessageMixin


@method_decorator(login_required, name='dispatch')
class CollectionCreate(CreateView, MessageMixin):
    model = Collection
    form_class = CollectionForm
    success_message = "Collection created successfully!"
    success_url = reverse_lazy('settings')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        return super(CollectionCreate, self).form_valid(form)
