from __future__ import annotations
import os
import threading
import wave
import speech_recognition as sr
from PySide6.QtCore import QObject, Signal, QByteArray
from PySide6.QtMultimedia import QAudioSource, QAudioFormat, QMediaDevices
from app.utils.logger import get_logger
from app.config import APP_DATA_DIR

logger = get_logger(__name__)

class DictationService(QObject):
    """
    Handles audio capture via PySide6 QAudioSource and transcription using SpeechRecognition.
    Produces raw 16-bit PCM WAV which is guaranteed to be compatible across platforms.
    """
    
    # Signal emitted when transcription is complete
    # signature: (textarea_id, transcribed_text, error_message)
    dictation_finished = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_path = os.path.join(APP_DATA_DIR, "temp_dictation.wav")
        self.current_textarea_id = ""
        self.current_language = "en-IN"
        
        self.fmt = QAudioFormat()
        self.fmt.setSampleRate(16000)
        self.fmt.setChannelCount(1)
        self.fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        
        self.device = QMediaDevices.defaultAudioInput()
        self.source = None
        self.io_device = None
        self.buffer = QByteArray()

    def start_recording(self, textarea_id: str):
        """Starts recording audio from the microphone."""
        self.current_textarea_id = textarea_id
        logger.info(f"Starting dictation for {textarea_id}...")
        
        self.buffer.clear()
        self.source = QAudioSource(self.device, self.fmt, self)
        self.io_device = self.source.start()
        
        if self.io_device:
            self.io_device.readyRead.connect(self._read_audio)
        else:
            logger.error("Failed to start QAudioSource")
            self.dictation_finished.emit(textarea_id, "", "Microphone access denied or unavailable.")

    def _read_audio(self):
        """Reads chunks of audio data as they become available."""
        if self.io_device:
            data = self.io_device.readAll()
            if data:
                self.buffer.append(data)

    def stop_recording(self, language: str = "en-IN"):
        """Stops recording, saves to a PCM WAV file, and processes in a thread."""
        logger.info(f"Stopping dictation for {self.current_textarea_id} (Language: {language})")
        self.current_language = language
        
        if self.source:
            self.source.stop()
            self.source = None
            self.io_device = None
            
        # Write buffer to WAV file manually to guarantee 16-bit PCM format
        try:
            with wave.open(self.audio_path, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2) # 16-bit
                w.setframerate(16000)
                w.writeframes(self.buffer.data())
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            self.dictation_finished.emit(self.current_textarea_id, "", f"Save error: {e}")
            return
            
        self.buffer.clear()
        
        # Process audio in background
        t = threading.Thread(target=self._process_audio, args=(self.current_textarea_id, self.current_language), daemon=True)
        t.start()

    def _process_audio(self, textarea_id: str, language: str):
        """Background thread worker to transcribe the WAV file."""
        recognizer = sr.Recognizer()
        text = ""
        error = ""
        
        try:
            if not os.path.exists(self.audio_path):
                error = "Audio file not found."
            else:
                with sr.AudioFile(self.audio_path) as source:
                    audio = recognizer.record(source)
                logger.info("Transcribing audio...")
                text = recognizer.recognize_google(audio, language=language)
                logger.info(f"Transcription successful: {text}")
        except sr.UnknownValueError:
            error = "Could not understand audio."
            logger.warning(error)
        except sr.RequestError as e:
            error = f"Speech service unavailable: {e}"
            logger.error(error)
        except Exception as e:
            error = f"An error occurred: {e}"
            logger.error(error)
            
        # Clean up the temporary audio file
        try:
            if os.path.exists(self.audio_path):
                os.remove(self.audio_path)
        except Exception as cleanup_err:
            logger.warning(f"Failed to delete temp audio file: {cleanup_err}")
        
        # Emit the result back to the main thread
        self.dictation_finished.emit(textarea_id, text, error)
