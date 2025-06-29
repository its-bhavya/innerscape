import requests
import time
import os

ASSEMBLY_API_KEY = os.getenv("ASSEMBLY_API_KEY")
BASE_URL = "https://api.assemblyai.com"

headers = {
    "authorization": ASSEMBLY_API_KEY
}

def transcribe(audio_path):
    # Upload audio
    with open(audio_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/v2/upload",
            headers=headers,
            data=f
        )
    response.raise_for_status()
    audio_url = response.json()["upload_url"]

    # Request transcription
    data = {
        "audio_url": audio_url,
        "speech_model": "universal"
    }

    response = requests.post(f"{BASE_URL}/v2/transcript", json=data, headers=headers)
    response.raise_for_status()
    transcript_id = response.json()['id']

    polling_endpoint = f"{BASE_URL}/v2/transcript/{transcript_id}"
    print(f"Polling for transcript ID: {transcript_id}")
    for i in range(30):  # ~90 sec max
        result = requests.get(polling_endpoint, headers=headers).json()
        print(f"[{i}] Status: {result['status']}")
        if result['status'] == 'completed':
            return result['text']
            print (result['text'])
        elif result['status'] == 'error':
            raise RuntimeError(f"Transcription failed: {result['error']}")
        time.sleep(3)
    raise TimeoutError("Polling timed out after 90 seconds.")