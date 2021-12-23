from videos.models import Video
from playlists.models import Playlist


video_a = Video.objects.create(title='My title', video_id='abc')

playlist_a = Playlist.objects.create(
    title='This is my title', video=video_a
)
