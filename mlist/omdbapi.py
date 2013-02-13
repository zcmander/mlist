import urllib
import urllib2
import json
import datetime

class BackendOMDB:
    """
    Backend for Internet Movie Database, using OMDB Api
    """

    __base_url = "http://www.omdbapi.com/"

    def _create_url(self, title=None, imdb_id=None):
        """
        Utility function to create url to datasource
        """
        url = self.__base_url

        if imdb_id != None:
            url += "?i=" + urllib.quote(imdb_id)
        elif title != None:
            url += "?t=" + urllib.quote(title)
        else:
            raise Exception('imdb_id OR title MUST be provided')

        url += "&plot=full"

        return url


    def _parse_json(self, data):
        """
        Returns None, but parses 'data' to 'movie_info'
        """

        movie_info = {}

        # Convert N/A to None
        for key in data:
            if data[key] == 'N/A':
                data[key] = None

        movie_info['title'] = data.get('Title', None)

        movie_info['year'] = data.get('Year', None)
        movie_info['rated'] = data.get('Rated', None)

        try:
            movie_info['released'] = datetime.datetime.strptime(data.get('Released', None), "%d %b %Y")
        except ValueError:
            movie_info['released'] = datetime.datetime.strptime(data.get('Released', None), "%b %Y")
        except:
            movie_info['released'] = None

        movie_info['runtime'] = data.get('Runtime', None)
        movie_info['director'] = data.get('Director', None)
        movie_info['writer'] = data.get('Writer', None)
        movie_info['actors'] = data.get('Actors', None)
        movie_info['plot'] = data.get('Plot', None)

        try:
            movie_info['votes'] = (int)(data['imdbVotes'].replace(",", ''))
        except:
            movie_info['votes'] = None

        try:
            movie_info['rating'] = (float)(data.get('imdbRating', None))
        except:
            movie_info['rating'] = None

        movie_info['genre'] = data.get('Genre', None)
        movie_info['poster_url'] = data.get('Poster', None)
        movie_info['imdb_id'] = data.get('imdbID')

        return movie_info

    def _get_data_from_source(self, url):
        """
        Creates HTTP connection to datasource and passes it to JSON-parser
        """
        conn = urllib2.urlopen(url)
        rawdata = conn.read()
        data = json.loads(rawdata)

        if data['Response'] != 'True':
            # TODO: Add logging for unexcepted responses
            if 'Error' in data:
                raise Exception(data['Error'])
            raise Exception(data['Response'])

        return data

    def get_data(self, title=None, imdb_id=None):
        url = self._create_url(title=title,  imdb_id=imdb_id)
        return self._parse_json(self._get_data_from_source(url))