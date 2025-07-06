from celery import Celery
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
from stt_scic.models.infer_wav2vec import Wav2Vec
import tempfile
import base64
import uuid
import os

stt_model = Wav2Vec()
stt_model.load_checkpoints()