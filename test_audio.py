import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtMultimedia import QMediaCaptureSession, QAudioInput, QMediaRecorder, QMediaFormat
from PySide6.QtCore import QUrl, QTimer

app = QApplication(sys.argv)

session = QMediaCaptureSession()
audio_input = QAudioInput()
session.setAudioInput(audio_input)

recorder = QMediaRecorder()
session.setRecorder(recorder)

# Set format to WAV
fmt = QMediaFormat()
fmt.setFileFormat(QMediaFormat.FileFormat.Wave)
recorder.setMediaFormat(fmt)

output_url = QUrl.fromLocalFile(os.path.abspath("test_audio.wav"))
recorder.setOutputLocation(output_url)

def stop_recording():
    print("Stopping recording...")
    recorder.stop()
    print("Saved to", output_url.toLocalFile())
    app.quit()

print("Starting recording...")
recorder.record()
QTimer.singleShot(3000, stop_recording)
app.exec()
