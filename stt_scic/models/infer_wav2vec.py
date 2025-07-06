import torch
import torchaudio
import time
import scipy
from datasets import Audio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from .model import STTModel

class Wav2Vec(STTModel):
    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    def load_checkpoints(self, model_path: str = "khanhld/wav2vec2-base-vietnamese-160h"):
        self.processor = Wav2Vec2Processor.from_pretrained(model_path)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_path)
        self.model.eval()
        self.model.to(self.device)
        # self.model = pipeline("automatic-speech-recognition", model=model_path, device=self.device)
    
    def transcribe(self, audio_path: str) -> str:
        try:
            waveform, sample_rate = torchaudio.load(audio_path)  # waveform is a tensor

            # Optional: Resample if needed
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
                waveform = resampler(waveform)
            speech_array = torch.tensor(waveform.squeeze(), dtype=torch.float32)
            
            inputs = self.processor(speech_array, return_tensors="pt", sampling_rate=16000, padding=True)
            input_values = inputs.input_values.to(self.device)
            
            start_time = time.time()
            with torch.no_grad():
                logits = self.model(input_values).logits
            inference_time = time.time() - start_time
            
            predicted_ids = torch.argmax(logits, dim=-1)
            predicted_text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            
            return {
                "text": predicted_text,
                "inference_time": inference_time
            }
            
            
        except Exception as e:
            return {
                "text": f"Error: {str(e)}",
                "inference_time": 0
            }

        # return result["text"]

if __name__ == "__main__":
    pho_whisper = Wav2Vec()
    pho_whisper.load_checkpoints("vinai/PhoWhisper-large")
    # print(f"Transcript: {pho_whisper.transcribe(audio_path)}")