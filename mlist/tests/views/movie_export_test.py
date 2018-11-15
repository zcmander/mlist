from django.test import TestCase
from django.test.client import RequestFactory
from mlist.views.movie_export import export_view
from mlist.models import User, Collection, Movie, MovieInCollection


class TestMovieExport(TestCase):
    def test_export_simple(self):
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
            title="watched"
        )

        mic0 = MovieInCollection(
            date="2018-11-15",
            collection=collection,
            movie=movie,
        )
        mic0.save()
        mic0.tags.add(*["location:Movie Theatre"])

        mic1 = MovieInCollection(
            date="2018-11-16",
            collection=collection,
            movie=movie,
        )
        mic1.save()
        mic1.tags.add(*["location:Home", "media:DVD"])

        request = request_factory.get('/')
        request.user = user
        response = export_view(request)

        self.assertEquals(
            response.content,
            b',14.11.2018,Unit Test,\r\nDVD,15.11.2018,Unit Test,\r\n')
