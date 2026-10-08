import hashlib
import re
from secrets import token_urlsafe

import bcrypt
from fastapi import APIRouter, HTTPException, status

from Source.Server.auth.token import token_generator
from Source.Server.database.database import get_user, update_token
from Source.Server.models.user import User

router = APIRouter()

@router.post(
	"/login",
	responses = {
		200: {"description": "Logged in successfully"},
		401: {"description": "Invalid credentials"}
	})
async def login(user: User):

	result = await get_user(user.username)
	password = hashlib.sha256(user.password.strip().encode()).digest()

	try:

		if bcrypt.checkpw(password, result['password'].encode('utf-8')):

			new_refresh = token_urlsafe(64)
			await update_token(user.username, new_refresh)

			return {'status': f'{status.HTTP_200_OK}', 'bearer': token_generator(user.username, 'user'), 'refresh_token': new_refresh}

		return {'status': f"{status.HTTP_401_UNAUTHORIZED}", 'detail': 'Invalid credentials',}


	except ValueError:
	 	return {'status': f"{status.HTTP_401_UNAUTHORIZED}", 'detail': 'Invalid credentials',}
