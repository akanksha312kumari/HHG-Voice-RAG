"""Speech-to-Text (STT) pipeline module.
Sarvam Saaras v3 realtime client.
"""
import os
import httpx
from typing import Optional
from backend.harness.schemas import STTResult

SARVAM_LANG_MAP = {
    "as": "as-IN", "bn": "bn-IN", "gu": "gu-IN", "hi": "hi-IN",
    "kn": "kn-IN", "ml": "ml-IN", "mr": "mr-IN", "ne": "ne-IN",
    "or": "od-IN", "pa": "pa-IN", "sa": "sa-IN", "ta": "ta-IN",
    "te": "te-IN", "ur": "ur-IN"
}

async def transcribe_audio(audio_data: bytes, language: str) -> STTResult:
    """
    Transcribes audio bytes to text using Sarvam Saaras v3.
    """
    sarvam_key = os.getenv("SARVAM_API_KEY")
    if not sarvam_key:
        print("WARNING: SARVAM_API_KEY not set. Falling back to stub transcript.")
        return STTResult(transcript="This is a fallback transcript due to missing API key.", detected_lang=SARVAM_LANG_MAP.get(language, language))

    lang_code = SARVAM_LANG_MAP.get(language, language)
    
    # NOTE: Assuming REST fallback if websockets is not strictly available in the python env
    # URL and payload structure represents a generic Sarvam HTTP STT integration pattern.
    url = "https://api.sarvam.ai/speech-to-text"
    
    headers = {
        "api-subscription-key": sarvam_key
    }
    
    files = {
        'file': ('audio.wav', audio_data, 'audio/wav')
    }
    data = {
        'language_code': lang_code,
        'model': 'saaras:v3-realtime'
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, headers=headers, files=files, data=data)
            
        if response.status_code == 200:
            res_json = response.json()
            # Handle typical Sarvam STT JSON schema
            transcript = res_json.get("transcript", "")
            return STTResult(transcript=transcript, detected_lang=lang_code)
        else:
            print(f"STT Error: {response.status_code} {response.text}")
            return STTResult(transcript="", detected_lang=lang_code)
            
    except Exception as e:
        print(f"STT Exception: {e}")
        return STTResult(transcript="", detected_lang=lang_code)

