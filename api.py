from pydantic import BaseModel
from fastapi import FastAPI
from tts_handler import TTSHandler

app = FastAPI() 
handler = TTSHandler()

@app.get("/synthesize")
def synthesize(message: str):
    if handler is not None:
        print('Synthesizing message...')
        handler.synthesize(message) 
