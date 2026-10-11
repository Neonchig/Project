import hashlib
import secrets

import bcrypt
from fastapi import APIRouter, status

from Source.Server.auth.token import token_generator
from Source.Server.database.database import register_user
from Source.Server.models.user import User

router = APIRouter()

@router.post("/register")
async def regUser(user: User):
	username = user.username.strip().lower()
	if user.email:
		email = user.email.strip()
	else:
		email = None
	password = user.password.strip().encode('utf-8')

	salt =  bcrypt.gensalt()
	password = bcrypt.hashpw(password, salt).decode()
	refresh_token = secrets.token_urlsafe(64)

	output = await register_user(username, password, refresh_token, email)

	if output["status"] != 201:
		return {"status": f"{status.HTTP_500_INTERNAL_SERVER_ERROR}"}

	return {'status': f"{status.HTTP_201_CREATED}", "refresh_token": refresh_token, "bearer": token_generator(username, 'user')}
