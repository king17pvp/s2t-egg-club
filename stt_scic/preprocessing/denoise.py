import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np

def denoise_audio(input_path, output_path, sr=16000):
    """
    Denoise audio using noisereduce library
    
    Parameters:
        input_path (str): Path to input audio file
        output_path (str): Path to save denoised audio
        sr (int): Sample rate to use
    """
    # Load audio file
    audio, sample_rate = librosa.load(input_path, sr=sr)
    
    
    # Apply noise reduction
    reduced_noise = nr.reduce_noise(
        y=audio, 
        sr=sample_rate,
        stationary=True,
        prop_decrease=0.75
    )
    # Save denoised audio
    sf.write(output_path, reduced_noise, sample_rate)
    print(f"Denoised audio saved to {output_path}")

if __name__ == "__main__":
    # Input and output paths
    audio_path = "/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav"
    output_path = "/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/denoise_recording.wav"
    
    # Denoise audio
    denoise_audio(audio_path, output_path)

