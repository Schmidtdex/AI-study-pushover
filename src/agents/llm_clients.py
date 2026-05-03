from groq import Groq
from google import genai
from google.genai import types
from src.config import config

GROQ_MODEL = "llama-3.3-70b-versatile"

_groq_client = Groq(api_key=config.groq_api_key)

def groq_chat_json(
    system: str,
    user: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> str:
    response = _groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


# =========== Gemini
GEMINI_MODEL = "gemini-2.5-flash"
_genai_client = genai.Client(api_key=config.gemini_api_key)

def gemini_generate_text(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
) -> str:
    response = _genai_client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=500,  
        ),
        contents=user_prompt,
    )
    return response.text.strip()