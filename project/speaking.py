from main import EssayGrader
import os
import speech_recognition as sr  # STT

para_writing = EssayGrader("data.json")
topic, _ = para_writing.select_topic()


def speech_to_text(path):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Your topic is {topic}")
        print("Listening...")
        audio = recognizer.listen(source)
        print("Recognizing...")
        try:
            text = recognizer.recognize_google(audio)
            print(f'You said: {text}')
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}")
            return ""


text = speech_to_text(".")
scores, overall_score = para_writing.grade_essay(text)
for item, score in scores.items():
    print(f"{item}: ({score})")
output = f"Your overall score is {overall_score}."
print(output)
