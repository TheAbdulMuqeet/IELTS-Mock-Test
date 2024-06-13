import speech_recognition as sr  # STT
from pydub import AudioSegment
import pyttsx3  # TTS


def text_to_speech(text):
    filename = "./static/recording.wav"
    output_path = "./static/recording.mp3"
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
    engine.stop()

    audio = AudioSegment.from_wav(filename)
    audio.export(output_path, format="mp3")

# Function to recognize speech using SpeechRecognition
def speech_to_text(path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_text = recognizer.record(source)
        print("Listening...")
        audio = recognizer.listen(source)
        print("Recognizing...")
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        