from pydantic import BaseModel, FilePath, Field
from typing import Optional

class Message(BaseModel):
    senderId: str = Field(min_length=36, max_length=36)
    sendTo: str
    message: str
    attachedFiles: Optional[FilePath]