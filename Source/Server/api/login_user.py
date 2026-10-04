import hashlib
from secrets import token_urlsafe

import bcrypt
from fastapi import APIRouter, status

from Source.Server.auth.token import token_generator
from Source.Server.database.database import get_user, update_token
from Source.Server.models.user import User

router = APIRouter()

@router.post("/login")
async def login(user: User):

	result = await get_user(user.username)
	password = hashlib.sha256(user.password.strip().encode()).digest()

	try:

		if bcrypt.checkpw(password, result['password'].encode('utf-8')):

			new_refresh = token_urlsafe(64)
			await update_token(user.username, new_refresh)

			return {"status": f"{status.HTTP_200_OK}", "bearer": token_generator(user.username, "user"), "refresh_token": new_refresh}

	except ValueError:
		return {"status": f"{status.HTTP_401_UNAUTHORIZED}", "message": "Invalid password"}
