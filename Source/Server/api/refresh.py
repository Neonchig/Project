import logging
import secrets

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from Source.Server.auth.token import token_generator
from Source.Server.database.database import get_user, update_token

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
	"/refresh",
	responses = {
		422: {"description": "Token or username not provided"},
		401: {"description": "Invalid refresh token"},
		200: {"description": "Successfully refreshed"}
	})
async def refresh_tokens(data: dict[str, str]):


	username = data.get("username", "").lower()
	token = data.get("refresh_token", "")
	if not(username):
		return JSONResponse(
			status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
			content = {'detail': 'Invalid username'}
		)

	if not(token):
		return JSONResponse(
			status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
			content = {'detail': 'Invalid token'}
		)

	user = await get_user(username)

	real_token = user["refresh_token"]

	if token != real_token:
		return JSONResponse(
			status_code = status.HTTP_401_UNAUTHORIZED,
			content = {'detail': 'Invalid refresh token', 'actual_token': real_token}
		)

	new_token = secrets.token_urlsafe(64)
	await update_token(username, new_token)
	content = {"refresh_token": new_token, "bearer": token_generator(username, 'user')}
	logger.info(content)

	return JSONResponse(
		status_code = status.HTTP_200_OK,
		content = content
	)
