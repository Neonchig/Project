from urllib import parse

from pydantic import BaseModel, field_validator
from pydantic.fields import Field


class User(BaseModel):

	username: str = Field(min_length=3, max_length=16)
	password: str = Field(min_length=8, max_length=60)
	email: str | None = Field(max_length=30, default=None)

	@field_validator('username')
	@classmethod
	def validate_username(cls, v: str) -> str:
		if parse.quote(v) == v:
			return v
		raise ValueError('Username must not contain url-unsafe characters')
