
from groq import Groq

from backend.config import (
    GROQ_API_KEY,
    MODEL_NAME,
    validate_config
)


def get_groq_client():
    """
    Create and return a Groq API client.
    """

    validate_config()

    return Groq(
        api_key=GROQ_API_KEY
    )


def generate_ai_response(system_prompt, user_prompt):
    """
    Send instructions to Groq and return its response.
    """

    client = get_groq_client()

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.1,

        max_tokens=3000,

        response_format={
            "type": "json_object"
        }
    )

    if not response.choices:
        raise ValueError(
            "The AI service returned an empty response."
        )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "The AI service returned empty content."
        )

    return content
