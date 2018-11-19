from datetime import datetime

import unicodecsv as csv
from six import BytesIO

from django.urls import reverse
from django.views.generic import FormView
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mlist.forms import ImportForm
from mlist.models import Movie, MovieInCollection, Collection


@method_decorator(login_required, name='dispatch')
class MovieImport(FormView):
    form_class = ImportForm
    template_name = 'mlist/import_movies.html'
    success_message = "All movies imported successfully!"

    def form_valid(self, form):
        csv_data = form.cleaned_data['data'].encode("utf-8")
        csv_file = BytesIO(csv_data)
        reader = csv.reader(csv_file, delimiter=",", quotechar="\"", encoding="utf-8")

        for row in reader:
            title = row[2]
            imdb_id = row[3]
            date = datetime.strptime(row[1], "%d.%m.%Y")
            date = datetime.combine(date, datetime.now().time())
            media = row[0]

            has_imdb = imdb_id is True

            movie = None

            if has_imdb:
                mlist = Movie.objects.filter(imdb_id=imdb_id)[:1]
                if mlist:
                    movie = mlist.get()
            else:
                mlist = Movie.objects.filter(title=title)[:1]
                if mlist:
                    movie = mlist.get()

            if not movie:
                movie = Movie()
                movie.title = row[2]
                if row[3]:
                    movie.imdb_id = row[3]
                movie.save()

            collection = Collection.objects\
                .filter(
                    user=self.request.user,
                    title="watched"
                )[:1].get()

            mic = MovieInCollection()
            mic.movie = movie
            mic.collection = collection
            mic.date = date
            mic.save()
            mic.tags.add("media:" + media)

        messages.success(self.request, self.success_message)
        return redirect(reverse('list-movies'))
