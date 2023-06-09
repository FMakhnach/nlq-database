import os
from pydub import AudioSegment
from speech_recognition import AudioFile, Recognizer


def try_recognize_text_from_audio(audio_file, language: str = 'ru_RU') -> str or None:
    wav_file_path = 'temp.wav'
    try:
        # Convert to WAV
        audio = AudioSegment.from_file(audio_file)
        audio.export(wav_file_path, format="wav")

        recognizer = Recognizer()
        with AudioFile(wav_file_path) as source:
            audio_text = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio_text, language=language)
                return text
            except Exception as e:
                print(e)
                return None
    finally:
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
