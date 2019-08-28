from django.contrib import admin
from .models import MovieInCollection, Collection, Movie, BackendMovie, BackendMovieAttribute, TMDBMovie, IMDBMovie


class CollectionAdmin(admin.ModelAdmin):
    list_display = ("user", "title")
    list_filter = ("user__username", "title")
    ordering = ("title",)
    search_fields = ("title",)


class MovieInCollectionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ("movie", "date", "collection")
    list_filter = ("date", "collection__user__username", "collection__title")
    ordering = ("-date",)
    search_fields = ("movie__title",)
    fieldsets = (
        (None, {
            'fields': ('movie', 'collection')
            }),
        ('Advanced', {
            'classes': ("collapse",),
            'fields': ('date', 'tags')
            })
    )


class MovieAdmin(admin.ModelAdmin):
    search_fields = ("title", "imdb_id")


admin.site.register(MovieInCollection, MovieInCollectionAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(TMDBMovie)
admin.site.register(IMDBMovie)


admin.site.register(BackendMovie)
admin.site.register(BackendMovieAttribute)
