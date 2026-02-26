import os

from google import genai
from google.genai import Client as GenaiClient

from .tts import TtsApi


class GeminiClient:
    def __init__(self, client: GenaiClient | None = None, api_key: str | None = None):
        if api_key:
            self._client = genai.Client(api_key)
        else:    
            self._client = client or genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        self.tts = TtsApi(client=self._client)
