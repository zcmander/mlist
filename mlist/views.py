import csv
import json
import codecs
import StringIO
import datetime

from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, FormView, DeleteView, UpdateView, CreateView
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.db.models import Count

from haystack.views import SearchView
from haystack.query import SearchQuerySet
from haystack.inputs import Raw

from mlist.forms import MovieForm, ImportForm, MovieEditForm, CollectionForm
from mlist.models import Movie, MovieInCollection, Collection, IMDBMovie, TMDBMovie


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class MessageMixin(object):
    """
    Make it easy to display notification messages when using Class Based Views.
    """
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)


class MovieCreate(FormView):
    form_class = MovieForm
    template_name = 'mlist/movie_form.html'
    success_message = "Movie added successfully!"

    def get_initial(self):
        collection = None
        collection_query = Collection.objects.filter(user=self.request.user,
                                                     title=self.request.GET.get("collection", "watched"))
        if collection_query:
            collection = collection_query.get()

        return {
            'title': self.request.GET.get("title"),
            'imdb_id': self.request.GET.get("imdb_id"),
            'collection': collection
        }

    def get_form_kwargs(self):
        kwargs = super(MovieCreate, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        title = form.cleaned_data['title']
        tags = form.cleaned_data['tags']
        date = form.cleaned_data['date']
        #date = datetime.datetime.combine(date, datetime.datetime.now().time())
        imdb_id = form.cleaned_data['imdb_id']

        collection = form.cleaned_data['collection']

        movie = None
        imdb_movie = None
        try:
            if imdb_id:
                movie = Movie.objects.get(imdb_id=imdb_id)
            else:
                movie = Movie.objects.get(title=title)
        except Movie.DoesNotExist:
            movie = Movie()
            movie.title = title
            movie.imdb_id = None
            movie.save()

        if not movie or not movie.imdb_id or not IMDBMovie.objects.filter(imdb_id=movie.imdb_id).all():

            try:
                if imdb_id:
                    imdb_movie = IMDBMovie.create(imdb_id=imdb_id)
                else:
                    imdb_movie = IMDBMovie.create(title=title)
            except Exception as e:
                messages.error(self.request, u"<strong>Error while fetching IMDB information:</strong>" + e.__class__.__name__ + u":" + unicode(e.message), extra_tags='safe')

            if imdb_movie and imdb_movie.imdb_id:
                try:
                    movie = Movie.objects.get(imdb_id=imdb_movie.imdb_id)
                except Movie.DoesNotExist:
                    pass

            if imdb_movie and not IMDBMovie.objects.filter(imdb_id=imdb_movie.imdb_id).all():
                imdb_movie.save()

                if movie and not movie.imdb_id:  # If movie without IMDB ID then update it
                    movie.imdb_id = imdb_movie.imdb_id
                    movie.save()

        if movie.imdb_id and not TMDBMovie.objects.filter(imdb_id=movie.imdb_id).all():
            try:
                tmdb_movie = TMDBMovie.create(movie.get_title(), imdb_id=movie.imdb_id)
                tmdb_movie.save()
            except Exception as e:
                messages.error(self.request, u"<strong>Error while fetching TMDB information:</strong>" + unicode(e.__class__.__name__) + u":" + e.message, extra_tags='safe')

        mic = MovieInCollection()
        mic.movie = movie
        mic.collection = collection
        mic.date = date

        mic.save()
        mic.tags.add(*tags)

        messages.success(self.request, self.success_message)
        return redirect(reverse('detail-movie', args=[mic.id]))


class MovieImport(FormView):
    form_class = ImportForm
    template_name = 'mlist/import_movies.html'
    success_message = "All movies imported successfully!"

    def form_valid(self, form):
        csv_data = form.cleaned_data['data']
        csv_file = StringIO.StringIO(csv_data)
        reader = UnicodeReader(csv_file, delimiter=",", quotechar="\"")

        for row in reader:
            title = row[2]
            imdb_id = row[3]
            date = datetime.datetime.strptime(row[1], "%d.%m.%Y")
            date = datetime.datetime.combine(date, datetime.datetime.now().time())
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

            collection = Collection.objects.filter(user=self.request.user, title="watched")[:1].get()

            mic = MovieInCollection()
            mic.movie = movie
            mic.collection = collection
            mic.date = date
            mic.save()
            mic.tags.add("media:" + media)

        messages.success(self.request, self.success_message)
        return redirect(reverse('list-movies'))


class MovieList(ListView):
    model = MovieInCollection

    #queryset=MovieInCollection.objects.order_by('id')
    context_object_name = 'movies'
    template_name = 'mlist/movie_list.html'
    paginate_by = 6 * 6

    def get_queryset(self):
        collection = Collection.objects.filter(user=self.request.user, title=self.kwargs['collection'])[:1].get()
        return collection.movieincollection_set.order_by('-date').select_related().all()

    def get_context_data(self, **kwargs):
        context = super(MovieList, self).get_context_data(**kwargs)
        context['collection_name'] = self.kwargs['collection']
        return context


class MovieDetail(DetailView):
    model = MovieInCollection
    context_object_name = 'mic'
    template_name = 'mlist/movie_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MovieDetail, self).get_context_data(**kwargs)

        qs = self.object.movie.movieincollection_set
        qs = qs.filter(collection__user=self.request.user)
        context['watchedmics'] = qs.filter(collection__title="watched").all()
        context['collections'] = qs.exclude(collection__title="watched").all()

        try:
            context['imdb'] = IMDBMovie.objects.filter(imdb_id=self.object.movie.imdb_id)[:1].get()
        except IMDBMovie.DoesNotExist:
            context['imdb'] = None

        try:
            context['tmdb'] = TMDBMovie.objects.filter(imdb_id=self.object.movie.imdb_id)[:1].get()
        except TMDBMovie.DoesNotExist:
            context['tmdb'] = None
        return context


class MovieUpdate(UpdateView, MessageMixin):
    model = MovieInCollection
    template_name = "mlist/movie_update.html"
    form_class = MovieEditForm
    success_message = "Updated movie successfully!"

    def get_success_url(self):
        return reverse('detail-movie', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        kwargs = super(MovieUpdate, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.movie.title = form.cleaned_data['title']
        instance.movie.imdb_id = form.cleaned_data['imdb_id']
        instance.movie.save()
        instance.tags.set(*form.cleaned_data['tags'])
        instance.save()
        form.save_m2m()
        return super(MovieUpdate, self).form_valid(form)


class MovieDelete(DeleteView, MessageMixin):
    model = MovieInCollection
    success_message = "Movie deleted successfully!"
    success_url = reverse_lazy('list-movies')
    template_name = "mlist/movie_delete.html"
    context_object_name = 'mic'

    def get_queryset(self):
        qs = super(MovieDelete, self).get_queryset()
        return qs.filter(collection__user=self.request.user)


class MovieSearch(SearchView):
    template = 'search/search.html'

    def get_results(self):
        sqs = SearchQuerySet()
        sqs = sqs.models(MovieInCollection)
        sqs = sqs.filter_and(collection__exact="watched")
        sqs = sqs.filter_and(collection_user=self.request.user.id)
        sqs = sqs.order_by("-date")

        if (self.form.is_valid()):
            sqs = sqs.filter_and(content=Raw(self.form.cleaned_data['q']))
            return sqs.all()
        return sqs.none()


class CollectionCreate(CreateView, MessageMixin):
    model = Collection
    form_class = CollectionForm
    success_message = "Collection created successfully!"
    success_url = reverse_lazy('settings_view')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        return super(CollectionCreate, self).form_valid(form)


class CollectionDelete(DeleteView, MessageMixin):
    model = Collection
    success_message = "Collection deleted successfully!"
    success_url = reverse_lazy('settings')
    context_object_name = 'collection'

    def get_queryset(self):
        qs = super(CollectionDelete, self).get_queryset()
        return qs.filter(user=self.request.user)


def authenticate_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect(reverse('list-movies'))
        else:
            messages.error(request, 'Disabled user.')
            return redirect(reverse('login'))
    else:
        messages.error(request, 'Invalid username or password.')
        return redirect(reverse('login'))


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))


def login_view(request):
    if request.user and request.user.is_authenticated():
        return redirect(reverse('list-movies'))
    return render_to_response("mlist/login.html", RequestContext(request))


@login_required()
def fetch_imdb_view(request, pk):
    movie = Movie.objects.get(pk=int(pk))
    imdb_movie = IMDBMovie.create(title=movie.title, imdb_id=movie.imdb_id)
    if not IMDBMovie.objects.filter(imdb_id=imdb_movie.imdb_id).all():
        imdb_movie.save()
        if not movie.imdb_id:  # If movie without IMDB ID then update it
            movie.imdb_id = imdb_movie.imdb_id
            movie.save()
    elif not movie.imdb_id:  # If movie without IMDB ID then update it
        movie.imdb_id = imdb_movie.imdb_id
        movie.save()

    messages.success(request, 'IMDB information fetched.')
    return redirect(reverse("list-movies"))


@login_required()
def fetch_tmdb_view(request, pk):
    movie = Movie.objects.get(pk=int(pk))
    if not movie.imdb_id:
        messages.error(request, 'TMDB information requires IMDB id before fetch.')
        return redirect(reverse("list-movies"))

    tmdb_movie = TMDBMovie.create(title=movie.title, imdb_id=movie.imdb_id)
    if not TMDBMovie.objects.filter(imdb_id=tmdb_movie.imdb_id).all():
        tmdb_movie.save()

    messages.success(request, 'TMDB information fetched.')
    return redirect(reverse("list-movies"))


@login_required()
def export_view(request):
    def get_media_tag(tags):
        for tag in tags:
            if unicode(tag).startswith("media:"):
                return unicode(tag)[len("media:"):]
        return ''

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exported-movies-' + datetime.date.today().strftime("%d%m%y") + '.csv"'

    writer = UnicodeWriter(response)

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

@login_required()
def settings_view(request):
    sqs = Movie.objects.values_list('imdb_id', flat=True)
    sqs = sqs.annotate(count_imdb=Count("imdb_id"))
    sqs = sqs.filter(count_imdb__gt=1)

    duplicate_imdb_ids = sqs.distinct()
    duplicate_movies = []

    for imdb_id in duplicate_imdb_ids:
        sqs = Movie.objects
        sqs = sqs.filter(imdb_id=imdb_id)
        sqs = sqs.annotate(mic_count=Count("movieincollection"))
        sqs = sqs.order_by("-mic_count")
        duplicate_movies.append(sqs.all())

    c = RequestContext(request)
    c.update({
            'movies_no_imdb_id': Movie.objects.filter(imdb_id=None),
            'movies_no_imdb_info': Movie.objects.exclude(imdb_id__in=[x.imdb_id for x in IMDBMovie.objects.all()]),
            'movies_no_tmdb_info': Movie.objects.exclude(imdb_id__in=[x.imdb_id for x in TMDBMovie.objects.all()]),
            'movies_duplicate_imdb': duplicate_movies,
            'collections': request.user.collection_set
        })
    return render_to_response("mlist/settings.html", c)


@login_required
def merge_movie_view(request, pk):
    to_movie = Movie.objects.get(pk=pk)
    other_movies = Movie.objects.filter(imdb_id=to_movie.imdb_id).exclude(pk=pk).all()

    for movie in other_movies:
        for mic in movie.movieincollection_set.all():
            mic.movie = to_movie
            mic.save()
        movie.delete()

    return redirect(reverse("settings"))


@login_required()
def statistics_view(request):
    c = RequestContext(request)
    return render_to_response("mlist/statistics.html", c)


@login_required()
def ajax_taglist_view(request):
    tags = []
    for tag in MovieInCollection.tags.all():
        tags.append({'tag': unicode(tag)})
    content = {'tags': tags}
    return HttpResponse(json.dumps(content), content_type="application/json")
