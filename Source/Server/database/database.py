
import datetime
import json
from sqlite3 import IntegrityError
from uuid import uuid4

import aiosqlite
from fastapi import status

from Source.Server.core.config import env

db_path = str(env.get('ProjPath', '')) + "/Source/Server/database/app.db"

async def get_unsent(username: str):
	connection = await aiosqlite.connect(db_path)
	cursor = await connection.execute("SELECT * FROM unsent WHERE to_username = ?;", [username])
	response = await cursor.fetchall()
	return [i for i, j in response]

async def move_to_unsent(message: str, sender: str, send_to: str):

	connection = await aiosqlite.connect(db_path)

	await connection.execute("INSERT INTO unsent (to_username, message) VALUES (?, ?)", [send_to, json.dumps({"sender": sender, "message": message})])
	await connection.commit()
	await connection.close()

	return True

async def clear_unsent(username: str):

	connection = await aiosqlite.connect(db_path)

	await connection.execute("DELETE FROM unsent WHERE to_username = ?;", [username])
	await connection.commit()
	await connection.close()

	return True

async def join_group(username: str, group_uuid: str):

	connection = await aiosqlite.connect(db_path)
	await connection.execute("INSERT INTO user_groups (username, group_uuid) VALUES (?, ?)", [username, group_uuid])
	await connection.commit()
	await connection.close()
	return True

async def create_group(group_name: str, description: str | None = None):
	if not(description):
		description = "No description provided"

	try:
		connection = await aiosqlite.connect(db_path)
		await connection.execute("INSERT INTO groups (name, uuid, description);", [group_name, uuid4(), description])
		await connection.commit()
		await connection.close()
		return True
	except IntegrityError:
		return False


async def get_group_by_name(group_name: str):
	connection = await aiosqlite.connect(db_path)
	cursor = await connection.execute("SELECT * FROM groups WHERE name = ?;", [group_name])
	response = await cursor.fetchall()
	return next(iter(response))

async def get_users_in_group(group_uuid: str):
	connection = await aiosqlite.connect(db_path)
	connection.row_factory = aiosqlite.Row
	cursor = await connection.execute("SELECT * FROM user_groups WHERE group_uuid = ?;", [group_uuid])
	response = await cursor.fetchall()
	output = [str(a) for a, _ in response]
	return output

async def user_in_group(group_uuid: str, username: str):
	return(username in (await get_users_in_group(group_uuid)))

async def register_user(username: str, password: str, refresh_token: str, email: str | None = None) -> dict[str, str | int]:

	connection = await aiosqlite.connect(db_path)

	try:
		await connection.execute("INSERT INTO users (username, password, email, refresh_token, token_until) VALUES (?, ?, ?, ?, ?);",
			[
				username.lower(),
				password,
				(email.lower() if email else email),
				refresh_token,
				(datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=30))
			]
		)

	except IntegrityError as e:
		await connection.commit()
		await connection.close()
		return {"status": status.HTTP_409_CONFLICT, "message": f"User with this {'email' if 'email' in str(e) else 'username'} already exists"}

	await connection.commit()
	await connection.close()

	return {"status": status.HTTP_201_CREATED}

async def get_user(username: str) -> aiosqlite.Row | dict[str, str]:

	connection = await aiosqlite.connect(db_path)
	connection.row_factory = aiosqlite.Row

	try:

		output = await connection.execute("SELECT * FROM users WHERE username = ?;", [username.lower()])
		output = list(await output.fetchall())
		await connection.close()

		if len(output) > 1:
			return {'type': 'about:blank', 'status': f"{status.HTTP_500_INTERNAL_SERVER_ERROR}", 'message': 'Internal database error'}


	except IndexError:
		await connection.close()
		return {"status": f"{status.HTTP_500_INTERNAL_SERVER_ERROR}", "message": "User not found"}
		 # TODO: Хэндлить исключения

	return output[0]


async def update_token(username: str, new_token: str):

	connection = await aiosqlite.connect(db_path)
	connection.row_factory = aiosqlite.Row

	try:
		await connection.execute("UPDATE users SET refresh_token=?, token_until=? WHERE username = ?;", [new_token, (datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=30)), username])
		await connection.commit()
		await connection.close()
	except ValueError:
		return {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "User not found"}
