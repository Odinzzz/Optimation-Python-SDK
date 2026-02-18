from enum import StrEnum


class CliAiProvider(StrEnum):
    CODEX = 'codex'
    CLAUDE = 'claude-code'
    GEMINI = 'gemini-cli'

class Template(StrEnum):
    FAST_API = 'fast-api'
    FLASK = 'flask'
    WORKER = 'worker'