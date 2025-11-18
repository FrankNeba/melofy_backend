# AI Music Copilot+ API Guide

This document provides **all API endpoints** for the **AI Music Copilot+ backend**, along with usage examples and how to consume them from a frontend (React Native, Axios, or any HTTP client).

---

## **Authentication**

All protected endpoints require **JWT authentication**.

1. **Login**

   ```http
   POST /api/login/
   Content-Type: application/json
   ```

   **Request Body**

   ```json
   {
     "email": "artist@example.com",
     "password": "yourpassword"
   }
   ```

   **Response**

   ```json
   {
     "user_id": 1,
     "token": "your_jwt_token_here"
   }
   ```

2. **Include JWT in Headers**

   ```javascript
   axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
   ```

---

## **Endpoints**

### 1. User Registration

**POST** `/api/register/`

**Body**

```json
{
  "username": "artist1",
  "email": "artist@example.com",
  "password": "securepassword",
  "is_artist": true,
  "stage_name": "DJ Frank",
  "primary_genre": "HipHop",
  "experience_level": "intermediate",
  "languages_of_lyrics": "english",
  "current_platforms": ["youtube","tiktok","facebook","instagram","x"],
  "social_media_handles": {"instagram":"@djfrank"},
  "goals_or_interests": ["promote","collaboration"]
}
```

**Response**

```json
{
  "id": 1,
  "username": "artist1",
  "email": "artist@example.com",
  "is_artist": true,
  "role": "artist",
  "artist_profile": {
    "stage_name": "DJ Frank",
    "primary_genre": "HipHop"
  }
}
```

---

### 2. Upload Song

**POST** `/api/upload-song/`

**Form Data**

```javascript
const formData = new FormData();
formData.append('audio_file', {
  uri: fileUri,
  name: 'song.mp3',
  type: 'audio/mpeg'
});
formData.append('song_title', 'My New Track');
formData.append('lyrics_text', 'Optional lyrics here');
formData.append('language', 'english');
```

**Response**

```json
{
  "song_id": 1,
  "transcribed_lyrics": "...",
  "audio_features": {
    "tempo": 120,
    "key": "5",
    "energy": 0.45
  },
  "AI_feedback_summary": "Initial AI suggestion based on transcription..."
}
```

---

### 3. Interactive AI Feedback

**POST** `/api/song-feedback/<song_id>/`

**Body**

```json
{
  "artist_input": "Improve this chorus"
}
```

**Response**

```json
{
  "ai_response": "AI iterative feedback based on your input..."
}
```

---

### 4. Social Media Content

**GET** `/api/social-content/<song_id>/`

**Response**

```json
{
  "captions": "🔥 DJ Frank just released 'My New Track' — out now!",
  "hashtags": "#NewMusic #AI #MusicCopilot",
  "flyer_text": "🎵 'My New Track' by DJ Frank is out!",
  "short_video_scripts": "A 10-second hype script",
  "streaming_links": "https://example.com/stream"
}
```

---

### 5. Release Plan & Reminders

**GET** `/api/release-plan/<song_id>/`

**Response**

```json
{
  "schedule_days": [
    {"day": "2025-11-17", "task": "Promotional task 1"},
    {"day": "2025-11-18", "task": "Promotional task 2"}
  ],
  "reminder_texts": [
    "Reminder for promotional task 1",
    "Reminder for promotional task 2"
  ]
}
```

---

### 6. Branding Suggestions

**GET** `/api/branding/<artist_id>/`

**Response**

```json
{
  "stage_name_suggestions": "DJ Frank Official, DJ Frank Vibes",
  "taglines": "HipHop Artist | Modern & Creative",
  "visual_style": "Bold, Vibrant, Modern",
  "content_tone": "Energetic, Engaging, Authentic"
}
```

---

### 7. Artist Profile

**GET** `/api/profile/<user_id>/`
**PUT** `/api/profile/<user_id>/`

**PUT Body Example**

```json
{
  "language_preference": "english",
  "UI_mode_preference": "dark"
}
```

**Response**

```json
{
  "uploaded_songs": [...],
  "AI_feedback_history": [...],
  "branding_profile": {...},
  "language_preference": "english",
  "UI_mode_preference": "dark"
}
```

---

### 8. Artist Discovery

**GET** `/api/discover-artists/`

Optional query params: `?genre=HipHop&style=Trap`

**Response**

```json
[
  {
    "id": 2,
    "stage_name": "DJ Max",
    "primary_genre": "HipHop"
  }
]
```

---

### 9. Song Analytics

**GET** `/api/song-analytics/<song_id>/`

**Response**

```json
{
  "virality_score": 78.5,
  "predicted_engagement": {
    "likes": 1000,
    "shares": 150,
    "comments": 45
  },
  "AI_trends_insight": "Song 'My New Track' matches trending patterns in english"
}
```

---

## **Tips for Frontend Consumption**

* Always include **JWT token** in `Authorization` headers.
* Use **FormData** for file uploads.
* Check responses for `status` and handle errors gracefully.
* All AI responses are **dynamic**, generated via Whisper, Librosa, and Gemini AI.

---

This document serves as a **reference for mobile app developers** to consume all backend APIs effectively.
