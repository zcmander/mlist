# -*- coding:utf-8 -*-
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import admin
from django.views.static import serve
from django.urls import path

from haystack.views import search_view_factory

from mlist.views.movie_create import MovieCreate
from mlist.views.movie_import import MovieImport
from mlist.views.movie_list import MovieList
from mlist.views.movie_detail import MovieDetail
from mlist.views.movie_update import MovieUpdate
from mlist.views.movie_delete import MovieDelete
from mlist.views.movie_search import MovieSearch
from mlist.views.collection_create import CollectionCreate
from mlist.views.collection_delete import CollectionDelete
from mlist.views.auth import login_view, authenticate_view, logout_view
from mlist.views.movie_export import export_view, adv_export_view
from mlist.views.settings import settings_view, merge_movie_view
from mlist.views.statistics import statistics_view
from mlist.views.movie_utils import fetch_imdb_view, fetch_tmdb_view
from mlist.views.movie_create import ajax_taglist_view

from mlist.forms import MovieSearchForm

admin.autodiscover()

urlpatterns = [
    url(r'^list$', MovieList.as_view(), {'collection': 'watched'},
        name="list-movies"),
    url(r'^list/(?P<collection>.*)/$', MovieList.as_view(),
        name="list-movies"),

    url(r'^add$', MovieCreate.as_view(), name="add-movie"),
    url(r'^update/(?P<pk>\d+)/$', MovieUpdate.as_view(), name="update-movie"),
    url(r'^delete/(?P<pk>\d+)/$', MovieDelete.as_view(), name="delete-movie"),
    url(r'^import$', MovieImport.as_view(), name='import-movies'),
    url(r'^movies/(?P<pk>\d+)/$', MovieDetail.as_view(), name="detail-movie"),

    url(r'^delete-collection/(?P<pk>\d+)/$', CollectionDelete.as_view(),
        name="delete-collection"),
    url(r'^create-collection$', CollectionCreate.as_view(),
        name="create-collection"),
]

urlpatterns += [
    url(r'^$', login_view, name="login"),
    url(r'^auth', authenticate_view, name="authenticate"),
    url(r'^logout$', logout_view, name="logout"),
    url(r'^export$', export_view, name="export-movies"),
    url(r'^export2$', adv_export_view, name="adv-export-movies"),
    url(r'^settings$', settings_view, name="settings"),
    url(r'^statistics$', statistics_view, name="statistics"),

    url(r'^merge-movie/(?P<pk>\d+)/$', merge_movie_view, name="merge-movie"),

    url(r'^fetch-imdb/(?P<pk>\d+)/$', fetch_imdb_view, name="fetch-imdb"),
    url(r'^fetch-tmdb/(?P<pk>\d+)/$', fetch_tmdb_view, name="fetch-tmdb"),
    url(r'^ajax/tag-list$', ajax_taglist_view, name="ajax_taglist"),
]

# Haystack
urlpatterns += [
    url(r'^search/', login_required(search_view_factory(
        view_class=MovieSearch,
        form_class=MovieSearchForm,
        results_per_page=6 * 6,
    )), name='search'),
]

urlpatterns += [
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
