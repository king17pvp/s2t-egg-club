import torch
from .model import STTModel

class Whisper(STTModel):
    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    def load_checkpoints(self, model_path: str):
        import whisper
        self.model = whisper.load_model(model_path, device=self.device)

    def transcribe(self, audio_path: str) -> str:
        transcript = self.model.transcribe(audio_path, language="vietnamese")
        return transcript
    
if __name__ == "__main__":
    whisper = Whisper()
    whisper.load_checkpoints("medium")
    # print(f"Transcript: {whisper.transcribe(audio_path)}")