
# ============================================================
# music/serializers.py - UPDATED
# ============================================================
from rest_framework import serializers
from .models import (
    Song, AIFeedback, SocialContent, SocialPost, StreamingLink,
    ReleasePlan, ArtistBranding, SongAnalytics
)
from users.models import User, ArtistProfile


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = "__all__"
        read_only_fields = ("tempo", "key", "energy", "transcription", "uploaded_at", 'artist')


class AIFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFeedback
        fields = ['id', 'song', 'is_user_message', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


# NEW: Social Post Serializer
class SocialPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPost
        fields = ['id', 'song', 'caption', 'hashtags', 'image_url', 'image_file', 
                  'platform', 'prompt_used', 'created_at']
        read_only_fields = ['id', 'created_at', 'image_url', 'image_file']


# NEW: Streaming Link Serializer
class StreamingLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingLink
        fields = ['id', 'song', 'platform', 'url', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class SocialContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialContent
        fields = "__all__"
        read_only_fields = ("video_script", "streaming_text")


class ReleasePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleasePlan
        fields = "__all__"


class ArtistBrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistBranding
        fields = "__all__"


class SongAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongAnalytics
        fields = "__all__"


# NEW: Artist Discovery Serializer
class ArtistProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = ArtistProfile
        fields = ['id', 'user_id', 'username', 'stage_name', 'primary_genre', 
                  'experience_level', 'languages_of_lyrics', 'current_platforms', 
                  'social_media_handles', 'goals_or_interests']

