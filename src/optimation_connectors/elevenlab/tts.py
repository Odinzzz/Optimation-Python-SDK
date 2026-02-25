import os
from typing import Literal
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

VoiceName = Literal["marc-aurel-qc-en", "luna-qc-en","brittney-qc-en","lana-fr-en", "theodore-nt", "john-en-fr"]
ModelName = Literal["eleven_multilingual_v2", "other"]
LanguageCode = Literal["fr", "en", "es"]

class TtsApi:
    def __init__(self, client: ElevenLabs | None = None):
        self._client = client or ElevenLabs(api_key=os.environ.get('ELEVENLABS_API_KEY'))
        self._voices: dict[VoiceName, str] = {
            "luna-qc-en": "iB0Pwf5VYt7UDBrGrMqH",
            "brittney-qc-en": "pjcYQlDFKMbcOUp6F5GD",
            "lana-fr-en": "rAmra0SCIYOxYmRNDSm3",
            "marc-aurel-qc-en": "RTFg9niKcgGLDwa3RFlz",
            "theodore-nt": "hqfrgApggtO1785R4Fsn",
            "john-en-fr": "EryqBbKuawX5rMsewc7f",
        }

    def generate(
            self,
            text:str,
            voice:VoiceName = 'marc-aurel-qc-en',
            model:ModelName = 'eleven_multilingual_v2',
            language_code: LanguageCode = 'en' 
        ):
        voice_id = self._voices[voice]

        return self._client.text_to_speech.convert(
            text=text,
            voice_id= voice_id,
            model_id=model,
            language_code=language_code,
            output_format="mp3_44100_128",
        )
        

