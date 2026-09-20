import hashlib

import bcrypt
from fastapi import APIRouter, status

from Source.Backend.database.database import login_user
from Source.Backend.models.user import User

router = APIRouter()

@router.post("/login")
async def login(user: User):

	result = await login_user(user.username)
	password = hashlib.sha256(user.password.strip().encode()).digest()

	return bcrypt.checkpw(password, result.password.encode('utf-8'))
	"""
	TODO: Сделать систему для генерации и возврата пользователю jwt токена
	"""
