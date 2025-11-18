
# ============================================================
# music/urls.py - UPDATED ROUTES
# ============================================================
from django.urls import path
from .views import (
    UploadSongView, SongFeedbackView,
    SocialPostListView, SocialPostDetailView,
    StreamingLinkListView, StreamingLinkDetailView,
    ArtistDiscoveryView,
    SocialContentView, ReleasePlanView, ArtistBrandingView, SongAnalyticsView
)

urlpatterns = [
    # Song upload
    path('upload-song/', UploadSongView.as_view(), name='upload-song'),
    
    # AI Feedback
    path('song-feedback/<int:song_id>/', SongFeedbackView.as_view(), name='song-feedback'),
    
    # NEW: Social Posts with Images
    path('social-posts/<int:song_id>/', SocialPostListView.as_view(), name='social-posts-list'),
    path('social-posts/detail/<int:pk>/', SocialPostDetailView.as_view(), name='social-post-detail'),
    
    # NEW: Streaming Links
    path('streaming-links/<int:song_id>/', StreamingLinkListView.as_view(), name='streaming-links-list'),
    path('streaming-links/detail/<int:pk>/', StreamingLinkDetailView.as_view(), name='streaming-link-detail'),
    
    # NEW: Artist Discovery
    path('discover-artists/', ArtistDiscoveryView.as_view(), name='discover-artists'),
    
    # Legacy endpoints
    path('social-content/<int:song_id>/', SocialContentView.as_view(), name='social-content'),
    path('release-plan/<int:song_id>/', ReleasePlanView.as_view(), name='release-plan'),
    path('branding/<int:artist_id>/', ArtistBrandingView.as_view(), name='branding'),
    path('song-analytics/<int:song_id>/', SongAnalyticsView.as_view(), name='song-analytics'),
]