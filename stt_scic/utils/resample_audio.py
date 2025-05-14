import numpy as np
import librosa

def resample(audio, orig_sample_rate, target_sample_rate=16000):
    """
    Resample audio data to a target sample rate.
    
    Parameters:
        audio (numpy.ndarray): Input audio signal (1D array for mono, 2D array for stereo)
        orig_sample_rate (int): Original sample rate of the audio
        target_sample_rate (int, optional): Target sample rate. Default: 16000 Hz
        
    Returns:
        numpy.ndarray: Resampled audio signal
    """
    if orig_sample_rate == target_sample_rate:
        return audio
    
    # Handle mono vs stereo
    if len(audio.shape) > 1:
        # For stereo or multi-channel, process each channel
        resampled_channels = []
        for channel in range(audio.shape[1]):
            channel_data = audio[:, channel]
            resampled = librosa.resample(
                y=channel_data.astype(np.float32),
                orig_sr=orig_sample_rate,
                target_sr=target_sample_rate
            )
            resampled_channels.append(resampled)
        return np.stack(resampled_channels, axis=1)
    else:
        # For mono audio
        return librosa.resample(
            y=audio.astype(np.float32),
            orig_sr=orig_sample_rate,
            target_sr=target_sample_rate
        )

def split_audio(audio, sample_rate, segment_duration=30.0, min_segment_duration=5.0):
    """
    Split a long audio file into segments of specified duration.
    
    Parameters:
        audio (numpy.ndarray): Input audio signal (1D array for mono, 2D array for stereo)
        sample_rate (int): Sample rate of the audio
        segment_duration (float, optional): Duration of each segment in seconds. Default: 30.0
        min_segment_duration (float, optional): Minimum duration in seconds for the last segment.
                                               If the last segment is shorter, it will be discarded.
                                               Default: 5.0
    
    Returns:
        list: List of audio segments as numpy arrays
    """
    # Calculate samples per segment
    samples_per_segment = int(sample_rate * segment_duration)
    
    # Calculate total number of full segments
    total_samples = audio.shape[0]
    num_segments = total_samples // samples_per_segment
    
    segments = []
    
    # Extract full segments
    for i in range(num_segments):
        start_sample = i * samples_per_segment
        end_sample = (i + 1) * samples_per_segment
        
        if len(audio.shape) > 1:  # Stereo
            segment = audio[start_sample:end_sample, :]
        else:  # Mono
            segment = audio[start_sample:end_sample]
            
        segments.append(segment)
    # Handle the last segment if it's long enough
    remaining_samples = total_samples - (num_segments * samples_per_segment)
    min_samples = int(sample_rate * min_segment_duration)
    
    if remaining_samples >= min_samples:
        if len(audio.shape) > 1:  # Stereo
            last_segment = audio[num_segments * samples_per_segment:, :]
        else:  # Mono
            last_segment = audio[num_segments * samples_per_segment:]
            
        segments.append(last_segment)
    
    return segments