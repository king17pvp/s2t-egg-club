
from stt_scic.train.example_trainer import ExampleTrainer
from stt_scic.utils.text_normalizer import normalize_text
from stt_scic.postprocessing import *

from stt_scic.preprocessing.denoise import denoise_audio
from stt_scic.preprocessing.remove_silence import remove_silence
from stt_scic.preprocessing.record_voice import record_audio, record_audio_until_keypress
import os
import tempfile
import librosa
import numpy as np

def create_audio_pipeline(record_mode="fixed", record_seconds=10, vad_mode=1, sample_rate=16000):
    """
    Tạo hàm tiền xử lý âm thanh kết hợp: ghi âm -> khử nhiễu -> loại bỏ khoảng lặng
    
    Parameters:
        record_mode (str): Chế độ ghi âm - "fixed" (thời gian cố định) hoặc "keypress" (nhấn phím để dừng)
        record_seconds (int): Thời gian ghi âm nếu sử dụng chế độ "fixed"
        vad_mode (int): Mức độ loại bỏ khoảng lặng (0-3)
        sample_rate (int): Tần số lấy mẫu
    
    Returns:
        function: Hàm tiền xử lý để cung cấp cho ASRPipeline
    """
    def preprocessing_fn(audio_input=None):
        """
        Tiền xử lý âm thanh thông qua 3 bước: ghi âm -> khử nhiễu -> loại bỏ khoảng lặng
        
        Parameters:
            audio_input: Có thể là None (sẽ ghi âm mới), đường dẫn file âm thanh, 
                        hoặc dữ liệu numpy array
        
        Returns:
            numpy.ndarray: Âm thanh đã xử lý
        """
        # Tạo các file tạm để lưu trữ giữa các bước xử lý
        temp_dir = tempfile.mkdtemp()
        raw_audio_path = os.path.join(temp_dir, "raw_audio.wav")
        denoised_path = os.path.join(temp_dir, "denoised.wav")
        no_silence_path = os.path.join(temp_dir, "no_silence.wav")

        try:
            # Bước 1: Xác định nguồn âm thanh đầu vào
            if audio_input is None:
                # Ghi âm mới nếu không có đầu vào
                print("Bắt đầu ghi âm...")
                if record_mode == "fixed":
                    success = record_audio(raw_audio_path, record_seconds=record_seconds, sample_rate=sample_rate)
                else:  # record_mode == "keypress"
                    success = record_audio_until_keypress(raw_audio_path, key_to_stop="space", 
                                                       max_duration=300, sample_rate=sample_rate)
                
                if not success:
                    print("Ghi âm thất bại!")
                    return None
                
                input_path = raw_audio_path
            elif isinstance(audio_input, str) and os.path.exists(audio_input):
                # Sử dụng file âm thanh hiện có
                input_path = audio_input
            elif isinstance(audio_input, np.ndarray):
                # Lưu dữ liệu numpy array thành file WAV
                import soundfile as sf
                sf.write(raw_audio_path, audio_input, sample_rate)
                input_path = raw_audio_path
            else:
                raise ValueError("audio_input phải là None, đường dẫn file, hoặc numpy array")
            
            # Bước 2: Khử nhiễu
            print("Đang khử nhiễu...")
            denoise_audio(input_path, denoised_path, sr=sample_rate)
            
            # Bước 3: Loại bỏ khoảng lặng
            print("Đang loại bỏ khoảng lặng...")
            remove_silence(denoised_path, no_silence_path, vad_mode)
            
            # Bước 4: Đọc file đã xử lý và trả về dữ liệu
            processed_audio, _ = librosa.load(no_silence_path, sr=sample_rate)
            print("Tiền xử lý âm thanh hoàn tất!")
            return processed_audio
        
        except Exception as e:
            print(f"Lỗi trong quá trình tiền xử lý: {str(e)}")
            return None
        finally:
            # Dọn dẹp file tạm (tuỳ chọn)
            # Nếu muốn giữ lại các file tạm, hãy comment các dòng dưới
            for file_path in [raw_audio_path, denoised_path, no_silence_path]:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            try:
                os.rmdir(temp_dir)
            except:
                pass
    
    return preprocessing_fn

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
            if audio is None:
                return "Không thể xử lý âm thanh."
        text = self.model.transcribe(audio)
        if self.postprocessing_fn:
            text = self.postprocessing_fn(text)
        return text

    def load_model(self, model_repo_or_path):
        pass
    
    def __call__(self, audio):
        return self.transcribe(audio)