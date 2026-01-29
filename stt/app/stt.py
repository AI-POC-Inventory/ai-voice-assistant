from fastapi import APIRouter, UploadFile
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import os


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()


@router.post("/stream")
async def streaming_stt(audio: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())

        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=open(tmp.name, "rb"),
            response_format="verbose_json"
        )

    return {
        "text": transcript["text"],
        "language": transcript.get("language", "auto"),
        "segments": transcript.get("segments", [])
    }
