from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.static import serve

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

from mlist import views

admin.autodiscover()

urlpatterns = [
    url(r'^list$', login_required(MovieList.as_view()), {'collection': 'watched'}, name="list-movies"),
    url(r'^list/(?P<collection>.*)/$', login_required(MovieList.as_view()), name="list-movies"),

    url(r'^add$',                 login_required(MovieCreate.as_view()), name="add-movie"),
    url(r'^update/(?P<pk>\d+)/$', permission_required('mlist.can_update_movie')(MovieUpdate.as_view()), name="update-movie"),
    url(r'^delete/(?P<pk>\d+)/$', login_required(MovieDelete.as_view()), name="delete-movie"),
    url(r'^import$',              login_required(MovieImport.as_view()), name='import-movies'),
    url(r'^movies/(?P<pk>\d+)/$', login_required(MovieDetail.as_view()), name="detail-movie"),

    url(r'^delete-collection/(?P<pk>\d+)/$', login_required(CollectionDelete.as_view()), name="delete-collection"),
    url(r'^create-collection$',              login_required(CollectionCreate.as_view()), name="create-collection"),
]

urlpatterns += [
    url(r'^$', views.login_view, name="login"),
    url(r'^auth', views.authenticate_view, name="authenticate"),
    url(r'^logout$', views.logout_view, name="logout"),
    url(r'^export$', views.export_view, name="export-movies"),
    url(r'^export2$', views.adv_export_view, name="adv-export-movies"),
    url(r'^settings$', views.settings_view, name="settings"),
    url(r'^statistics$', views.statistics_view, name="statistics"),

    url(r'^merge-movie/(?P<pk>\d+)/$', views.merge_movie_view, name="merge-movie"),

    url(r'^fetch-imdb/(?P<pk>\d+)/$', views.fetch_imdb_view, name="fetch-imdb"),
    url(r'^fetch-tmdb/(?P<pk>\d+)/$', views.fetch_tmdb_view, name="fetch-tmdb"),
    url(r'^ajax/tag-list$', views.ajax_taglist_view, name="ajax_taglist"),
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
    # Examples:
    # url(r'^$', 'mlist.views.home', name='home'),
    # url(r'^mlist/', include('mlist.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns