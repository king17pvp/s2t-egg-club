# # audio_recorder.py

# import pyaudio
# import wave
# import time # Có thể không cần thiết nếu không có độ trễ chủ động

# def record_audio(output_filename="/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav", 
#                  record_seconds=10, 
#                  sample_rate=16000, 
#                  channels=1, 
#                  chunk_size=1024,
#                  audio_format=pyaudio.paInt16):
#     """
#     Thu âm từ microphone và lưu vào file WAV.

#     Tham số:
#         output_filename (str): Tên file WAV để lưu.
#         record_seconds (int): Thời gian thu âm (giây).
#         sample_rate (int): Tần số lấy mẫu (samples/giây).
#         channels (int): Số kênh (1 cho mono, 2 cho stereo).
#         chunk_size (int): Số khung hình mỗi buffer.
#         audio_format (pyaudio.paFormat): Định dạng mẫu âm thanh (ví dụ: pyaudio.paInt16).

#     Trả về:
#         bool: True nếu thu âm và lưu file thành công, False nếu có lỗi.
#     """

#     audio = pyaudio.PyAudio()
#     stream = None  # Khởi tạo stream là None để kiểm tra trong khối finally

#     print(f"Chuẩn bị thu âm {record_seconds} giây vào file: {output_filename}")

#     try:
#         stream = audio.open(format=audio_format,
#                             channels=channels,
#                             rate=sample_rate,
#                             input=True,
#                             frames_per_buffer=chunk_size)
#     except Exception as e:
#         print(f"Lỗi khi mở stream: {e}")
#         print("Hãy chắc chắn bạn đã cắm microphone và cho phép truy cập.")
#         audio.terminate()
#         return False

#     print("Đang thu âm...")
#     frames = []

#     for i in range(0, int(sample_rate / chunk_size * record_seconds)):
#         try:
#             data = stream.read(chunk_size, exception_on_overflow=False)
#             frames.append(data)
#         except IOError as ex:
#             print(f"Lỗi I/O khi đọc stream: {ex}")
#             if hasattr(pyaudio, 'paInputOverflowed') and ex.errno == pyaudio.paInputOverflowed: # Kiểm tra xem pyaudio.paInputOverflowed có tồn tại không
#                 print("Input bị tràn. Một số dữ liệu có thể đã bị mất.")
#             continue
#         except Exception as e:
#             print(f"Lỗi không xác định khi đọc stream: {e}")
#             break # Thoát vòng lặp nếu có lỗi nghiêm trọng

#     print("Kết thúc thu âm.")

#     # Dừng và đóng stream, giải phóng tài nguyên
#     if stream:
#         stream.stop_stream()
#         stream.close()
#     audio.terminate()

#     # Lưu dữ liệu âm thanh vào file WAV
#     try:
#         with wave.open(output_filename, 'wb') as wf:
#             wf.setnchannels(channels)
#             wf.setsampwidth(audio.get_sample_size(audio_format))
#             wf.setframerate(sample_rate)
#             wf.writeframes(b''.join(frames))
#         print(f"Đã lưu file thu âm vào: {output_filename}")
#         return True
#     except Exception as e:
#         print(f"Lỗi khi lưu file WAV: {e}")
#         return False

# if __name__ == '__main__':
#     # Đây là phần để bạn chạy thử nghiệm trực tiếp file audio_recorder.py
#     # Nếu bạn import file này từ file khác, đoạn code dưới đây sẽ không chạy.
#     print("Chạy thử nghiệm trực tiếp hàm record_audio:")
    
#     # Thu âm 3 giây với tên file mặc định
#     # success = record_audio(record_seconds=3)
#     # if success:
#     #     print("Thu âm thử nghiệm 1 thành công!")
#     # else:
#     #     print("Thu âm thử nghiệm 1 thất bại.")

#     # Thu âm 5 giây với tên file tùy chỉnh và các thông số khác
#     custom_filename = "/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav"
#     success_custom = record_audio(output_filename=custom_filename, 
#                                   record_seconds=10, 
#                                   sample_rate=16000, 
#                                   channels=1) # Mono
#     if success_custom:
#         print(f"Thu âm thử nghiệm 2 thành công! File được lưu tại: {custom_filename}")
#     else:
#         print("Thu âm thử nghiệm 2 thất bại.")

# audio_recorder.py

import pyaudio
import wave
import time
import os
from pynput import keyboard  # Thay thế keyboard bằng pynput
import numpy as np

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
    # Đảm bảo thư mục chứa file tồn tại
    os.makedirs(os.path.dirname(os.path.abspath(output_filename)), exist_ok=True)
    
    audio = pyaudio.PyAudio()
    stream = None
    
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
            continue
        except Exception as e:
            print(f"Lỗi không xác định khi đọc stream: {e}")
            break
    
    print("Kết thúc thu âm.")
    
    # Dừng và đóng stream
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

