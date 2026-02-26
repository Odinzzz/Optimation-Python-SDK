from __future__ import annotations

from typing import Literal
import os
import mimetypes
import struct
import subprocess
import tempfile

from google.genai import types
from google.genai import Client as GenaiClient

VoiceName = Literal["Zephyr", "Puck"]
ModelName = Literal[
    "gemini-2.5-pro-preview-tts",
    "gemini-2.5-flash-preview-tts",
    "lyria-realtime-exp",
    "gemini-2.5-flash-native-audio-preview-12-2025",
]
OutFormat = Literal["wav", "mp3"]


class TtsApi:
    def __init__(self, client: GenaiClient | None = None):
        self._client = client or GenaiClient(api_key=os.environ.get("GEMINI_API_KEY"))

    def genrate(
        self,
        model: ModelName = "gemini-2.5-pro-preview-tts",
        system_prompt: str = "",
        prompt: str = "",
        voice_name: VoiceName = "Zephyr",
    ) -> types.GenerateContentResponse:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=1,
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                )
            ),
        )
        return self._client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

    # ----------------------------
    # Public helper: returns bytes ready to save
    # ----------------------------
    def synthesize(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        model: ModelName = "gemini-2.5-pro-preview-tts",
        voice_name: VoiceName = "Zephyr",
        out_format: OutFormat = "wav",
    ) -> tuple[bytes, str]:
        """
        Returns (audio_bytes, mime_type_of_returned_bytes).
        - out_format="wav": always returns a valid WAV container (PCM).
        - out_format="mp3": returns MP3 bytes (requires ffmpeg installed).
        """
        generation = self.genrate(
            model=model,
            system_prompt=system_prompt,
            prompt=prompt,
            voice_name=voice_name,
        )

        inline = self._extract_inline_audio(generation)
        audio_bytes = inline.data
        mime_type = inline.mime_type or ""

        # Ensure we have a real WAV first (wrap PCM if needed)
        wav_bytes = self._ensure_wav(audio_bytes, mime_type)

        if out_format == "wav":
            return wav_bytes, "audio/wav"

        # out_format == "mp3"
        mp3_bytes = self._wav_bytes_to_mp3(wav_bytes)
        return mp3_bytes, "audio/mpeg"

    # ----------------------------
    # Internals
    # ----------------------------
    def _extract_inline_audio(self, generation: types.GenerateContentResponse) -> types.Blob:
        try:
            part = generation.candidates[0].content.parts[0]
            inline = part.inline_data
        except Exception as e:
            raise RuntimeError("No audio part found in generation response.") from e

        if not inline or not inline.data:
            raise RuntimeError("Audio inline_data is empty.")
        return inline

    def _ensure_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        # If API returned a real audio container with known extension, we still
        # normalize to WAV for consistency when out_format="wav" or before mp3 encoding.
        # If it's PCM raw (audio/L16;rate=24000), we must add WAV header.
        mt = (mime_type or "").lower()

        # Raw PCM is usually "audio/L16;rate=24000"
        if "audio/l" in mt:
            return self._pcm_to_wav(audio_data, mime_type)

        # If it's already wav-ish, just return
        ext = mimetypes.guess_extension(mime_type or "")
        if ext == ".wav":
            return audio_data

        # Otherwise, we *could* attempt to decode other containers to wav,
        # but in practice Gemini TTS here is usually PCM. We'll be strict:
        # treat unknown as PCM and wrap (safe fallback).
        return self._pcm_to_wav(audio_data, mime_type)

    def _pcm_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        # Defaults
        bits_per_sample = 16
        sample_rate = 24000

        # Parse "audio/L16;rate=24000"
        parts = [p.strip() for p in (mime_type or "").split(";") if p.strip()]
        for p in parts:
            pl = p.lower()
            if pl.startswith("rate="):
                try:
                    sample_rate = int(p.split("=", 1)[1])
                except ValueError:
                    pass
            elif pl.startswith("audio/l"):
                try:
                    bits_per_sample = int(pl.split("audio/l", 1)[1])
                except ValueError:
                    pass

        num_channels = 1
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        data_size = len(audio_data)
        chunk_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            chunk_size,
            b"WAVE",
            b"fmt ",
            16,
            1,  # PCM
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_size,
        )
        return header + audio_data

    def _wav_bytes_to_mp3(self, wav_bytes: bytes) -> bytes:
        # Requires ffmpeg in PATH
        with tempfile.TemporaryDirectory() as td:
            wav_path = os.path.join(td, "in.wav")
            mp3_path = os.path.join(td, "out.mp3")

            with open(wav_path, "wb") as f:
                f.write(wav_bytes)

            subprocess.run(
                ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-q:a", "3", mp3_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            with open(mp3_path, "rb") as f:
                return f.read()