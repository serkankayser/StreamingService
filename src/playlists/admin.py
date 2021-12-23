from django.contrib import admin
from .models import Playlist, PlaylistItem, TVShowProxy, TVShowSeasonProxy, MovieProxy
from tags.admin import TaggedItemInline


class MovieProxyAdmin(admin.ModelAdmin):
    list_display = ['title']
    fields = ['title', 'description', 'state', 'category', 'video', 'slug']

    class Meta:
        model = MovieProxy

    def get_queryset(self, request):
        return MovieProxy.objects.all()


admin.site.register(MovieProxy, MovieProxyAdmin)


class SeasonEpisodeInline(admin.TabularInline):
    model = PlaylistItem
    extra = 0


class TVShowSeasonProxyAdmin(admin.ModelAdmin):
    inlines = [SeasonEpisodeInline]
    list_display = ['title', 'parent']

    class Meta:
        model = TVShowSeasonProxy

    def get_queryset(self, request):
        return TVShowSeasonProxy.objects.all()


admin.site.register(TVShowSeasonProxy, TVShowSeasonProxyAdmin)


class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem


class PlaylistAdmin(admin.ModelAdmin):
    inlines = [PlaylistItemInline]

    class Meta:
        model = Playlist

    def get_queryset(self, request):
        return Playlist.objects.filter(type=Playlist.PlaylistTypeChoices.PLAYLIST)


admin.site.register(Playlist, PlaylistAdmin)


class TVShowSeasonProxyInline(admin.TabularInline):
    model = TVShowSeasonProxy
    extra = 0
    fields = ['order', 'title', 'state']


class TVShowProxyAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline, TVShowSeasonProxyInline]
    fields = ['title', 'description', 'state', 'category', 'video', 'slug']
    list_display = ['title']

    class Meta:
        model = TVShowProxy

    def get_queryset(self, request):
        return TVShowProxy.objects.all()


admin.site.register(TVShowProxy, TVShowProxyAdmin)
