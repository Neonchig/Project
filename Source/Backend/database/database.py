import datetime

import aiosqlite
from fastapi import status

from Source.Backend.core.config import env
from Source.Backend.models.user import User


async def register_user(username: str, password: str, refresh_token: str, email: str | None = None) -> dict[str, str | int]:

	connection = await aiosqlite.connect(f"{env['ProjPath']}/Source/Backend/database/app.db")

	try:
		await connection.execute("INSERT INTO users (username, password, email, refresh_token, token_until) VALUES (?, ?, ?, ?, ?)",
			[
				username.lower(),
				password,
				(email.lower() if email else email),
				refresh_token,
				(datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=30))
			]
		)

	except aiosqlite.IntegrityError as e:
		await connection.commit()
		await connection.close()
		return {"status": status.HTTP_409_CONFLICT, "message": f"User with this {'email' if 'email' in str(e) else 'username'} already exists"}

	await connection.commit()
	await connection.close()

	return {"status": status.HTTP_201_CREATED}

async def login_user(username: str) -> User:

	connection = await aiosqlite.connect(f"{env['ProjPath']}/Source/Backend/database/app.db")
	connection.row_factory = aiosqlite.Row

	try:

		output = await connection.execute("SELECT * FROM users WHERE username = ?", [username.lower()])
		output = list(await output.fetchall())
		await connection.close()

		if len(output) > 1:
			return {'type': 'about:blank', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': 'Internal database error'}

		entry = next(iter(output))
		user_info = User(username = entry['username'], password = entry['password'], email = entry['email'])

	except Exception as e:
		await connection.close()
		return str(e)
		 # TODO: Хэндлить исключения

	return user_info
