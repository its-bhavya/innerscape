import json
import re

def clean_json_from_string(text: str):
    """
    Cleans a JSON string that may be wrapped in markdown (```json ... ```) or improperly escaped.
    Returns a Python object (dict or list), or raises ValueError.
    """
    try:
        # Strip markdown block if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
