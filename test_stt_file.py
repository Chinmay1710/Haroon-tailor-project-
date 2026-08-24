import speech_recognition as sr
import sys

r = sr.Recognizer()
file_path = "test_audio.wav"

try:
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)
    print("Recognizing...")
    text = r.recognize_google(audio, language="hi-IN")
    print("Text (Hindi):", text)
except Exception as e:
    print("Error:", e)
