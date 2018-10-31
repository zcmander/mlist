from haystack import indexes
from mlist.models import MovieInCollection


class MovieInCollectionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField()
    date = indexes.DateField(model_attr="date")
    collection = indexes.CharField(model_attr="collection__title")
    collection_user = indexes.IntegerField()
    id = indexes.IntegerField(model_attr="id")
    tags = indexes.CharField()

    def get_model(self):
        return MovieInCollection

    def prepare_title(self, obj):
        return obj.movie.get_title()

    def prepare_collection_user(self, obj):
        return obj.collection.user.id

    def prepare(self, object):
        self.prepared_data = super(MovieInCollectionIndex, self) \
            .prepare(object)

        self.prepared_data['tags'] = [tag.name for tag in object.tags.all()]
        return self.prepared_data
