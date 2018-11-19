from django.test import TestCase
from django.test.client import RequestFactory
from mlist.views.movie_list import MovieList
from mlist.models import User, Collection, MovieInCollection, Movie


class TestMovieList(TestCase):
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

    def test_get_queryset(self):
        movie = Movie.objects.create(
            title="Unit Test"
        )
        MovieInCollection(
            date="2018-11-15",
            collection=self.watched_collection,
            movie=movie
        ).save()

        request = self.request_factory.get("/")
        request.user = self.user

        view = MovieList()
        view.kwargs = {
            'collection': "watched"
        }
        view.request = request

        result = view.get_queryset()

        self.assertEqual(len(result), 1)

    def test_get_context_data(self):
        request = self.request_factory.get("/")
        request.user = self.user

        view = MovieList()
        view.request = request
        view.kwargs = {
            'collection': "watched"
        }

        view.object_list = view.get_queryset()

        result = view.get_context_data()

        self.assertEqual(result["collection_name"], "watched")
