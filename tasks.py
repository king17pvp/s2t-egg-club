from celery import Celery
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
from stt_scic.models.infer_wav2vec import Wav2Vec
import tempfile
import base64
import uuid
import os

app = Celery(
    "tasks", 
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

# Load Whisper pipeline once (on GPU)
# from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor

# model_id = "openai/whisper-small"  # or tiny / medium

# model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
# processor = AutoProcessor.from_pretrained(model_id)

# # Set Vietnamese forced decoder tokens
# model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="vi", task="transcribe")

# pipe = pipeline(
#     "automatic-speech-recognition",
#     model=model,
#     tokenizer=processor.tokenizer,
#     feature_extractor=processor.feature_extractor,
#     device=-1 # or -1 for CPU
# )

stt_model = Wav2Vec()
stt_model.load_checkpoints()

@app.task()
def transcribe_audio_base64(audio_base64: str, file_ext: str = "wav"):
    print(">>> Received task to transcribe audio")
    try:
        # Decode and write to temp file
        file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.{file_ext}")
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(audio_base64))
        # with open(f"{uuid.uuid4()}.{file_ext}", "wb") as f:
        #     f.write(base64.b64decode(audio_base64))
        # Transcribe
        result = stt_model.transcribe(file_path)
        transcription = result["text"]
        print(">>> Transcription done")
        os.remove(file_path)
        return transcription

    except Exception as e:
        return f"Error: {str(e)}"
