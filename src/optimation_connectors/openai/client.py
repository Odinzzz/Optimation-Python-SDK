from openai import OpenAI

from .ocr import OcrApi
from .files import FilesApi


class OpenAiClient:
    def __init__(self, client: OpenAI = None, api_key:str = None):
        if api_key:
            self.client = OpenAI(api_key)
        else:    
            self.client = client or OpenAI()

        self.ocr = OcrApi(client = self.client)
        self.files = FilesApi(client = self.client)