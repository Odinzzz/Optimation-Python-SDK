import os
from elevenlabs.client import ElevenLabs
from .tts import TtsApi


class ElevenLabsClient:
    def __init__(self, client: ElevenLabs = None, api_key:str = None):
        if api_key:
            self._client = ElevenLabs(api_key=api_key),

        else:    
            self._client = client or ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

        self.tts = TtsApi(client=self._client)

