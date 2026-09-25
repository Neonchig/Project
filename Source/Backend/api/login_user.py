import hashlib

import bcrypt
from fastapi import APIRouter, status

from Source.Backend.auth.token import token_generator
from Source.Backend.database.database import get_user
from Source.Backend.models.user import User

router = APIRouter()

@router.post("/login")
async def login(user: User):

	result = await get_user(user.username)
	password = hashlib.sha256(user.password.strip().encode()).digest()

	try:
		if bcrypt.checkpw(password, result['password'].encode('utf-8')):
			return {"status": status.HTTP_200_OK, "bearer": token_generator(user.username, "user")}
	except ValueError:
		return {"status": status.HTTP_401_UNAUTHORIZED, "message": "Invalid password"}
