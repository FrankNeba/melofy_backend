
# ============================================================
# music/utils.py - UPDATED WITH CHAT HISTORY SUPPORT
# ============================================================
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional

import librosa
import soundfile as sf
import whisper
import google.generativeai as genai

genai.configure(api_key=os.getenv("GENAI_API_KEY"))

try:
    whisper_model = whisper.load_model("base")
except Exception as e:
    print("Warning: could not load whisper model:", e)
    whisper_model = None


def _call_gemini(prompt: str, model_name: str = "models/gemini-2.5-flash-lite") -> str:
    """Call Gemini safely, return text (fallback string on error)."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.85,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            ),
        )
        text = getattr(response, "text", None)
        if text:
            return text.strip()
        candidates = getattr(response, "candidates", None)
        if candidates and len(candidates) > 0:
            candidate = candidates[0]
            content = candidate.get("content") if isinstance(candidate, dict) else getattr(candidate, "content", None)
            if content:
                if isinstance(content, dict):
                    return content.get("text", str(content)).strip()
                return str(content).strip()
        return "AI returned no content. Keep going — your sound is unique!"
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "This is fire. Keep going — your sound is unique and powerful!"


def preprocess_audio(file_path: str) -> Optional[str]:
    """Ensure audio is resampled to 16k WAV for Whisper."""
    try:
        y, sr = librosa.load(file_path, sr=16000)
        base, _ = os.path.splitext(file_path)
        temp_path = f"{base}_16k.wav"
        sf.write(temp_path, y, 16000)
        return temp_path
    except Exception as e:
        print("Preprocessing error:", e)
        return None


def transcribe_audio(file_path: str) -> str:
    """Transcribe audio with Whisper."""
    processed = preprocess_audio(file_path)
    if not processed:
        return "[No audio detected]"

    if whisper_model is None:
        return "[Transcription model not available]"

    try:
        result = whisper_model.transcribe(processed)
        text = result.get("text", "").strip() if isinstance(result, dict) else str(result).strip()
        return text if text else "[Instrumental / No lyrics detected]"
    except Exception as e:
        print("Whisper error:", e)
        return "[Transcription failed]"
    finally:
        if processed and os.path.exists(processed):
            try:
                os.remove(processed)
            except Exception:
                pass


def extract_audio_features(file_path: str) -> Dict[str, Any]:
    """Extract tempo, key, energy from audio."""
    try:
        y, sr = librosa.load(file_path)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        key_idx = int(chroma.mean(axis=1).argmax())
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key = keys[key_idx] if 0 <= key_idx < len(keys) else "Unknown"
        energy = float(librosa.feature.rms(y=y).mean())
        return {"tempo": round(float(tempo), 1), "key": key, "energy": round(energy, 4)}
    except Exception as e:
        print("Feature extraction error:", e)
        return {"tempo": None, "key": "Unknown", "energy": None}


# ============================================================
# NEW: AI Feedback with Conversation History
# ============================================================
def generate_ai_feedback_with_history(
    user,
    song,
    artist_input: Optional[str] = None,
    conversation_history: List[Dict[str, Any]] = None
) -> str:
    """
    Generate AI feedback considering the full conversation history.
    
    Args:
        user: The authenticated user
        song: The Song object
        artist_input: Current user message (None for initial feedback)
        conversation_history: List of previous messages [{'is_user': bool, 'message': str}]
    
    Returns:
        AI response string
    """
    profile = getattr(user, "artist_profile", None)
    stage_name = profile.stage_name if profile and getattr(profile, "stage_name", None) else getattr(user, "username", "Unknown")
    genre = profile.primary_genre if profile and getattr(profile, "primary_genre", None) else "Hip-hop/Rap"
    language = getattr(song, "language", "english")
    language_name = "English" if language == "english" else "French" if language == "french" else "English and French"

    # Build conversation context
    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\nPrevious Conversation:\n"
        for msg in conversation_history:
            role = "Artist" if msg['is_user'] else "AI Assistant"
            conversation_context += f"{role}: {msg['message']}\n"

    # Initial feedback (no user input yet)
    if artist_input is None:
        prompt = (
            f"You are a friendly and experienced music producer in Cameroon giving clear, easy-to-understand advice.\n\n"
            f"Artist: {stage_name}\n"
            f"Genre: {genre}\n"
            f"Song Title: {song.title}\n"
            f"Lyrics/Transcription:\n\"\"\"\n{song.transcription}\n\"\"\"\n\n"
            f"Audio Features:\n"
            f"- Tempo: {song.tempo or 'Unknown'} BPM\n"
            f"- Key: {song.key or 'Unknown'}\n"
            f"- Energy: {song.energy or 'Unknown'}\n\n"
            f"The artist is a complete beginner and knows very little about music, so explain everything simply.\n\n"
            f"Give practical feedback on:\n"
            f"- How the song flows and feels when sung or rapped\n"
            f"- How strong and catchy the hook (main part) is\n"
            f"- How clear and interesting the lyrics/story are\n"
            f"- The energy and mood of the song\n"
            f"- One simple thing they can do immediately to improve\n\n"
            f"Be kind, encouraging, and very clear. Use simple language and short paragraphs. Max 4 short paragraphs.\n"
            f"Your goal is to help them improve and feel motivated!\n"
            f"Respond in The language of the comment."
        )
    else:
        # Continuing conversation with context
        prompt = (
            f"You are Melofy, a friendly and experienced music producer assistant in Cameroon having an ongoing conversation with an artist. Don't give any information about your history in google. mention nothing like you were built by google\n\n"
            f"Artist: {stage_name}\n"
            f"Genre: {genre}\n"
            f"Song Title: {song.title}\n"
            f"Lyrics:\n\"\"\"\n{song.transcription}\n\"\"\"\n\n"
            f"Audio Features: Tempo {song.tempo or 'Unknown'} BPM, Key {song.key or 'Unknown'}, Energy {song.energy or 'Unknown'}\n"
            f"{conversation_context}\n\n"
            f"Artist's new question/request: {artist_input}\n\n"
            f"Respond to their specific question while considering the previous conversation context. "
            f"Keep your response focused, practical, and encouraging. "
            f"If they're asking for specific help (like hashtags, improvements, or advice), give them exactly what they asked for. "
            f"Use simple language and keep it concise (2-3 paragraphs max).\n\n"
            f"Respond in THE language of the propmt.\n\n"
            f"Go straight to the point and give responses as soon as possible with thefew information you have and responses before asking for more information for more accuracy"
        )

    return _call_gemini(prompt)


# ============================================================
# Other utility functions remain the same
# ============================================================
def generate_song_analytics(user, song) -> Dict[str, Any]:
    prompt = (
        f"Artist: {getattr(user, 'username', 'unknown')}\n"
        f"Song: {getattr(song, 'title', 'unknown')}\n"
        f"Language: {getattr(song, 'language', 'english')}\n"
        f"Transcription:\n\"\"\"\n{getattr(song, 'transcription', '')}\n\"\"\"\n\n"
        f"Analyze like a major label A&R:\n"
        f"- Virality score (0–100)\n"
        f"- Predicted first-week streams\n"
        f"- Target audience vibe\n"
        f"- One current trend this fits perfectly\n"
        f"Be bold and specific. Speak like an African. Return back the lyrics then comment on it."
    )
    try:
        text = _call_gemini(prompt)
    except Exception:
        text = "This has serious hit potential. The energy is undeniable."

    return {
        "virality_score": 90.0,
        "predicted_engagement": {"first_week_streams": "10K-50K", "monthly_listeners_est": "50K-200K"},
        "ai_trends_insight": text,
    }


def generate_social_content(user, song_title: str, transcription: str) -> Dict[str, Any]:
    profile = getattr(user, "artist_profile", None)
    stage_name = profile.stage_name if profile and getattr(profile, "stage_name", None) else getattr(user, "username", "Unknown")

    prompt = (
        f"Artist {stage_name} just dropped: '{song_title}'\n\n"
        f"Lyrics snippet:\n{transcription[:280]}{'...' if len(transcription) > 280 else ''}\n\n"
        f"Generate viral social content:\n"
        f"- 3 caption options (TikTok/IG style)\n"
        f"- 8 trending hashtags\n"
        f"- One 15-second video script idea\n"
        f"- Streaming call-to-action"
    )
    text = _call_gemini(prompt)

    return {
        "captions": text,
        "hashtags": "#NewMusic #UnsignedArtist #HipHop #Rap #Afrobeats #Viral #Music2025 #Fire",
        "flyer_text": f"Listen to '{song_title}' by {stage_name} — out now!",
        "short_video_scripts": "POV: You just heard the song that's about to take over your playlist",
        "streaming_links": f"Stream '{song_title}' by {stage_name} everywhere NOW!",
        "video_script": "POV: You just heard the song that's about to take over your playlist",
        "streaming_text": f"Stream '{song_title}' by {stage_name} everywhere NOW!",
    }


def generate_artist_branding(user) -> Dict[str, Any]:
    profile = getattr(user, "artist_profile", None)
    name = profile.stage_name if profile and getattr(profile, "stage_name", None) else getattr(user, "username", "Unknown")
    genre = profile.primary_genre if profile and getattr(profile, "primary_genre", None) else "Hip-hop/Rap"

    prompt = (
        f"Artist: {name}\n"
        f"Genre: {genre}\n\n"
        f"Create a full artist brand package:\n"
        f"- 5 stage name alternatives\n"
        f"- 3 iconic taglines\n"
        f"- Visual aesthetic (colors, style, mood board)\n"
        f"- Social media voice\n"
    )
    try:
        text = _call_gemini(prompt)
    except Exception:
        text = "Your authenticity is your brand. Own your story — the world is watching."

    return {
        "stage_name_suggestions": text,
        "taglines": text,
        "visual_style": text,
        "content_tone": text,
    }


def generate_song_release_plan(user, song, days: int = 7) -> Tuple[List[Dict[str, str]], List[str]]:
    profile = getattr(user, "artist_profile", None)
    stage_name = profile.stage_name if profile and getattr(profile, "stage_name", None) else getattr(user, "username", "Unknown")
    song_title = getattr(song, "title", "Unknown Song")
    genre = getattr(song, "genre", "Hip-hop/Rap")
    transcription = getattr(song, "transcription", "")
    
    base_prompt = (
        f"You are a music release strategist. Create a detailed {days}-day release plan for this new song.\n\n"
        f"Artist: {stage_name}\n"
        f"Genre: {genre}\n"
        f"Song: {song_title}\n"
        f"Lyrics/Transcription:\n\"\"\"\n{transcription}\n\"\"\"\n\n"
        f"The plan should include:\n"
        f"- Daily tasks to promote the song (social media posts, influencer outreach, teaser clips, live events, etc.)\n"
        f"- Short, actionable reminders for the artist\n"
        f"- Tips for engagement and maximizing streams\n"
        f"Make it beginner-friendly and clear. Return in a format that can be parsed into schedule and reminders."
    )

    ai_response = _call_gemini(base_prompt)

    schedule = []
    reminders = []
    lines = ai_response.splitlines()
    day_count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("day") and ":" in line:
            day_count += 1
            if day_count > days:
                break
            day_name = (datetime.today() + timedelta(days=day_count-1)).strftime("%A, %b %d")
            task = line.split(":", 1)[1].strip()
            schedule.append({"day": day_name, "task": task})
            reminders.append(f"Reminder for {day_name}: {task}")
        else:
            reminders.append(line)

    if not schedule:
        return generate_release_plan(days)

    return schedule, reminders


def generate_release_plan(days: int = 7) -> Tuple[List[Dict[str, str]], List[str]]:
    today = datetime.today()
    tasks = [
        "Drop teaser on TikTok/Reels",
        "Post lyrics video",
        "Go live and talk about the song",
        "Behind-the-scenes content",
        "Send to 5 influencers",
        "Pitch to Spotify playlists",
        "OFFICIAL RELEASE — GO VIRAL!",
    ]
    schedule = []
    reminders = []
    for i in range(days):
        task = tasks[i] if i < len(tasks) else "Engage with fans & promote"
        day_name = (today + timedelta(days=i)).strftime("%A, %b %d")
        schedule.append({"day": day_name, "task": task})
        reminders.append(f"Reminder for {day_name}: {task}")
    return schedule, reminders


# music/utils.py - ADD THESE NEW FUNCTIONS

import os
import requests
from typing import Dict, Any
import google.generativeai as genai

genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# ============================================================
# AI Image Generation for Social Posts
# ============================================================

def generate_social_post_with_image(
    user,
    song,
    custom_prompt: str = "",
    platform: str = "instagram"
) -> Dict[str, Any]:
    """
    Generate social media post with AI-generated image
    
    Args:
        user: Authenticated user
        song: Song object
        custom_prompt: Custom prompt from user (e.g., "Make it more energetic")
        platform: Target platform (instagram, tiktok, facebook)
    
    Returns:
        Dict with caption, hashtags, image_url, default_prompt
    """
    profile = getattr(user, "artist_profile", None)
    stage_name = profile.stage_name if profile and getattr(profile, "stage_name", None) else getattr(user, "username", "Unknown")
    genre = profile.primary_genre if profile and getattr(profile, "primary_genre", None) else "Hip-hop/Rap"

    # Generate caption and hashtags
    caption_prompt = (
        f"Create a viral {platform} caption for this song:\n\n"
        f"Artist: {stage_name}\n"
        f"Song: {song.title}\n"
        f"Genre: {genre}\n"
        f"Lyrics snippet: {song.transcription[:200] if song.transcription else 'Instrumental'}\n\n"
    )
    
    if custom_prompt:
        caption_prompt += f"Artist's request: {custom_prompt}\n\n"
    
    caption_prompt += (
        f"Create:\n"
        f"1. A catchy caption (2-3 lines, emojis included)\n"
        f"2. 10 trending hashtags\n\n"
        f"Make it authentic, engaging, and platform-appropriate for {platform}."
    )
    
    caption_response = _call_gemini(caption_prompt)
    
    # Parse response (simple split by lines)
    lines = caption_response.split('\n')
    caption = '\n'.join(lines[:3]) if len(lines) >= 3 else caption_response[:280]
    hashtags = ' '.join([line for line in lines if line.strip().startswith('#')])
    
    if not hashtags:
        hashtags = f"#{genre.replace(' ', '')} #NewMusic #{stage_name.replace(' ', '')} #Viral #MusicPromotion"

    # Generate image using AI (multiple options)
    image_url = generate_ai_image_for_post(
        song_title=song.title,
        artist_name=stage_name,
        genre=genre,
        custom_prompt=custom_prompt,
        platform=platform
    )

    return {
        "caption": caption.strip(),
        "hashtags": hashtags.strip(),
        "image_url": image_url,
        "default_prompt": f"Promotional post for {song.title} by {stage_name}",
    }


def generate_ai_image_for_post(
    song_title: str,
    artist_name: str,
    genre: str,
    custom_prompt: str = "",
    platform: str = "instagram"
) -> str:
    """
    Generate AI image using multiple services
    Priority: Imagen 3 > DALL-E > Stability AI > Placeholder
    
    Returns:
        Image URL (string)
    """
    
    # Build image generation prompt
    base_prompt = (
        f"Create a professional music promotional image for {platform}. "
        f"Song: '{song_title}' by {artist_name}. "
        f"Genre: {genre}. "
        f"Style: Modern, vibrant, eye-catching, album cover aesthetic. "
        f"Include bold typography with song title. "
        f"High quality, 1080x1080 for Instagram. "
    )
    
    if custom_prompt:
        base_prompt += f"Additional style: {custom_prompt}. "
    
    base_prompt += "No faces, abstract art preferred."

    # Method 1: Try Google Imagen 3 (requires Vertex AI setup)
    try:
        image_url = generate_with_google_imagen(base_prompt)
        if image_url:
            return image_url
    except Exception as e:
        print(f"Imagen 3 failed: {e}")

    # Method 2: Try DALL-E (requires OpenAI API key)
    try:
        image_url = generate_with_dalle(base_prompt)
        if image_url:
            return image_url
    except Exception as e:
        print(f"DALL-E failed: {e}")

    # Method 3: Try Stability AI (requires API key)
    try:
        image_url = generate_with_stability_ai(base_prompt)
        if image_url:
            return image_url
    except Exception as e:
        print(f"Stability AI failed: {e}")

    # Fallback: Return placeholder or use a template
    return generate_placeholder_image(song_title, artist_name, genre)


# ============================================================
# Image Generation Methods
# ============================================================

def generate_with_google_imagen(prompt: str) -> str:
    """
    Generate image using Google Imagen 3 (Vertex AI)
    Requires: google-cloud-aiplatform library and project setup
    """
    try:
        from google.cloud import aiplatform
        from vertexai.preview.vision_models import ImageGenerationModel
        
        # Initialize Vertex AI
        aiplatform.init(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        )
        
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",  # Square for Instagram
        )
        
        if images and len(images) > 0:
            # Upload to cloud storage and return URL
            # For now, return base64 or local path
            return images[0].url if hasattr(images[0], 'url') else ""
    except Exception as e:
        print(f"Imagen error: {e}")
        return ""


def generate_with_dalle(prompt: str) -> str:
    """
    Generate image using OpenAI DALL-E
    Requires: openai library and API key
    """
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        return response['data'][0]['url']
    except Exception as e:
        print(f"DALL-E error: {e}")
        return ""


def generate_with_stability_ai(prompt: str) -> str:
    """
    Generate image using Stability AI (Stable Diffusion)
    Requires: Stability AI API key
    """
    try:
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            return ""
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        body = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            data = response.json()
            # Save image and return URL
            # For now return base64 or placeholder
            return data.get('artifacts', [{}])[0].get('url', '')
    except Exception as e:
        print(f"Stability AI error: {e}")
        return ""


def generate_placeholder_image(song_title: str, artist_name: str, genre: str) -> str:
    """
    Generate placeholder image URL using a service like Placeholder.com or UI Avatars
    """
    # Option 1: Use placeholder.com with custom text
    text = f"{song_title}+by+{artist_name}".replace(' ', '+')
    return f"https://via.placeholder.com/1080x1080/6366F1/FFFFFF?text={text}"
    
    # Option 2: Use DiceBear for avatar-style images
    # return f"https://api.dicebear.com/7.x/shapes/svg?seed={song_title}&size=1080"
    
    # Option 3: Use Unsplash for music-related stock photos
    # return f"https://source.unsplash.com/1080x1080/?music,{genre}"


# ============================================================
# Alternative: Local Image Generation with PIL (No API needed)
# ============================================================

def generate_local_promotional_image(song_title: str, artist_name: str, genre: str) -> str:
    """
    Generate a simple promotional image locally using PIL
    No external API required - good for MVP/testing
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        import base64
        from django.core.files.base import ContentFile
        
        # Create image
        width, height = 1080, 1080
        
        # Gradient background colors based on genre
        genre_colors = {
            "HipHop": [(99, 102, 241), (139, 92, 246)],  # Blue to Purple
            "Pop": [(236, 72, 153), (251, 146, 60)],      # Pink to Orange
            "R&B": [(59, 130, 246), (147, 51, 234)],      # Blue to Purple
            "Afrobeat": [(234, 179, 8), (239, 68, 68)],   # Yellow to Red
            "Default": [(99, 102, 241), (139, 92, 246)]
        }
        
        colors = genre_colors.get(genre, genre_colors["Default"])
        
        # Create gradient
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        for y in range(height):
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / height)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / height)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / height)
            draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
        
        # Add text
        try:
            # Try to use a nice font
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw song title
        title_bbox = draw.textbbox((0, 0), song_title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) / 2
        draw.text((title_x, 400), song_title, fill='white', font=font_large)
        
        # Draw artist name
        artist_bbox = draw.textbbox((0, 0), artist_name, font=font_medium)
        artist_width = artist_bbox[2] - artist_bbox[0]
        artist_x = (width - artist_width) / 2
        draw.text((artist_x, 520), artist_name, fill='white', font=font_medium)
        
        # Draw genre
        genre_bbox = draw.textbbox((0, 0), genre.upper(), font=font_small)
        genre_width = genre_bbox[2] - genre_bbox[0]
        genre_x = (width - genre_width) / 2
        draw.text((genre_x, 620), genre.upper(), fill='rgba(255,255,255,0.8)', font=font_small)
        
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to Django media storage
        from django.core.files.storage import default_storage
        filename = f"social_posts/{song_title}_{artist_name}.png".replace(' ', '_')
        path = default_storage.save(filename, ContentFile(buffer.read()))
        
        # Return media URL
        from django.conf import settings
        return f"{settings.MEDIA_URL}{path}"
        
    except Exception as e:
        print(f"Local image generation error: {e}")
        return generate_placeholder_image(song_title, artist_name, genre)


# ============================================================
# Example usage in generate_social_post_with_image
# ============================================================
# Update the function to use local generation as fallback:

def generate_ai_image_for_post_v2(
    song_title: str,
    artist_name: str,
    genre: str,
    custom_prompt: str = "",
    platform: str = "instagram"
) -> str:
    """
    Enhanced version with local fallback
    """
    # Try cloud AI services first
    base_prompt = (
        f"Professional music promotional image for {platform}. "
        f"Song: '{song_title}' by {artist_name}. Genre: {genre}. "
        f"Modern, vibrant, eye-catching style. 1080x1080. {custom_prompt}"
    )
    
    # Try external APIs
    for generator in [generate_with_google_imagen, generate_with_dalle, generate_with_stability_ai]:
        try:
            url = generator(base_prompt)
            if url:
                return url
        except Exception:
            continue
    
    # Fallback to local generation
    return generate_local_promotional_image(song_title, artist_name, genre)