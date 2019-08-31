from django.test import TestCase
from django.test.client import RequestFactory
from mlist.views.movie_detail import MovieDetail
from mlist.models import User, Collection, Movie, MovieInCollection


class TestMovieDetail(TestCase):
    def test_get_context_data(self):
        request_factory = RequestFactory()

        movie = Movie.objects.create(
            title="Unit Test"
        )

        user = User.objects.create_user(
            username='javed',
            email='javed@javed.com',
            password='my_secret')
        collection = Collection.objects.create(
            user=user,
            title="watched")
        MovieInCollection(
            date="2018-11-15",
            collection=collection,
            movie=movie
        ).save()

        view = MovieDetail()
        view.request = request_factory.get('/')
        view.request.user = user
        view.kwargs = {
            'pk': movie.id
        }
        view.object = view.get_object()

        result = view.get_context_data()

        self.assertFalse(result["has_imdb"])
        self.assertFalse(result["has_tmdb"])
        self.assertEqual(1, len(result["watchedmics"]))
        self.assertEqual(0, len(result["collections"]))
