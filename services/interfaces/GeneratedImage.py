from dataclasses import dataclass

@dataclass 
class GeneratedImage:
    provider: str
    model: str
    data: bytes
    mime_type: str
    revised_prompt: str | None = None


