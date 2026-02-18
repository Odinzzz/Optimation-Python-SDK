# connector/openai/ocr.py

from typing import Any
from openai import OpenAI

class OcrApi:
    def __init__(self, client: OpenAI = None):
        self.client = client or OpenAI()


    def _build_content(
        self,
        prompt: str,
        url: str = None,
        base64_data: str = None,
        file_id: str = None,
        mime_type: str = "application/pdf",
    ) -> list:
        """Construit le contenu du message selon les inputs fournis."""

        # we verified that only one files is provided

        sources = [url, base64_data, file_id]

        if sum(x is not None for x in sources) != 1:
            raise ValueError(
                "Exactly one of (url, base64_data, file_id) must be provided."
            )   
         
        if mime_type:
            accepted_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf']
            
            if mime_type not in accepted_types:
                raise ValueError(
                    f'File type {mime_type} supported use {accepted_types} file type'
                )
            
        content = [{"type": "input_text", "text": prompt}]

        if url and 'image' in mime_type:
            content.append({"type": "input_image", "image_url": url})
        elif url:    
            content.append({"type": "input_file", "file_url": url})
        elif file_id:
            content.append({"type": "input_file", "file_id": file_id})
        elif base64_data:
            content.append({
                "type": "input_file",
                "file_data": f"data:{mime_type};base64,{base64_data}",
            })

        return content

    def _build_messages(self, content: list, system_prompt: str = None) -> list:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})
        return messages

    def extract_data(
        self,
        url: str = None,
        base64_data: str = None,
        file_id: str = None,
        prompt: str = "Analyse ce document.",
        model: str = "gpt-4o",
        parse: bool = False,
        schema: Any = None,
        system_prompt: str = None,
        mime_type: str = "application/pdf",
    ) -> Any:
        content = self._build_content(prompt, url, base64_data, file_id, mime_type)
        messages = self._build_messages(content, system_prompt)

        kwargs = {"model": model, "input": messages}

        if parse and schema:
            kwargs["text_format"] = schema

        response = self.client.responses.parse(**kwargs)

        return response.output_parsed if (parse and schema) else response.output_text