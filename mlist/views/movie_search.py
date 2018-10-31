from haystack.views import SearchView
from haystack.query import SearchQuerySet
from haystack.inputs import Raw

from mlist.models import MovieInCollection


class MovieSearch(SearchView):
    template = 'search/search.html'

    def get_results(self):
        sqs = SearchQuerySet()
        sqs = sqs.models(MovieInCollection)
        sqs = sqs.filter_and(collection__exact="watched")
        sqs = sqs.filter_and(collection_user=self.request.user.id)
        sqs = sqs.order_by("-date")

        if (self.form.is_valid()):
            sqs = sqs.filter_and(content=Raw(self.form.cleaned_data['q']))
            return sqs.all()
        return sqs.none()
