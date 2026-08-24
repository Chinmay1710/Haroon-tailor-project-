from __future__ import annotations
import os
import threading
import speech_recognition as sr
from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtMultimedia import QMediaCaptureSession, QAudioInput, QMediaRecorder, QMediaFormat
from app.utils.logger import get_logger
from app.config import APP_DATA_DIR

logger = get_logger(__name__)

class DictationService(QObject):
    """
    Handles audio capture via PySide6 and transcription using SpeechRecognition.
    Must be instantiated in the main thread for QMediaRecorder to function correctly.
    """
    
    # Signal emitted when transcription is complete
    # signature: (textarea_id, transcribed_text, error_message)
    dictation_finished = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = QMediaCaptureSession(self)
        self.audio_input = QAudioInput(self)
        self.session.setAudioInput(self.audio_input)
        
        self.recorder = QMediaRecorder(self)
        self.session.setRecorder(self.recorder)
        
        # Configure format
        fmt = QMediaFormat()
        fmt.setFileFormat(QMediaFormat.FileFormat.Wave)
        self.recorder.setMediaFormat(fmt)
        
        # Define output path
        self.audio_path = os.path.join(APP_DATA_DIR, "temp_dictation.wav")
        self.recorder.setOutputLocation(QUrl.fromLocalFile(self.audio_path))
        
        self.current_textarea_id = ""
        self.current_language = "en-IN"

    def start_recording(self, textarea_id: str):
        """Starts recording audio from the microphone."""
        try:
            if os.path.exists(self.audio_path):
                os.remove(self.audio_path)
        except Exception:
            pass
            
        self.current_textarea_id = textarea_id
        logger.info(f"Starting dictation for {textarea_id}...")
        self.recorder.record()

    def stop_recording(self, language: str = "en-IN"):
        """Stops recording and processes the audio in a background thread."""
        logger.info(f"Stopping dictation for {self.current_textarea_id} (Language: {language})")
        self.current_language = language
        self.recorder.stop()
        
        # QMediaRecorder might need a few milliseconds to finalize the file.
        # We spawn a thread to handle the file processing.
        t = threading.Thread(target=self._process_audio, args=(self.current_textarea_id, self.current_language), daemon=True)
        t.start()

    def _process_audio(self, textarea_id: str, language: str):
        """Background thread worker to transcribe the WAV file."""
        import time
        # Give the recorder a tiny moment to flush the file to disk
        time.sleep(0.3)
        
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
        
        # Emit the result back to the main thread
        self.dictation_finished.emit(textarea_id, text, error)
