from typing import Any
from openai import OpenAI
from openai import BadRequestError

from optimation_core.exceptions import ApiError
from .exceptions import OcrBadMimeTypeError, OcrInputError

class OcrApi:
    def __init__(self, client: OpenAI = None):
        self.client = client or OpenAI()

    

    def _build_content(
        self,
        prompt: str,
        mime_type: str,
        *,
        url: str | None = None,
        base64_data: str | None = None,
        file_id: str | None = None,
    ) -> list:
        """Construit le contenu du message selon les inputs fournis."""

        # we verified that only one files is provided

        sources = [url, base64_data, file_id]

        if sum(x is not None for x in sources) != 1:
            raise OcrInputError(
                "Exactly one of (url, base64_data, file_id) must be provided."
            )   
         
        
        accepted_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'}
            
        if mime_type not in accepted_types:
                raise OcrBadMimeTypeError(f"File type {mime_type} not supported. Use {sorted(accepted_types)}")
            
        content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt}]

        is_image = bool(mime_type and mime_type.startswith("image/"))
        
        if url:
            if is_image:
                content.append({"type": "input_image", "image_url": url})
            else:
                content.append({"type": "input_file", "file_url": url})
        
        elif base64_data:
            if is_image:
                content.append({
                    "type": "input_image",
                    "filename": "a.pdf", #TODO fixe naming
                    "file_data": f"data:{mime_type};base64,{base64_data}",
                })

            else:    
                content.append({
                    "type": "input_file",
                    "filename": "a.pdf", #TODO fixe naming
                    "file_data": f"data:{mime_type};base64,{base64_data}",
                })

        elif file_id:
            content.append({"type": "input_file", "file_id": file_id})            

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
        model: str = "gpt-5.2",
        schema: Any = None,
        system_prompt: str = None,
        mime_type: str = "application/pdf",
    ) -> Any:
        content = self._build_content(
            prompt=prompt,
            mime_type=mime_type,
            url=url,
            base64_data=base64_data,
            file_id=file_id
        )
        messages = self._build_messages(content, system_prompt)

        kwargs = {"model": model, "input": messages}

        if schema:
            kwargs["text_format"] = schema

        try:
            response = self.client.responses.parse(**kwargs)
        except BadRequestError as e:
            status = getattr(e, "status_code", 400)

            # Essaye de récupérer le body JSON propre
            error_data = None
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                except Exception:
                    pass

            # Fallback sur le message string
            message = str(e)

            # Extraire infos si possible
            error_code = None
            error_type = None
            error_param = None

            if error_data and "error" in error_data:
                err = error_data["error"]
                message = err.get("message", message)
                error_code = err.get("code")
                error_type = err.get("type")
                error_param = err.get("param")

            raise ApiError(
                url='openAI Api',
                status_code=status,
                message=message,
                details={
                    'code': error_code,
                    'error_type': error_type,
                    'param': error_param}
            ) from e

        return response.output_parsed if (schema) else response.output_text