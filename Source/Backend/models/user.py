from pydantic import BaseModel

from pydantic.fields import Field

class User(BaseModel):

    username: str = Field(min_length=3, max_length=16)
    password: str = Field(min_length=8, max_length=32)
    email: str = Field(max_length=30)

class Login_user(BaseModel):

    username: str | None = Field(min_length = 3, max_length = 16, default = None)
    email: str | None = Field(max_length = 30, default = None)
    password: str = Field(min_length = 8, max_length = 32)