import os
from typing import Tuple

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


async def analyze_text(text: str) -> Tuple[str, float, str, str]:
    """Analyze text content and return classification and related info."""
    if not openai.api_key:
        lower = text.lower()
        if any(word in lower for word in ["spam", "harass", "toxic"]):
            classification = "toxic"
            confidence = 0.9
        else:
            classification = "safe"
            confidence = 0.8
        reasoning = "Heuristic analysis without OpenAI key."
        return classification, confidence, reasoning, "{}"

    prompt = (
        "Classify the following content into one of [toxic, spam, harassment, safe] "
        "and explain briefly: \n" + text
    )
    try:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
        )
        message = completion.choices[0].message["content"].strip()
        classification = message.split("\n")[0].split()[0].lower()
        reasoning = message
        confidence = 0.75
        return classification, confidence, reasoning, str(completion)
    except Exception as exc:  # pragma: no cover - network errors
        return "error", 0.0, str(exc), "{}"


async def analyze_image(image_b64: str) -> Tuple[str, float, str, str]:
    """Placeholder for image analysis; uses text analyzer on base64 string."""
    return await analyze_text(image_b64)
