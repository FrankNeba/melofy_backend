
# ============================================================
# music/views.py
# ============================================================
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Song, AIFeedback, SocialContent, ReleasePlan, ArtistBranding, SongAnalytics
from .serializers import (
    SongSerializer, AIFeedbackSerializer, SocialContentSerializer,
    ReleasePlanSerializer, ArtistBrandingSerializer, SongAnalyticsSerializer
)
from .utils import (
    transcribe_audio,
    extract_audio_features,
    generate_ai_feedback_with_history,  # NEW: History-aware function
    generate_social_content,
    generate_song_release_plan,
    generate_artist_branding,
    generate_song_analytics
)


# ---------------- Upload Song + Initial AI ----------------
class UploadSongView(generics.CreateAPIView):
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print(self.request.data)
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

        # ---------------- Initial AI Feedback (First Message) ----------------
        initial_feedback = generate_ai_feedback_with_history(
            user=user,
            song=song,
            artist_input=None,  # No user message yet
            conversation_history=[]  # Empty history
        )
        
        # Save initial AI message
        AIFeedback.objects.create(
            song=song,
            is_user_message=False,  # AI message
            message=initial_feedback
        )

        # ---------------- Social Content ----------------
        social_data = generate_social_content(user, song.title, song.transcription)
        SocialContent.objects.create(song=song, **social_data)

        # ---------------- Release Plan ----------------
        schedule, reminders = generate_song_release_plan(song=song, user=user)
        ReleasePlan.objects.create(song=song, schedule_days=schedule, reminder_texts=reminders)

        # ---------------- Branding ----------------
        branding_data = generate_artist_branding(user)
        ArtistBranding.objects.update_or_create(user=user, defaults=branding_data)

        # ---------------- Analytics ----------------
        analytics_data = generate_song_analytics(user, song)
        SongAnalytics.objects.update_or_create(song=song, defaults=analytics_data)


        return song


# ---------------- Interactive AI Feedback (Chat with History) ----------------
class SongFeedbackView(generics.GenericAPIView):
    serializer_class = AIFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, song_id):
        """
        GET: Retrieve entire chat history for this song
        Returns all messages (user + AI) in chronological order
        """
        song = get_object_or_404(Song, id=song_id)

        # Only allow song owner to view feedback
        if song.user != request.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        # Get all messages in order
        feedbacks = song.feedbacks.all().order_by('created_at')
        serializer = self.get_serializer(feedbacks, many=True)
        
        return Response({
            "conversation": serializer.data,
            "song_title": song.title,
            "song_id": song.id
        }, status=status.HTTP_200_OK)

    def post(self, request, song_id):
        """
        POST: Send new message and get AI response
        Creates 2 new records: user message + AI response
        """
        song = get_object_or_404(Song, id=song_id)

        # Only allow song owner to request AI feedback
        if song.user != request.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        artist_input = request.data.get('artist_input', '').strip()
        
        if not artist_input:
            return Response(
                {"error": "artist_input is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get conversation history (last 10 messages to keep context manageable)
        conversation_history = song.feedbacks.all().order_by('created_at')[:10]
        
        # Format history for AI context
        history_context = []
        for msg in conversation_history:
            history_context.append({
                'is_user': msg.is_user_message,
                'message': msg.message
            })

        # Generate AI response with full context
        ai_response = generate_ai_feedback_with_history(
            user=request.user,
            song=song,
            artist_input=artist_input,
            conversation_history=history_context
        )

        # Save user message
        user_message = AIFeedback.objects.create(
            song=song,
            is_user_message=True,
            message=artist_input
        )

        # Save AI response
        ai_message = AIFeedback.objects.create(
            song=song,
            is_user_message=False,
            message=ai_response
        )

        # Return both messages
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


# ---------------- Social Content ----------------
class SocialContentView(generics.RetrieveAPIView):
    serializer_class = SocialContentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        song_id = self.kwargs['song_id']
        return get_object_or_404(SocialContent, song_id=song_id)


# ---------------- Release Plan ----------------
class ReleasePlanView(generics.RetrieveAPIView):
    serializer_class = ReleasePlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        song_id = self.kwargs['song_id']
        return get_object_or_404(ReleasePlan, song_id=song_id)


# ---------------- Branding ----------------
class ArtistBrandingView(generics.RetrieveAPIView):
    serializer_class = ArtistBrandingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['artist_id']
        return get_object_or_404(ArtistBranding, user_id=user_id)


# ---------------- Song Analytics ----------------
class SongAnalyticsView(generics.RetrieveAPIView):
    serializer_class = SongAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        song_id = self.kwargs['song_id']
        return get_object_or_404(SongAnalytics, song_id=song_id)

