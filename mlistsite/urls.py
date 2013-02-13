from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required, permission_required

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from mlist.views import (
    MovieCreate,
    MovieImport,
    MovieList,
    MovieDetail,
    MovieUpdate,
    MovieDelete,
    MovieSearch
)
from mlist.views import (
    CollectionDelete,
    CollectionCreate
)
from mlist.forms import MovieSearchForm
from haystack.views import search_view_factory

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^list$', login_required(MovieList.as_view()), {'collection': 'watched'}, name="list-movies"),
    url(r'^list/(?P<collection>.*)/$', login_required(MovieList.as_view()), name="list-movies"),

    url(r'^add$',                 login_required(MovieCreate.as_view()), name="add-movie"),
    url(r'^update/(?P<pk>\d+)/$', permission_required('mlist.can_update_movie')(MovieUpdate.as_view()), name="update-movie"),
    url(r'^delete/(?P<pk>\d+)/$', login_required(MovieDelete.as_view()), name="delete-movie"),
    url(r'^import$',              login_required(MovieImport.as_view()), name='import-movies'),
    url(r'^movies/(?P<pk>\d+)/$', login_required(MovieDetail.as_view()), name="detail-movie"),

    url(r'^delete-collection/(?P<pk>\d+)/$', login_required(CollectionDelete.as_view()), name="delete-collection"),
    url(r'^create-collection$',              login_required(CollectionCreate.as_view()), name="create-collection"),
)

urlpatterns += patterns('mlist.views',
    url(r'^$', 'login_view', name="login"),
    url(r'^auth', 'authenticate_view', name="authenticate"),
    url(r'^logout$', 'logout_view', name="logout"),
    url(r'^export$', 'export_view', name="export-movies"),
    url(r'^export2$', 'adv_export_view', name="adv-export-movies"),
    url(r'^settings$', 'settings_view', name="settings"),
    url(r'^statistics$', 'statistics_view', name="statistics"),

    url(r'^merge-movie/(?P<pk>\d+)/$', 'merge_movie_view', name="merge-movie"),

    url(r'^fetch-imdb/(?P<pk>\d+)/$', 'fetch_imdb_view', name="fetch-imdb"),
    url(r'^fetch-tmdb/(?P<pk>\d+)/$', 'fetch_tmdb_view', name="fetch-tmdb"),
    url(r'^ajax/tag-list$', 'ajax_taglist_view', name="ajax_taglist"),
)

# Haystack
urlpatterns += patterns('',
    url(r'^search/', login_required(search_view_factory(
        view_class=MovieSearch,
        form_class=MovieSearchForm,
        results_per_page=6 * 6,
    )), name='search'),
)

# django-js-utils
urlpatterns += patterns('',
    (r'^jsurls.js$', 'django_js_utils.views.jsurls', {}, 'jsurls'),
)

urlpatterns += patterns('',

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    # Examples:
    # url(r'^$', 'mlist.views.home', name='home'),
    # url(r'^mlist/', include('mlist.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
