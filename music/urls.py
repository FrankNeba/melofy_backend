from django.urls import path
from .views import (
    UploadSongView, SongFeedbackView, SocialContentView,
    ReleasePlanView, ArtistBrandingView, SongAnalyticsView
)

urlpatterns = [
    path('upload-song/', UploadSongView.as_view(), name='upload_song'),
    path('song-feedback/<int:song_id>/', SongFeedbackView.as_view(), name='song_feedback'),
    path('social-content/<int:song_id>/', SocialContentView.as_view(), name='social_content'),
    path('release-plan/<int:song_id>/', ReleasePlanView.as_view(), name='release_plan'),
    path('branding/<int:artist_id>/', ArtistBrandingView.as_view(), name='artist_branding'),
    path('song-analytics/<int:song_id>/', SongAnalyticsView.as_view(), name='song_analytics'),
]
