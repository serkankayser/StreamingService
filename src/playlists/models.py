from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from streaming_service.db.models import PublishStateOptions
from streaming_service.db.receivers import publish_state_pre_save, slugify_pre_save
from videos.models import Video


class PlaylistQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            state=PublishStateOptions.PUBLISH,
            publish_timestamp__lte=now
        )


class PlaylistManager(models.Manager):
    def get_queryset(self):
        return PlaylistQuerySet(self.model, using=self._db)

    def publised(self):
        self.get_queryset().published()


class Playlist(models.Model):
    class PlaylistTypeChoices(models.TextChoices):
        MOVIE = "MOV", "Movie"
        SHOW = "TVS", "TV Show"
        SEASON = "SEA", "Season"
        PLAYLIST = "PLY", "Playlist"

    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)
    order = models.IntegerField(default=1)
    title = models.CharField(max_length=220)
    type = models.CharField(
        max_length=3,
        choices=PlaylistTypeChoices.choices,
        default=PlaylistTypeChoices.PLAYLIST
    )
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video = models.ForeignKey(
        Video,
        related_name='playlist_futured',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    videos = models.ManyToManyField(
        Video,
        blank=True,
        related_name='playlist_item',
        through='PlaylistItem'
    )
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(
        max_length=2,
        choices=PublishStateOptions.choices,
        default=PublishStateOptions.DRAFT
    )
    publish_timestamp = models.DateTimeField(
        auto_now_add=False,
        auto_now=False,
        blank=True,
        null=True
    )

    objects = PlaylistManager()

    def timestamp(self):
        return None

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.active


pre_save.connect(publish_state_pre_save, sender=Playlist)
pre_save.connect(slugify_pre_save, sender=Playlist)


class TVShowProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=True, type=Playlist.PlaylistTypeChoices.SHOW)


class TVShowProxy(Playlist):
    objects = TVShowProxyManager()

    class Meta:
        verbose_name = 'TV Show'
        verbose_name_plural = 'TV Shows'
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SHOW
        super().save(*args, **kwargs)


class TVShowSeasonProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=False, type=Playlist.PlaylistTypeChoices.SEASON)


class TVShowSeasonProxy(Playlist):
    objects = TVShowSeasonProxyManager()

    class Meta:
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SEASON
        super().save(*args, **kwargs)


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-timestamp']


class MovieProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=True, type=Playlist.PlaylistTypeChoices.MOVIE)


class MovieProxy(Playlist):
    objects = MovieProxyManager()

    class Meta:
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.MOVIE
        super().save(*args, **kwargs)
