# backend/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64

app = FastAPI(title="InnerScape Backend")

# Allow CORS for local development and your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextPayload(BaseModel):
    text: str

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Mock transcription, ignore actual audio content
    return {"transcript": "This is a mocked transcription of your audio journal entry."}

@app.post("/journal/summary")
async def journal_summary(payload: TextPayload):
    # Mock summary based on the input text
    summary = "This is a warm, supportive summary highlighting the key feelings and themes in your journal."
    return {"summary": summary}

@app.post("/journal/prompts")
async def journal_prompts(payload: TextPayload):
    # Mock reflective questions
    prompts = [
        "What emotions stood out to you in this entry?",
        "Can you identify any patterns in your thoughts or feelings?",
        "What small step can you take to nurture yourself today?"
    ]
    return {"prompts": prompts}

@app.post("/journal/resources")
async def journal_resources(payload: TextPayload):
    # Mock wellness resources - URLs can be replaced with actual helpful links
    resources = [
        {"title": "Mindfulness Meditation Guide", "url": "https://www.mindful.org/how-to-meditate/"},
        {"title": "Stress Management Techniques", "url": "https://www.helpguide.org/articles/stress/stress-management.htm"},
        {"title": "Emotional Self-Care Tips", "url": "https://psychcentral.com/lib/what-is-emotional-self-care/"}
    ]
    return {"resources": resources}

@app.post("/journal/mindmap")
async def journal_mindmap(payload: TextPayload):
    # Return a small transparent PNG base64 as placeholder mindmap image
    transparent_png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAACXBIWXMAAAsTAAALEwEAmpwYAAAB"
        "WklEQVR4nO3YMQ6CMBBF0U8EuQoWxC6KKpDKZAn6xRqvYg6Ejr3kTr9MwHvCXkkMd4fe9PzP8XY8"
        "TKiIICICAgICAvzI7BrAm3lgAmPz/7nFh+hwACDwAAJhIIwjpPL8AiBc+wwTx33aQ3Ahm8PQyT4H"
        "1q86Sfh5xq6j+AAAgMAAAIDu5wXwV6Ho3E97cLgNgABAAACAwAA8DC+ADYCjIBARq6v/AnI15dcA"
        "AAAE5SURBVHja7cExAQAAAMKg9U9tCF8gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgFkAGa6x92HgAAAABJRU5ErkJggg=="
    )
    image_bytes = base64.b64decode(transparent_png_base64)

    return {"mindmap_png_base64": image_bytes}
