from fastapi import APIRouter
from pydantic import BaseModel
import pyttsx3
import tempfile
from fastapi.responses import FileResponse
router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    voice: str | None = None  # optional

@router.post("/")
async def text_to_speech(req: TTSRequest):
    engine = pyttsx3.init()

    # Optional: select voice if available
    if req.voice:
        for v in engine.getProperty("voices"):
            if req.voice.lower() in v.name.lower():
                engine.setProperty("voice", v.id)
                break

    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    output_path = output_file.name
    output_file.close()

    engine.save_to_file(req.text, output_path)
    engine.runAndWait()

    return FileResponse(
        output_path,
        media_type="audio/wav",
        filename="speech.wav"
    )
