import hashlib
from secrets import token_urlsafe

import bcrypt
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from Source.auth.token import token_generator
from Source.database.database import get_user, update_token
from Source.models.user import User

router = APIRouter()

@router.post(
	"/login",
	responses = {
		200: {"description": "Logged in successfully"},
		401: {"description": "Invalid credentials"}
	})
async def login(user: User):

	result = await get_user(user.username.lower())
	password = hashlib.sha256(user.password.strip().encode()).digest()

	try:

		if bcrypt.checkpw(password, result['password'].encode('utf-8')):

			new_refresh = token_urlsafe(64)
			await update_token(user.username, new_refresh)

			return JSONResponse(
				status_code = status.HTTP_200_OK,
				content = {'bearer': token_generator(user.username, 'user'), 'refresh_token': new_refresh}
			)

		return JSONResponse(
			status_code = status.HTTP_401_UNAUTHORIZED,
			content = {'detail': 'Invalid credentials'}
		)


	except ValueError:
	 	return JSONResponse(
			status_code = status.HTTP_401_UNAUTHORIZED,
			content = {'detail': 'Invalid credentials',}
		)
