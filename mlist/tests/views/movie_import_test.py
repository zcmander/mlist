import mock
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from mlist.views.movie_import import MovieImport
from mlist.models import User, Collection, MovieInCollection, Movie


class TestMovieImport(TestCase):
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

    def mock_message_middleware(self, request):
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

    @mock.patch('mlist.omdbapi.urlopen')
    def test_form_valid(self, mockurlopen):
        data = {
            'data': ',14.11.2018,Unit Test,\r\nDVD,15.11.2018,Unit Test,\r\n'
        }

        request = self.request_factory.post('/', data)
        request.user = self.user
        self.mock_message_middleware(request)

        response = MovieImport.as_view()(request)

        self.assertEqual(response.status_code, 302)

        movies = Movie.objects.all()
        mics = MovieInCollection.objects.all()
        self.assertEqual(len(mics), 2)
        self.assertEqual(len(movies), 1)
