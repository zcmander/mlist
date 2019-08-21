import json
import mock
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from mlist.views.movie_create import MovieCreate, ajax_taglist_view
from mlist.models import User, Collection, MovieInCollection, Movie


class TestMovieCreate(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='javed',
            email='javed@javed.com',
            password='my_secret')
        self.watched_collection = Collection.objects.create(
            user=self.user,
            title="watched"
        )
        self.favorite_collection = Collection.objects.create(
            user=self.user,
            title="favorites"
        )

    def mock_message_middleware(self, request):
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

    def test_get_initial(self):
        view = MovieCreate()
        view.request = self.request_factory.get('/')
        view.request.user = self.user
        result = view.get_initial()

        self.assertEqual(self.watched_collection, result["collection"])

    def test_get_initial_when_collection_specified(self):
        view = MovieCreate()
        view.request = self.request_factory.get('/?collection=favorites')
        view.request.user = self.user
        result = view.get_initial()

        self.assertEqual(self.favorite_collection, result["collection"])

    def test_get_form_kwargs(self):
        view = MovieCreate()
        view.request = self.request_factory.get('/')
        view.request.user = self.user

        result = view.get_form_kwargs()

        self.assertEqual(view.request, result["request"])

    @mock.patch('mlist.omdbapi.urlopen')
    def test_form_valid(self, mockurlopen):
        data = {
            'title': "Dark knight",
            "tags": "hello, world",
            "date": "12.11.2018",
            "imdb_id": "tt0468569",
            "collection": self.watched_collection.id,
        }

        request = self.request_factory.post('/', data)
        request.user = self.user
        self.mock_message_middleware(request)

        response = MovieCreate.as_view()(request)

        self.assertEqual(response.status_code, 302)

        movies = Movie.objects.all()
        mics = MovieInCollection.objects.all()
        self.assertEqual(len(mics), 1)
        self.assertEqual(len(movies), 1)


class AjaxTagListViewTest(TestCase):
    def test_simple(self):
        request_factory = RequestFactory()
        request = request_factory.get("/")

        user = User.objects.create(
            username='javed',
            email='javed@javed.com',
            password='my_secret'
        )

        request.user = user

        collection = Collection.objects.create(
            title="unittest",
            user=user,
        )

        movie = Movie.objects.create(
            title="Hello World!",
        )

        mic = MovieInCollection.objects.create(
            date="2018-11-10",
            collection=collection,
            movie=movie
        )
        mic.save()
        mic.tags.add(*["hello", "world"])

        response = ajax_taglist_view(request)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)

        tags = sorted(content)

        self.assertEqual(tags[0], 'hello')
        self.assertEqual(tags[1], 'world')
