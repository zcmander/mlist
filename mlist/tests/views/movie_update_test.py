from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from mlist.views.movie_update import MovieUpdate
from mlist.models import User, Collection, MovieInCollection, Movie


class TestMovieUpdate(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='javed',
            email='javed@javed.com',
            password='my_secret',
            is_superuser=True)

        self.watched_collection = Collection.objects.create(
            user=self.user,
            title="watched"
        )

    def mock_message_middleware(self, request):
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

    def test_form_valid(self):
        movie = Movie.objects.create(
            title="Unit Test"
        )
        mic = MovieInCollection(
            date="2018-11-15",
            collection=self.watched_collection,
            movie=movie
        )
        mic.save()

        data = {
            'pk': mic.id,
            'title': "Dark knight",
            "tags": "hello, world",
            "date": "2018-11-22",
            "imdb_id": "tt0468569",
            "collection": self.watched_collection.id,
        }
        request = self.request_factory.post('/', data)
        request.user = self.user
        self.mock_message_middleware(request)

        view = MovieUpdate.as_view()
        response = view(request, pk=mic.id)

        self.assertEqual(response.status_code, 302)

        movies = Movie.objects.all()
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0].title, "Dark knight")
        self.assertEqual(movies[0].imdb_id, "tt0468569")