def record_audio_until_keypress(output_filename="/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav", 
                               key_to_stop="space",
                               max_duration=300,
                               sample_rate=16000, 
                               channels=1, 
                               chunk_size=1024,
                               audio_format=pyaudio.paInt16):
    """
    Thu âm từ microphone cho đến khi nhấn phím chỉ định, hoặc đạt thời gian tối đa.
    
    Tham số:
        output_filename (str): Tên file WAV để lưu.
        key_to_stop (str): Phím để dừng thu âm (mặc định: space).
        max_duration (int): Thời gian tối đa cho phép thu âm (giây).
        sample_rate (int): Tần số lấy mẫu (samples/giây).
        channels (int): Số kênh (1 cho mono, 2 cho stereo).
        chunk_size (int): Số khung hình mỗi buffer.
        audio_format (pyaudio.paFormat): Định dạng mẫu âm thanh.
    
    Trả về:
        bool: True nếu thu âm và lưu file thành công, False nếu có lỗi.
    """
    # Đảm bảo thư mục chứa file tồn tại
    os.makedirs(os.path.dirname(os.path.abspath(output_filename)), exist_ok=True)
    
    audio = pyaudio.PyAudio()
    frames = []
    stop_recording = False
    
    # Sử dụng pynput để bắt sự kiện phím
    def on_press(key):
        nonlocal stop_recording
        try:
            # Kiểm tra nếu là phím space
            if key == keyboard.Key.space and key_to_stop == "space":
                stop_recording = True
                return False
            elif hasattr(key, 'char') and key.char == key_to_stop:
                stop_recording = True
                return False
        except AttributeError:
            pass
    
    # Bắt đầu lắng nghe phím nhấn trong một luồng riêng biệt
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    try:
        stream = audio.open(format=audio_format,
                            channels=channels,
                            rate=sample_rate,
                            input=True,
                            frames_per_buffer=chunk_size)
    except Exception as e:
        print(f"Lỗi khi mở stream: {e}")
        audio.terminate()
        listener.stop()
        return False
    
    print(f"Đang thu âm... Nhấn phím '{key_to_stop}' để dừng (tối đa {max_duration} giây)")
    start_time = time.time()
    
    # Thu âm cho đến khi người dùng dừng hoặc đạt thời gian tối đa
    try:
        while not stop_recording and (time.time() - start_time) < max_duration:
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)
            
            # Hiển thị thời gian đã trôi qua
            elapsed = int(time.time() - start_time)
            if elapsed % 5 == 0 and elapsed > 0:
                print(f"\rThời gian thu âm: {elapsed}s", end="", flush=True)
    except KeyboardInterrupt:
        print("\nĐã hủy thu âm")
    except Exception as e:
        print(f"\nLỗi khi thu âm: {e}")
    
    # Giải phóng tài nguyên
    stream.stop_stream()
    stream.close()
    audio.terminate()
    listener.stop()
    
    # Kiểm tra xem có dữ liệu thu âm không
    if len(frames) == 0:
        print("Không có dữ liệu thu âm được lưu.")
        return False
    
    # Lưu dữ liệu âm thanh vào file WAV
    try:
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(audio_format))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        duration = len(frames) * chunk_size / sample_rate
        print(f"\nĐã lưu file thu âm ({duration:.1f} giây) vào: {output_filename}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file WAV: {e}")
        return False

def record_audio_interactive(output_filename="/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav", 
                            sample_rate=16000, 
                            channels=1, 
                            chunk_size=1024,
                            audio_format=pyaudio.paInt16):
    """
    Thu âm tương tác cho phép người dùng quyết định khi nào bắt đầu/dừng.
    """
    # Đảm bảo thư mục chứa file tồn tại
    os.makedirs(os.path.dirname(os.path.abspath(output_filename)), exist_ok=True)
    
    while True:
        choice = input("Chọn phương thức thu âm:\n"
                      "1. Nhập thời gian cụ thể (giây)\n"
                      "2. Thu âm cho đến khi nhấn phím\n"
                      "Lựa chọn của bạn (1/2): ")
        
        if choice == '1':
            try:
                seconds = int(input("Nhập thời gian thu âm (giây): "))
                if seconds <= 0:
                    print("Thời gian phải lớn hơn 0.")
                    continue
                return record_audio(output_filename, seconds, sample_rate, channels, chunk_size, audio_format)
            except ValueError:
                print("Vui lòng nhập một số nguyên hợp lệ.")
        elif choice == '2':
            return record_audio_until_keypress(output_filename, "space", 300, sample_rate, channels, chunk_size, audio_format)
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn 1 hoặc 2.")

if __name__ == '__main__':
    # File output mặc định
    custom_filename = "/Users/vietnguyen/Desktop/Deep learning/s2t_scic/s2t-egg-club/stt_scic/data/my_voice/output_recording.wav"
    
    # Sử dụng phương thức thu âm cố định thời gian (an toàn nhất)
    # record_audio(custom_filename, record_seconds=5)
    
    # Hoặc nếu muốn thu âm với phím dừng (cài đặt pynput trước)
    record_audio_until_keypress(custom_filename, key_to_stop="space")
    
    # Hoặc sử dụng phương thức tương tác
    # record_audio_interactive(custom_filename)