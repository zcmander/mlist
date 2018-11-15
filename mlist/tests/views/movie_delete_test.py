from django.test import TestCase
from django.test.client import RequestFactory
from mlist.views.movie_delete import MovieDelete
from mlist.models import User, Collection, Movie, MovieInCollection


class TestMovieDelete(TestCase):
    def test_get_queryset(self):
        request_factory = RequestFactory()

        movie = Movie.objects.create(
            title="Unit Test"
        )

        user = User.objects.create_user(
            username='javed',
            email='javed@javed.com',
            password='my_secret')
        collection2 = Collection.objects.create(
            user=user,
            title="watched"
        )
        collection1 = Collection.objects.create(
            user=user,
            title="favorites"
        )

        MovieInCollection(
            date="2018-11-15",
            collection=collection1,
            movie=movie,
        ).save()

        MovieInCollection(
            date="2018-11-15",
            collection=collection2,
            movie=movie,
        ).save()

        user2 = User.objects.create_user(
            username='javed2',
            email='javed@javed.com',
            password='my_secret')
        collection21 = Collection.objects.create(
            user=user2,
            title="watched"
        )
        collection22 = Collection.objects.create(
            user=user2,
            title="favorites"
        )

        MovieInCollection(
            date="2018-11-15",
            collection=collection21,
            movie=movie,
        ).save()

        MovieInCollection(
            date="2018-11-15",
            collection=collection22,
            movie=movie,
        ).save()

        MovieInCollection(
            date="2018-11-15",
            collection=collection22,
            movie=movie,
        ).save()

        view = MovieDelete()
        view.request = request_factory.get('/')
        view.request.user = user

        result = view.get_queryset()

        self.assertEqual(len(result), 2)
