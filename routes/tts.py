from flask import Blueprint, request, jsonify, Response
from flask_cors import cross_origin
import requests
import os

tts_bp = Blueprint("tts", __name__)

@tts_bp.route("/text-to-speech", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
def text_to_speech():
    data = request.get_json()
    text = data.get("text", "")
    voice_id = data.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Default to Rachel
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # ElevenLabs API configuration
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ElevenLabs API key not configured"}), 500
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return Response(
                response.content,
                mimetype="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=speech.mp3",
                    "Access-Control-Allow-Origin": "http://localhost:3000",
                    "Access-Control-Allow-Methods": "POST",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        else:
            error_msg = f"ElevenLabs API error: {response.status_code}"
            if response.text:
                error_msg += f" - {response.text}"
            return jsonify({"error": error_msg}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Alternative endpoint without ElevenLabs (fallback using gTTS)
@tts_bp.route("/text-to-speech-simple", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
def text_to_speech_simple():
    """Fallback TTS using Google Text-to-Speech (gTTS)"""
    try:
        from gtts import gTTS
        import io
        
        data = request.get_json()
        text = data.get("text", "")
        lang = data.get("lang", "en")
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to BytesIO object
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return Response(
            audio_buffer.getvalue(),
            mimetype="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
        
    except ImportError:
        return jsonify({"error": "gTTS not installed. Install with: pip install gtts"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
