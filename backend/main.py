from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import base64, os, shutil, json, re, sys, time, dspy
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

import dspy
api_key = os.getenv("GOOGLE_API_KEY")
dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash", api_key=api_key))

from app.utils.transcriber import transcribe
from app.utils.mindmap_generator import generate_mindmap
from app.utils.json_cleaner import clean_json_from_string
from app.agents.extractor_agent import MindmapExtractor
from app.agents.summary_agent import Summarizer
from app.agents.resource_agent import ResourceRecommender
from app.agents.companion_agent import CompanionChat

app = FastAPI(title="InnerScape Backend")

extractor = MindmapExtractor()
summarizer = Summarizer()
recommender = ResourceRecommender()
companion = CompanionChat()

class TextPayload(BaseModel):
    text: str

DATA_DIR = "backend/data"

@app.post("/transcribe")
def transcribe_audio(file: UploadFile = File(...)):
    start = time.time()
    os.makedirs(os.path.join(DATA_DIR, "audio"), exist_ok=True)
    audio_path = os.path.join(DATA_DIR, "audio", file.filename)

    with open(audio_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    print("File saved in:", time.time() - start)

    start_transcribe = time.time()
    text = transcribe(audio_path)
    print("Transcription done in:", time.time() - start_transcribe)

    print("Total time taken:", time.time() - start)

    return {"transcript": text}

class TranscriptRequest(BaseModel):
    transcript: str

@app.post("/extract")
def extract_json(req: TranscriptRequest):
    try:
        result = extractor.forward(transcript=req.transcript)
        subtopics = clean_json_from_string(result.subtopics)
        data = {"central_topic": result.central_topic, "subtopics": subtopics}

        os.makedirs(f"{DATA_DIR}/json", exist_ok=True)
        json_name = result.central_topic.replace(" ", "-")
        path = f"{DATA_DIR}/json/{json_name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Generate mindmap after JSON is created
        generate_mindmap(path)

        return {"success": True, "central_topic": result.central_topic, "path": path, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/mindmap/{topic}")
def get_mindmap(topic: str):
    file_path = os.path.join(DATA_DIR, "mindmaps", f"{topic}.png")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    return {"error": "Mindmap not found"}

@app.post("/journal/summary")
async def journal_summary(payload: TextPayload):
    result = summarizer.forward(transcript=payload)
    try:
        return{"success":True,"summary":result.summary}
    except Exception as e:
        return{"success":False, "error":str(e)}

@app.post("/journal/resources")
async def journal_resources(payload: TextPayload):
    result = recommender.forward(payload)
    try:
        resources = clean_json_from_string(result.strategies)
        print(resources)
        return {"resources": resources}
    except ValueError as e:
        return {"error": f"Failed to parse coping strategies: {e}"}

@app.post("/chat")
async def chat_reply(payload: dict):
    context = payload.get("context", "")
    user_message = payload.get("message", "")
    if not user_message:
        return {"error": "Message missing"}
    try:
        result = companion.forward(context=context, user_message=user_message)
        return {"response": result.companion_response}
    except Exception as e:
        return {"error": str(e)}