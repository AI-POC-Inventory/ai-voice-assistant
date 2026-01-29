from fastapi import FastAPI
from app.stt import router as stt_router
from app.tts import router as tts_router
from app.webhooks import router as webhook_router

app = FastAPI(title="Voice AI Platform")
app.include_router(stt_router, prefix="/stt")
app.include_router(tts_router, prefix="/tts")
app.include_router(webhook_router, prefix="/webhook")
