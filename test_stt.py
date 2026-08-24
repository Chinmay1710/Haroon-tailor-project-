import sounddevice as sd
import numpy as np
import speech_recognition as sr

def record_audio(duration=5, fs=16000):
    print("Recording...")
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording finished")
    
    # Convert numpy array to bytes
    audio_data = myrecording.tobytes()
    
    # Create AudioData object for SpeechRecognition
    audio = sr.AudioData(audio_data, fs, 2)
    return audio

def recognize():
    r = sr.Recognizer()
    audio = record_audio(5)
    try:
        print("Recognizing...")
        text = r.recognize_google(audio, language="en-IN")
        print("Text:", text)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

if __name__ == "__main__":
    recognize()
