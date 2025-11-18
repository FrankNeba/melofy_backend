from django.db import models
from django.contrib.auth.models import AbstractUser

LANGUAGE_CHOICES = [
    ('english', 'English'),
    ('french', 'French'),
    ('both', 'Both'),
    ('English', 'English'),
    ('French', 'French'),
    ('Both', 'Both'),
]

EXPERIENCE_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('professional', 'Professional'),
]

PLATFORM_CHOICES = [
    ('youtube', 'YouTube'),
    ('tiktok', 'TikTok'),
    ('boomplay', 'Boomplay'),
    ('spotify', 'Spotify'),
    ('facebook', 'Facebook'),
    ('instagram', 'Instagram'),
    ('x', 'X'),
]


GOAL_CHOICES = [
    ('promote', 'Promoting Songs'),
    ('collaboration', 'Collaboration'),
    ('monetization', 'Monetization'),
    ('branding', 'Branding'),
]

class User(AbstractUser):
    is_artist = models.BooleanField(default=False)
    role = models.CharField(max_length=20, default='artist')  # artist, beatmaker, producer, etc.


class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    stage_name = models.CharField(max_length=255)
    primary_genre = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    languages_of_lyrics = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    current_platforms = models.JSONField(default=list)  # Example: ["YouTube", "TikTok", "Instagram"]
    social_media_handles = models.JSONField(default=dict, blank=True)  # Example: {"instagram": "@user"}
    goals_or_interests = models.JSONField(default=list)
