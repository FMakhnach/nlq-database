import os
from pydub import AudioSegment
from speech_recognition import AudioFile, Recognizer


def ogg_to_text(ogg_file_path: str) -> str or None:
    if not ogg_file_path.endswith('.ogg'):
        raise Exception('Not ogg file')
    wav_file_path = ogg_file_path[:-4] + '.wav'
    try:
        # Convert to WAV
        audio = AudioSegment.from_file(ogg_file_path, format="ogg")
        audio.export(wav_file_path, format="wav")

        language = 'ru_RU'  # TODO choice
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
