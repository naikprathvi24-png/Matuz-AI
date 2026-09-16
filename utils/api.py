import os
import base64

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found. Please check your .env file."
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY,
    timeout=60.0
)


# ============================================================
# NORMAL TEXT AI RESPONSE
# ============================================================

def get_ai_response(prompt):

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Matuz AI, an intelligent study assistant. "
                        "Help students understand study material clearly. "
                        "Give accurate, well-structured answers. "
                        "Use headings, bullet points and examples when useful."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3,

            max_tokens=2048
        )

        return response.choices[0].message.content

    except Exception as e:

        return (
            "❌ Unable to generate AI response.\n\n"
            f"Error: {type(e).__name__}: {str(e)}"
        )


# ============================================================
# FIND AVAILABLE VISION MODEL
# ============================================================

def get_available_vision_model():

    preferred_models = [
        "qwen/qwen3.8-27b",
        "qwen/qwen3.6-27b",
    ]

    try:

        models = client.models.list()

        available_ids = {
            model.id
            for model in models.data
            if getattr(model, "active", True)
        }

        for model_id in preferred_models:

            if model_id in available_ids:

                return model_id

    except Exception:
        pass

    return None


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def get_image_response(
    prompt,
    image_bytes,
    mime_type
):

    try:

        vision_model = get_available_vision_model()

        if not vision_model:

            return (
                "❌ Image analysis is currently unavailable.\n\n"
                "Your Groq API key does not currently provide "
                "access to a supported vision model."
            )


        # ----------------------------------------------------
        # CONVERT IMAGE TO BASE64
        # ----------------------------------------------------

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")


        image_url = (
            f"data:{mime_type};base64,{encoded_image}"
        )


        # ----------------------------------------------------
        # SEND IMAGE TO GROQ
        # ----------------------------------------------------

        response = client.chat.completions.create(

            model=vision_model,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI study assistant. "
                        "Analyze images containing notes, "
                        "textbooks, diagrams, screenshots, "
                        "handwritten notes or study material. "
                        "Explain the content clearly and accurately."
                    )
                },

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text": prompt
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url": image_url
                            }
                        }

                    ]
                }
            ],

            temperature=0.3,

            max_tokens=2048
        )


        return response.choices[0].message.content


    except Exception as e:

        return (
            "❌ Unable to analyze image.\n\n"
            f"Error: {type(e).__name__}: {str(e)}"
        )


# ============================================================
# VOICE TRANSCRIPTION
# ============================================================

def transcribe_audio(
    audio_bytes,
    filename="audio.wav"
):

    try:

        transcription = client.audio.transcriptions.create(

            file=(
                filename,
                audio_bytes
            ),

            model="whisper-large-v3-turbo",

            response_format="text"
        )

        return transcription


    except Exception as e:

        return (
            "❌ Voice transcription failed.\n\n"
            f"Error: {type(e).__name__}: {str(e)}"
        )