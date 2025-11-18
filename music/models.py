# ============================================================
# music/models.py - UPDATED WITH NEW MODELS
# ============================================================
from django.db import models
from django.conf import settings
from users.models import ArtistProfile

LANGUAGE_CHOICES = [
    ("english", "English"),
    ("french", "French"),
    ("both", "Both"),
]


class Song(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name="music_songs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="songs")
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to="songs/", null=True, blank=True)
    lyrics_text = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="english")

    # Extracted audio features
    tempo = models.FloatField(null=True, blank=True)
    key = models.CharField(max_length=10, null=True, blank=True)
    energy = models.FloatField(null=True, blank=True)

    transcription = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {getattr(self.user, 'username', 'unknown')}"
    
    def save(self, *args, **kwargs):
        self.artist = self.user.artist_profile
        super().save(*args, **kwargs)


class AIFeedback(models.Model):
    """Each row represents ONE message in the conversation."""
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="feedbacks")
    is_user_message = models.BooleanField(default=False)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        msg_type = "User" if self.is_user_message else "AI"
        return f"{msg_type} message for {self.song.title}"


# ============================================================
# NEW: Social Media Posts with AI-Generated Images
# ============================================================
class SocialPost(models.Model):
    """Individual social media post with AI-generated image"""
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="social_posts")
    caption = models.TextField()
    hashtags = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)  # AI-generated image
    image_file = models.ImageField(upload_to="social_posts/", blank=True, null=True)  # Local storage
    platform = models.CharField(max_length=50, default="instagram")  # instagram, tiktok, facebook, etc.
    prompt_used = models.TextField(blank=True)  # The prompt that generated this post
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post for {self.song.title} - {self.platform}"


# ============================================================
# NEW: Streaming Links Management
# ============================================================
class StreamingLink(models.Model):
    """Streaming platform links for a song"""
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="streaming_links")
    platform = models.CharField(max_length=50)  # spotify, apple_music, youtube_music, etc.
    url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['platform']
        unique_together = ['song', 'platform']

    def __str__(self):
        return f"{self.song.title} - {self.platform}"


# ============================================================
# LEGACY: Keep for backward compatibility
# ============================================================
class SocialContent(models.Model):
    song = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="social_content")
    captions = models.TextField(blank=True, null=True)
    hashtags = models.TextField(blank=True, null=True)
    flyer_text = models.TextField(blank=True, null=True)
    short_video_scripts = models.TextField(blank=True, null=True)
    streaming_links = models.TextField(blank=True, null=True)
    video_script = models.TextField(blank=True, null=True)
    streaming_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"SocialContent for {self.song.title}"


class ReleasePlan(models.Model):
    song = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="release_plan")
    schedule_days = models.JSONField(default=list)
    reminder_texts = models.JSONField(default=list)

    def __str__(self):
        return f"ReleasePlan for {self.song.title}"


class ArtistBranding(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="branding")
    stage_name_suggestions = models.TextField(blank=True, null=True)
    taglines = models.TextField(blank=True, null=True)
    visual_style = models.TextField(blank=True, null=True)
    content_tone = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Branding for {getattr(self.user, 'username', 'user')}"


class SongAnalytics(models.Model):
    song = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="analytics")
    virality_score = models.FloatField(default=0.0)
    predicted_engagement = models.JSONField(default=dict)
    ai_trends_insight = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Analytics for {self.song.title}"
