from django.test import TestCase
from django.test.client import RequestFactory
from mlist.views.movie_search import MovieSearch
from mlist.models import User, Collection, MovieInCollection, Movie

from mlist.search_indexes import MovieInCollectionIndex


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

    def test_view(self):
        movie = Movie.objects.create(
            title="Unit Test"
        )
        MovieInCollection(
            date="2018-11-15",
            collection=self.watched_collection,
            movie=movie
        ).save()

        data = {
            'models': ['mlist.movieincollection'],
            'q': 'Unit'
        }
        request = self.request_factory.get("/", data)
        request.user = self.user
        view = MovieSearch()

        response = view(request)

        self.assertIsNotNone(response)

    def test_get_results(self):
        movie = Movie.objects.create(
            title="Unit Test"
        )
        MovieInCollection(
            date="2018-11-15",
            collection=self.watched_collection,
            movie=movie
        ).save()

        data = {
            'models': ['mlist.movieincollection'],
            'q': 'Unit'
        }
        request = self.request_factory.get("/", data)
        request.user = self.user

        view = MovieSearch()
        view.request = request
        view.form = view.build_form()

        idx = MovieInCollectionIndex()
        idx.reindex()

        result = view.get_results()

        self.assertEqual(len(result), 1)
