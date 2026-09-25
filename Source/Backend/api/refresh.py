import secrets

from fastapi import APIRouter, status

from Source.Backend.auth.token import token_generator
from Source.Backend.database.database import get_user, update_token

router = APIRouter()

@router.post("/refresh")
async def refresh_tokens(data: dict[str, str]):

	username = data.get("username", "")
	token = data.get("token", "")
	user = await get_user(username)
	real_token = user["refresh_token"]

	if token != real_token:
		return {"status": f"{status.HTTP_401_UNAUTHORIZED}", "message": "Invalid refresh token"}

	new_token = secrets.token_urlsafe(64)
	await update_token(username, new_token)
	return {"status": f"{status.HTTP_200_OK}", "refresh": f"{new_token}", "bearer": f"{token_generator(username, 'user')}"}
