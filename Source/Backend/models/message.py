
from pydantic import BaseModel, Field, FilePath


class Message(BaseModel):
    senderId: str = Field(min_length=36, max_length=36)
    sendTo: str
    message: str
    attachedFiles: FilePath | None