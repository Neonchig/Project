import json

from pydantic import BaseModel, model_validator
from pydantic.fields import Field

class User(BaseModel):

    username: str = Field(min_length=3, max_length=16)
    password: str = Field(min_length=8, max_length=32)