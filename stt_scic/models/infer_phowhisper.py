import torch
from transformers import pipeline
from model import STTModel

class Phowhisper(STTModel):
    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    def load_checkpoints(self, model_path: str):
        self.model = pipeline("automatic-speech-recognition", model=model_path, device=self.device)
    
    def transcribe(self, audio_path: str) -> str:
        result = self.model(audio_path)

        return result["text"]

if __name__ == "__main__":
    pho_whisper = Phowhisper()
    pho_whisper.load_checkpoints("vinai/PhoWhisper-large")
    # print(f"Transcript: {pho_whisper.transcribe(audio_path)}")