from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ArtistProfile
from music.models import Song

User = get_user_model()

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = "__all__"

# -----------------------------
# Artist Profile Serializer
# -----------------------------
class ArtistProfileSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True, source='music_songs')
    class Meta:
        model = ArtistProfile
        fields = '__all__'
        read_only_fields = ('user',)


# -----------------------------
# User Serializer
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    artist_profile = ArtistProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_artist', 'role',
            'artist_profile'
        ]


# -----------------------------
# Registration Serializer
# -----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_artist = serializers.BooleanField(default=False)
    
    # Artist-specific fields
    stage_name = serializers.CharField(required=False)
    primary_genre = serializers.CharField(required=False)
    experience_level = serializers.ChoiceField(
        choices=[
            ('beginner','Beginner'),
            ('intermediate','Intermediate'),
            ('professional','Professional')
        ], 
        required=False
    )
    languages_of_lyrics = serializers.ChoiceField(
        choices=[
            ('english','English'),
            ('french','French'),
            ('both','Both')
        ],
        required=False
    )
    current_platforms = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'youtube','tiktok','boomplay','spotify','facebook','instagram','x'
        ]),
        required=False
    )
    social_media_handles = serializers.DictField(required=False)
    goals_or_interests = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'promote','collaboration','monetization','branding'
        ]),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'is_artist',
            'stage_name', 'primary_genre', 'experience_level',
            'languages_of_lyrics', 'current_platforms',
            'social_media_handles', 'goals_or_interests'
        ]

    def create(self, validated_data):
        is_artist = validated_data.pop('is_artist', False)
        password = validated_data.pop('password')
        user = User.objects.create(is_artist=is_artist, **validated_data)
        user.set_password(password)
        user.save()

        # If artist, create ArtistProfile
        if is_artist:
            ArtistProfile.objects.create(
                user=user,
                stage_name=validated_data.get('stage_name', ''),
                primary_genre=validated_data.get('primary_genre', ''),
                experience_level=validated_data.get('experience_level', 'beginner'),
                languages_of_lyrics=validated_data.get('languages_of_lyrics', 'english'),
                current_platforms=validated_data.get('current_platforms', []),
                social_media_handles=validated_data.get('social_media_handles', {}),
                goals_or_interests=validated_data.get('goals_or_interests', [])
            )
        return user


# -----------------------------
# Login Serializer (optional)
# -----------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
