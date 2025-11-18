
# ============================================================
# music/views.py - UPDATED WITH NEW ENDPOINTS
# ============================================================
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Song, AIFeedback, SocialPost, StreamingLink, SocialContent, ReleasePlan, ArtistBranding, SongAnalytics
from users.models import ArtistProfile
from .serializers import (
    SongSerializer, AIFeedbackSerializer, SocialPostSerializer, StreamingLinkSerializer,
    SocialContentSerializer, ReleasePlanSerializer, ArtistBrandingSerializer, 
    SongAnalyticsSerializer, ArtistProfileSerializer
)
from .utils import (
    transcribe_audio, extract_audio_features, generate_ai_feedback_with_history,
    generate_social_content, generate_song_release_plan, generate_artist_branding,
    generate_song_analytics, generate_social_post_with_image
)


# ---------------- Upload Song + Initial AI ----------------
class UploadSongView(generics.CreateAPIView):
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        song = serializer.save(user=user)

        # Audio processing
        if song.audio_file:
            song.transcription = transcribe_audio(song.audio_file.path)
            features = extract_audio_features(song.audio_file.path)
            song.tempo = features.get('tempo')
            song.key = features.get('key')
            song.energy = features.get('energy')
        else:
            song.transcription = song.lyrics_text or ""
        song.save()

        # Initial AI Feedback
        initial_feedback = generate_ai_feedback_with_history(
            user=user, song=song, artist_input=None, conversation_history=[]
        )
        AIFeedback.objects.create(song=song, is_user_message=False, message=initial_feedback)

        # Social Content (Legacy)
        social_data = generate_social_content(user, song.title, song.transcription)
        SocialContent.objects.create(song=song, **social_data)

        # Release Plan
        schedule, reminders = generate_song_release_plan(song=song, user=user)
        ReleasePlan.objects.create(song=song, schedule_days=schedule, reminder_texts=reminders)

        # Branding
        branding_data = generate_artist_branding(user)
        ArtistBranding.objects.update_or_create(user=user, defaults=branding_data)

        # Analytics
        analytics_data = generate_song_analytics(user, song)
        SongAnalytics.objects.update_or_create(song=song, defaults=analytics_data)

        return song


