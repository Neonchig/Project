import secrets

from fastapi import APIRouter, HTTPException, status

from Source.Server.auth.token import token_generator
from Source.Server.database.database import get_user, update_token

router = APIRouter()

@router.post(
	"/refresh",
	responses = {
		422: {"description": "Token or username not provided"},
		401: {"description": "Invalid refresh token"},
		200: {"description": "Successfully refreshed"}
	})
async def refresh_tokens(data: dict[str, str]):


	username = data.get("username", "")
	token = data.get("refresh_token", "")
	if not(username):
		return {'status': f"{status.HTTP_422_UNPROCESSABLE_CONTENT}", 'detail': 'Invalid username'}
	if not(token):
		return {'status': f"{status.HTTP_422_UNPROCESSABLE_CONTENT}", 'detail': 'Invalid token'}
	user = await get_user(username)

	real_token = user["refresh_token"]

	if token != real_token:
		return {'status': f"{status.HTTP_401_UNAUTHORIZED}", 'detail': 'Invalid refresh token'}

	new_token = secrets.token_urlsafe(64)
	await update_token(username, new_token)
	return {"status": f"{status.HTTP_200_OK}", "refresh_token": f"{new_token}", "bearer": f"{token_generator(username, 'user')}"}
