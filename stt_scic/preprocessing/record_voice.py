# audio_recorder.py

import pyaudio
import wave
import time # Có thể không cần thiết nếu không có độ trễ chủ động

def record_audio(output_filename="/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav", 
                 record_seconds=10, 
                 sample_rate=16000, 
                 channels=1, 
                 chunk_size=1024,
                 audio_format=pyaudio.paInt16):
    """
    Thu âm từ microphone và lưu vào file WAV.

    Tham số:
        output_filename (str): Tên file WAV để lưu.
        record_seconds (int): Thời gian thu âm (giây).
        sample_rate (int): Tần số lấy mẫu (samples/giây).
        channels (int): Số kênh (1 cho mono, 2 cho stereo).
        chunk_size (int): Số khung hình mỗi buffer.
        audio_format (pyaudio.paFormat): Định dạng mẫu âm thanh (ví dụ: pyaudio.paInt16).

    Trả về:
        bool: True nếu thu âm và lưu file thành công, False nếu có lỗi.
    """

    audio = pyaudio.PyAudio()
    stream = None  # Khởi tạo stream là None để kiểm tra trong khối finally

    print(f"Chuẩn bị thu âm {record_seconds} giây vào file: {output_filename}")

    try:
        stream = audio.open(format=audio_format,
                            channels=channels,
                            rate=sample_rate,
                            input=True,
                            frames_per_buffer=chunk_size)
    except Exception as e:
        print(f"Lỗi khi mở stream: {e}")
        print("Hãy chắc chắn bạn đã cắm microphone và cho phép truy cập.")
        audio.terminate()
        return False

    print("Đang thu âm...")
    frames = []

    for i in range(0, int(sample_rate / chunk_size * record_seconds)):
        try:
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)
        except IOError as ex:
            print(f"Lỗi I/O khi đọc stream: {ex}")
            if hasattr(pyaudio, 'paInputOverflowed') and ex.errno == pyaudio.paInputOverflowed: # Kiểm tra xem pyaudio.paInputOverflowed có tồn tại không
                print("Input bị tràn. Một số dữ liệu có thể đã bị mất.")
            continue
        except Exception as e:
            print(f"Lỗi không xác định khi đọc stream: {e}")
            break # Thoát vòng lặp nếu có lỗi nghiêm trọng

    print("Kết thúc thu âm.")

    # Dừng và đóng stream, giải phóng tài nguyên
    if stream:
        stream.stop_stream()
        stream.close()
    audio.terminate()

    # Lưu dữ liệu âm thanh vào file WAV
    try:
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(audio_format))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        print(f"Đã lưu file thu âm vào: {output_filename}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file WAV: {e}")
        return False

if __name__ == '__main__':
    # Đây là phần để bạn chạy thử nghiệm trực tiếp file audio_recorder.py
    # Nếu bạn import file này từ file khác, đoạn code dưới đây sẽ không chạy.
    print("Chạy thử nghiệm trực tiếp hàm record_audio:")
    
    # Thu âm 3 giây với tên file mặc định
    # success = record_audio(record_seconds=3)
    # if success:
    #     print("Thu âm thử nghiệm 1 thành công!")
    # else:
    #     print("Thu âm thử nghiệm 1 thất bại.")

    # Thu âm 5 giây với tên file tùy chỉnh và các thông số khác
    custom_filename = "/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav"
    success_custom = record_audio(output_filename=custom_filename, 
                                  record_seconds=10, 
                                  sample_rate=16000, 
                                  channels=1) # Mono
    if success_custom:
        print(f"Thu âm thử nghiệm 2 thành công! File được lưu tại: {custom_filename}")
    else:
        print("Thu âm thử nghiệm 2 thất bại.")