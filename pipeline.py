
from stt_scic.train.example_trainer import ExampleTrainer
from stt_scic.utils.text_normalizer import normalize_text

from stt_scic.preprocessing.denoise import denoise_audio
from stt_scic.preprocessing.remove_silence import remove_silence
from stt_scic.preprocessing.record_voice import record_audio

from stt_scic.postprocessing import *

class ASRPipeline:
    def __init__(
        self, 
        model_class, 
        preprocessing_fn=None, 
        postprocessing_fn=None,
        model_kwargs=None,
    ):
        """
        ASR Pipeline using single preprocessing/postprocessing functions.

        Parameters:
        - model_class: A class or function returning a model with `.transcribe(audio)` method
        - preprocessing_fn: A function that takes raw audio and returns processed audio
        - postprocessing_fn: A function that takes raw text and returns final text
        - model_kwargs: Optional dict of keyword arguments for the model
        """
        self.model = model_class(**(model_kwargs or {}))
        self.preprocessing_fn = preprocessing_fn
        self.postprocessing_fn = postprocessing_fn

    def transcribe(self, audio):
        """
        Full transcription flow: audio → (pre) → model → (post) → text
        """
        if self.preprocessing_fn:
            audio = self.preprocessing_fn(audio)
        text = self.model.transcribe(audio)
        if self.postprocessing_fn:
            text = self.postprocessing_fn(text)
        return text

    def load_model(self, model_repo_or_path):
        pass
    
    def __call__(self, audio):
        return self.transcribe(audio)