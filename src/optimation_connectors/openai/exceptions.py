from optimation_core import ConnectorError

class OcrInputError(ConnectorError):
    ...

class OcrBadMimeTypeError(OcrInputError):
    ...