# ---------------- Interactive AI Feedback ----------------
class SongFeedbackView(generics.GenericAPIView):
    serializer_class = AIFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        if song.user != request.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        feedbacks = song.feedbacks.all().order_by('created_at')
        serializer = self.get_serializer(feedbacks, many=True)
        
        return Response({
            "conversation": serializer.data,
            "song_title": song.title,
            "song_id": song.id
        }, status=status.HTTP_200_OK)

    def post(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        if song.user != request.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        artist_input = request.data.get('artist_input', '').strip()
        if not artist_input:
            return Response({"error": "artist_input is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get conversation history
        conversation_history = song.feedbacks.all().order_by('created_at')[:10]
        history_context = [{'is_user': msg.is_user_message, 'message': msg.message} for msg in conversation_history]

        # Generate AI response
        ai_response = generate_ai_feedback_with_history(
            user=request.user, song=song, artist_input=artist_input, conversation_history=history_context
        )

        # Save messages
        user_message = AIFeedback.objects.create(song=song, is_user_message=True, message=artist_input)
        ai_message = AIFeedback.objects.create(song=song, is_user_message=False, message=ai_response)

        return Response({
            "user_message": {
                "id": user_message.id,
                "is_user_message": True,
                "message": user_message.message,
                "created_at": user_message.created_at
            },
            "ai_response": {
                "id": ai_message.id,
                "is_user_message": False,
                "message": ai_message.message,
                "created_at": ai_message.created_at
            }
        }, status=status.HTTP_201_CREATED)


# ============================================================
# NEW: Social Posts with AI-Generated Images
# ============================================================
class SocialPostListView(generics.ListCreateAPIView):
    """
    GET: List all social posts for a song
    POST: Generate new social post with AI image
    """
    serializer_class = SocialPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        song_id = self.kwargs['song_id']
        return SocialPost.objects.filter(song_id=song_id).order_by('-created_at')

    def post(self, request, song_id):
        """
        Generate social post with AI-generated image
        Body: {
            "prompt": "Create an energetic hip-hop promotional post",
            "platform": "instagram"  // optional, defaults to "instagram"
        }
        """
        song = get_object_or_404(Song, id=song_id)
        
        if song.user != request.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        custom_prompt = request.data.get('prompt', '')
        platform = request.data.get('platform', 'instagram')

        # Generate post with image
        post_data = generate_social_post_with_image(
            user=request.user,
            song=song,
            custom_prompt=custom_prompt,
            platform=platform
        )

        # Create post record
        social_post = SocialPost.objects.create(
            song=song,
            caption=post_data['caption'],
            hashtags=post_data['hashtags'],
            image_url=post_data.get('image_url'),
            platform=platform,
            prompt_used=custom_prompt or post_data.get('default_prompt', '')
        )

        serializer = self.get_serializer(social_post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SocialPostDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: Retrieve single post
    DELETE: Delete post
    """
    serializer_class = SocialPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SocialPost.objects.all()

    def get_object(self):
        post = super().get_object()
        if post.song.user != self.request.user:
            self.permission_denied(self.request)
        return post


# ============================================================
# NEW: Streaming Links Management
# ============================================================
class StreamingLinkListView(generics.ListCreateAPIView):
    """
    GET: List all streaming links for a song
    POST: Add new streaming link
    """
    serializer_class = StreamingLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        song_id = self.kwargs['song_id']
        return StreamingLink.objects.filter(song_id=song_id, is_active=True)

    def post(self, request, song_id):
        """
        Add streaming link
        Body: {
            "platform": "spotify",  // spotify, apple_music, youtube_music, tidal, deezer, etc.
            "url": "https://open.spotify.com/track/..."
        }
        """
        song = get_object_or_404(Song, id=song_id)
        
        if song.user != request.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        platform = request.data.get('platform', '').lower()
        url = request.data.get('url', '')

        if not platform or not url:
            return Response(
                {"error": "Both 'platform' and 'url' are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or update link
        link, created = StreamingLink.objects.update_or_create(
            song=song,
            platform=platform,
            defaults={'url': url, 'is_active': True}
        )

        serializer = self.get_serializer(link)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class StreamingLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve link
    PUT/PATCH: Update link
    DELETE: Delete link (soft delete - sets is_active=False)
    """
    serializer_class = StreamingLinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = StreamingLink.objects.all()

    def get_object(self):
        link = super().get_object()
        if link.song.user != self.request.user:
            self.permission_denied(self.request)
        return link

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


# ============================================================
# NEW: Artist Discovery
# ============================================================
class ArtistDiscoveryView(generics.ListAPIView):
    """
    Discover artists by genre, experience, language, platforms
    Query params:
        - genre: Filter by primary_genre
        - experience: Filter by experience_level
        - language: Filter by languages_of_lyrics
        - platform: Filter by current_platforms (contains)
        - search: Search in stage_name or username
    """
    serializer_class = ArtistProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ArtistProfile.objects.all().select_related('user')
        
        # Exclude current user
        queryset = queryset.exclude(user=self.request.user)

        # Filters
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(primary_genre__iexact=genre)

        experience = self.request.query_params.get('experience')
        if experience:
            queryset = queryset.filter(experience_level=experience)

        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(languages_of_lyrics=language)

        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(current_platforms__contains=[platform])

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(stage_name__icontains=search) | 
                Q(user__username__icontains=search)
            )

        return queryset[:50]  # Limit to 50 results


# Legacy endpoints (keep for backward compatibility)
class SocialContentView(generics.RetrieveAPIView):
    serializer_class = SocialContentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        song_id = self.kwargs['song_id']
        return get_object_or_404(SocialContent, song_id=song_id)


class ReleasePlanView(generics.RetrieveAPIView):
    serializer_class = ReleasePlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        song_id = self.kwargs['song_id']
        return get_object_or_404(ReleasePlan, song_id=song_id)


class ArtistBrandingView(generics.RetrieveAPIView):
    serializer_class = ArtistBrandingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['artist_id']
        return get_object_or_404(ArtistBranding, user_id=user_id)


class SongAnalyticsView(generics.RetrieveAPIView):
    serializer_class = SongAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        song_id = self.kwargs['song_id']
        return get_object_or_404(SongAnalytics, song_id=song_id)
