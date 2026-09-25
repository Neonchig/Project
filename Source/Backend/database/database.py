import datetime

import aiosqlite
from fastapi import status
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from Source.Backend.core.config import env


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

async def get_user(username: str) -> aiosqlite.Row | dict[str, str]:

	connection = await aiosqlite.connect(f"{env['ProjPath']}/Source/Backend/database/app.db")
	connection.row_factory = aiosqlite.Row

	try:

		output = await connection.execute("SELECT * FROM users WHERE username = ?;", [username.lower()])
		output = list(await output.fetchall())
		await connection.close()

		if len(output) > 1:
			return {'type': 'about:blank', 'status': f"{status.HTTP_500_INTERNAL_SERVER_ERROR}", 'message': 'Internal database error'}


	except IndexError:
		await connection.close()
		return {"status": f"{HTTP_500_INTERNAL_SERVER_ERROR}", "message": "User not found"}
		 # TODO: Хэндлить исключения

	return output[0]


async def update_token(username: str, new_token: str):

	connection = await aiosqlite.connect(f"{env['ProjPath']}/Source/Backend/database/app.db")
	connection.row_factory = aiosqlite.Row

	try:
		await connection.execute("UPDATE users SET refresh_token=?, token_until=? WHERE username = ?;", [new_token, (datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=30)), username])
		await connection.commit()
		await connection.close()
	except ValueError:
		return {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "User not found"}
