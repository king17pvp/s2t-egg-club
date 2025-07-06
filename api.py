# from stt_scic.train.example_trainer import ExampleTrainer
# from stt_scic.utils.text_normalizer import normalize_text
# t = ExampleTrainer("ALO")
# print(normalize_text("ALO"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from tasks import app as celery_app

app = FastAPI()

class AudioRequest(BaseModel):
    audio_base64: str
    file_ext: str = "wav"

@app.post("/transcribe/")
async def transcribe_audio(request: AudioRequest):
    print("Request audio: ", request.audio_base64[:30])
    print("Request audio base 64 lenght: ", len(request.audio_base64))
    print("Request file extension: ", request.file_ext)
    task = celery_app.send_task(
        "tasks.transcribe_audio_base64",
        args=[request.audio_base64, request.file_ext]
    )
    return {"task_id": task.id}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        return {"status": "done", "transcription": result.result}
    else:
        return {"status": result.state}
