"""Audio helpers for EldhoAi voice input and local speech output.

Speech-to-text uses NVIDIA's hosted Riva ASR endpoint. Text-to-speech
uses the computer's installed speech engine through pyttsx3.
"""

from __future__ import annotations

import os
import tempfile
import threading
import wave
from pathlib import Path
from typing import Optional

import numpy as np

SAMPLE_RATE = 16_000
CHANNELS = 1
SAMPLE_WIDTH_BYTES = 2  # int16 PCM
RIVA_SERVER = "grpc.nvcf.nvidia.com:443"
RIVA_FUNCTION_ID = "d3fe9151-442b-4204-a70d-5fcc597fd610"  # Parakeet TDT 0.6B v2 (offline ASR)


class VoiceRecorder:
    """Record mono 16 kHz audio from the default microphone."""

    def __init__(self) -> None:
        self._stream = None
        self._chunks = []
        self._lock = threading.Lock()
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        """Start recording. Call stop() to finish and create a temporary WAV."""
        if self._recording:
            return

        try:
            import sounddevice as sd
        except ImportError as error:
            raise RuntimeError(
                "Microphone support is not installed. Run: pip install sounddevice numpy"
            ) from error

        self._chunks = []

        def on_audio(indata, frames, timing, status):
            # Copy the captured samples because PortAudio reuses its input buffer.
            if status:
                # Overflow warnings are non-fatal; preserve captured audio.
                pass
            with self._lock:
                self._chunks.append(indata.copy())

        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                callback=on_audio,
            )
            self._stream.start()
            self._recording = True
        except Exception as error:
            self._stream = None
            self._recording = False
            raise RuntimeError(
                "EldhoAi could not start the microphone. Check Windows microphone permissions "
                "and make sure a microphone is connected."
            ) from error

    def stop(self) -> str:
        """Stop capture and return a temporary 16-bit mono WAV file path."""
        if not self._recording or self._stream is None:
            raise RuntimeError("The microphone is not recording.")

        stream = self._stream
        self._stream = None
        self._recording = False

        try:
            stream.stop()
            stream.close()
        except Exception:
            try:
                stream.close()
            except Exception:
                pass

        with self._lock:
            chunks = list(self._chunks)
            self._chunks.clear()

        if not chunks:
            raise RuntimeError("No audio was captured. Please check your microphone and try again.")

        samples = np.concatenate(chunks, axis=0)
        if samples.size < SAMPLE_RATE // 4:
            raise RuntimeError("The recording was too short. Speak for a little longer and try again.")

        temp_file = tempfile.NamedTemporaryFile(prefix="eldhoai_voice_", suffix=".wav", delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            with wave.open(temp_path, "wb") as wav_file:
                wav_file.setnchannels(CHANNELS)
                wav_file.setsampwidth(SAMPLE_WIDTH_BYTES)
                wav_file.setframerate(SAMPLE_RATE)
                wav_file.writeframes(samples.astype(np.int16, copy=False).tobytes())
        except Exception:
            try:
                os.remove(temp_path)
            except OSError:
                pass
            raise

        return temp_path

    def cancel(self) -> None:
        """Stop recording without saving or transcribing the audio."""
        stream = self._stream
        self._stream = None
        self._recording = False
        self._chunks = []
        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass


def transcribe_audio_file(audio_path: str | os.PathLike[str], language_code: str = "en-US") -> str:
    """Transcribe a 16-bit mono WAV file using NVIDIA's hosted Riva ASR."""
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    function_id = os.getenv("NVIDIA_ASR_FUNCTION_ID", RIVA_FUNCTION_ID).strip()
    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY was not found in your .env file. Keep your existing NVIDIA key there."
        )

    try:
        import riva.client
    except ImportError as error:
        raise RuntimeError(
            "NVIDIA Riva client is not installed. Run: pip install nvidia-riva-client"
        ) from error

    wav_path = Path(audio_path)
    with wave.open(str(wav_path), "rb") as wav_file:
        if wav_file.getnchannels() != CHANNELS or wav_file.getsampwidth() != SAMPLE_WIDTH_BYTES:
            raise RuntimeError("The audio format is not supported. Please record again.")
        sample_rate = wav_file.getframerate()
        audio_bytes = wav_file.readframes(wav_file.getnframes())

    if not audio_bytes:
        raise RuntimeError("The recording was empty. Please try again.")

    metadata = [
        ["function-id", function_id],
        ["authorization", f"Bearer {api_key}"],
    ]
    # Use named arguments so the connection options stay explicit across
    # nvidia-riva-client versions.
    auth = riva.client.Auth(
        use_ssl=True,
        uri=RIVA_SERVER,
        metadata_args=metadata,
    )
    service = riva.client.ASRService(auth)
    config = riva.client.RecognitionConfig(
        encoding=riva.client.AudioEncoding.LINEAR_PCM,
        sample_rate_hertz=sample_rate,
        language_code=language_code,
        max_alternatives=1,
        enable_automatic_punctuation=True,
        audio_channel_count=CHANNELS,
    )

    try:
        response = service.offline_recognize(audio_bytes, config)
    except Exception as error:
        # Do not assume this is an internet problem: gRPC can report useful
        # status details for API-key access, quota, endpoint, and audio issues.
        grpc_status = ""
        grpc_details = ""
        try:
            code = error.code()
            grpc_status = getattr(code, "name", str(code))
        except Exception:
            pass
        try:
            grpc_details = str(error.details() or "").strip()
        except Exception:
            pass

        details = grpc_details or str(error).strip()
        details = details[:700] if details else "No additional error details were provided."
        combined = f"{grpc_status} {details}".lower()

        if any(token in combined for token in ("unauthenticated", "401", "invalid api key", "unauthorized")):
            explanation = (
                "NVIDIA did not authenticate this speech request. Confirm the NVIDIA_API_KEY in .env, "
                "and that it is an NVIDIA API Catalog key with access to the hosted ASR model."
            )
        elif any(token in combined for token in ("permission_denied", "403", "permission denied")):
            explanation = (
                "NVIDIA denied access to this hosted speech model. Open the model's page in NVIDIA API Catalog, "
                "choose Get API Key / Try API, and confirm the model's access terms are accepted."
            )
        elif any(token in combined for token in ("resource_exhausted", "429", "quota", "rate limit")):
            explanation = (
                "The hosted speech service may have reached a quota or rate limit. Wait and try again, "
                "or check the model's usage/access in NVIDIA API Catalog."
            )
        elif any(token in combined for token in ("not_found", "404", "function not found")):
            explanation = (
                "NVIDIA could not find the hosted ASR function. Check that the Function ID and model access "
                "match the English Parakeet ASR API Catalog instructions."
            )
        elif any(token in combined for token in ("invalid_argument", "400", "unsupported audio", "sample rate", "unavailable model requested")):
            explanation = (
                "NVIDIA received the request, but the selected speech model does not appear to support the "
                "requested recognition mode or audio settings. This is a model/configuration mismatch, not "
                "evidence of an internet problem. The default has been changed to NVIDIA Parakeet TDT 0.6B v2 "
                "for offline transcription. If it persists, verify this model is enabled for your NVIDIA API key."
            )
        elif any(token in combined for token in ("unavailable", "deadline_exceeded", "deadline exceeded", "timeout")):
            explanation = (
                "The NVIDIA speech endpoint was unavailable or timed out. Your internet can still be working; "
                "wait briefly and retry."
            )
        else:
            explanation = (
                "The request reached a failure inside the speech-recognition call. This message alone does not "
                "prove your internet is the problem. Use the status/details below to identify the cause."
            )

        status_line = f"gRPC status: {grpc_status}\n" if grpc_status else ""
        raise RuntimeError(
            f"{explanation}\n\n{status_line}NVIDIA details: {details}"
        ) from error

    transcripts = []
    for result in getattr(response, "results", []) or []:
        alternatives = getattr(result, "alternatives", []) or []
        if alternatives:
            text = getattr(alternatives[0], "transcript", "").strip()
            if text:
                transcripts.append(text)

    transcript = " ".join(transcripts).strip()
    if not transcript:
        raise RuntimeError("I couldn't detect any speech. Try speaking clearly a little closer to the microphone.")
    return transcript


