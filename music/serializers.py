

# ============================================================
# music/serializers.py
# ============================================================
from rest_framework import serializers
from .models import Song, AIFeedback, SocialContent, ReleasePlan, ArtistBranding, SongAnalytics


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
