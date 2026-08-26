import sys
import wave
from PySide6.QtCore import QCoreApplication, QTimer, QIODevice, QByteArray
from PySide6.QtMultimedia import QAudioSource, QAudioFormat, QMediaDevices

app = QCoreApplication(sys.argv)

fmt = QAudioFormat()
fmt.setSampleRate(16000)
fmt.setChannelCount(1)
fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)

device = QMediaDevices.defaultAudioInput()
source = QAudioSource(device, fmt)

buffer = QByteArray()

io = source.start()

def read_more():
    data = io.readAll()
    if data:
        buffer.append(data)

io.readyRead.connect(read_more)

def stop_recording():
    source.stop()
    print(f"Captured {buffer.size()} bytes.")
    with wave.open("test_qaudio.wav", "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(buffer.data())
    app.quit()

QTimer.singleShot(2000, stop_recording)

app.exec()