_speech_lock = threading.Lock()
_current_engine = None


def _clean_text_for_speech(text: str) -> str:
    """Remove common Markdown/URLs before speaking an AI response aloud."""
    import re

    text = re.sub(r"```.*?```", " Code block omitted. ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\((?:https?://)[^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Avoid unexpectedly reading a very long response out loud.
    if len(text) > 5000:
        text = text[:5000].rsplit(" ", 1)[0] + ". The rest of the response is available on screen."
    return text


def speak_text(text: str) -> None:
    """Read text aloud on a background thread using the local system voice."""
    cleaned = _clean_text_for_speech(text or "")
    if not cleaned:
        return

    # Stop any earlier utterance before starting a newer reply.
    stop_speaking()
    thread = threading.Thread(target=_speak_worker, args=(cleaned,), daemon=True)
    thread.start()


def _speak_worker(text: str) -> None:
    global _current_engine
    engine = None
    try:
        import pyttsx3
        engine = pyttsx3.init()
        with _speech_lock:
            _current_engine = engine
        engine.say(text)
        engine.runAndWait()
    except Exception as error:
        # Keep speech failures from crashing EldhoAi's chat window.
        print(f"EldhoAi speech output error: {error}")
    finally:
        with _speech_lock:
            if _current_engine is engine:
                _current_engine = None
        try:
            if engine is not None:
                engine.stop()
        except Exception:
            pass


def stop_speaking() -> None:
    """Stop current text-to-speech playback, if active."""
    with _speech_lock:
        engine = _current_engine
    if engine is not None:
        try:
            engine.stop()
        except Exception:
            pass
