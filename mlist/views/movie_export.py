import datetime
import json

import unicodecsv as csv

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from mlist.models import MovieInCollection, Collection


@login_required()
def export_view(request):
    def get_media_tag(tags):
        for tag in tags:
            if str(tag).startswith("media:"):
                return str(tag)[len("media:"):]
        return ''

    response = HttpResponse(content_type='text/csv')
    todaystr = datetime.date.today().strftime("%d%m%y")
    response['Content-Disposition'] = 'attachment; filename="exported-movies-' + todaystr + '.csv"'

    writer = csv.writer(response)

    collection = Collection.objects.filter(user=request.user, title="watched").get()
    for mic in collection.movieincollection_set.order_by("date").all():
        media = get_media_tag(mic.tags.all())
        title = mic.movie.get_title()
        imdb_id = mic.movie.imdb_id if mic.movie.imdb_id else ''
        date = None
        if mic.date:
            date = mic.date.strftime(u"%d.%m.%Y")

        writer.writerow([media, date, title, imdb_id])
    return response


class MovieInCollectionExportJsonEncode(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MovieInCollection):
            r = {
                'id': obj.id,
                'date': obj.date,
                'tags': [str(x) for x in obj.tags.all()],
                'movie': {
                    'id': obj.movie.id,
                    'title': obj.movie.get_title(),
                    'imdb_id': obj.movie.imdb_id,
                },
                'collection': {
                    'id': obj.collection.id,
                    'title': obj.collection.title,
                },
            }

            imdb_movie = obj.movie.has_imdb
            if imdb_movie:
                imdb_info = {
                    'year': imdb_movie.year,
                    'released': imdb_movie.released,
                    'genres': [x.strip() for x in imdb_movie.genre.split(",")],
                    'rating': imdb_movie.rating,
                }

                r['movie']['imdb'] = imdb_info


            return r
        if isinstance(obj, datetime.datetime) or \
           isinstance(obj, datetime.date):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


@login_required()
def adv_export_view(request):
    collection = Collection.objects.filter(user=request.user, title="watched").get()
    movies = list(collection.movieincollection_set.order_by("date").all())
    content = json.dumps(movies, cls=MovieInCollectionExportJsonEncode, indent=4)

    return HttpResponse(content, content_type="application/json")
