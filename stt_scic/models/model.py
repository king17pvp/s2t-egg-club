from abc import ABC, abstractmethod

class STTModel(ABC):
    def __init__(self):
        self.model = None
    
    @abstractmethod
    def load_checkpoints(self, model_path: str):
        pass

    @abstractmethod
    def transcribe(self, audio_path: str):
        pass