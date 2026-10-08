import asyncio
import getpass
import json

import aiofiles
import aiohttp
import keyring

# TODO: Полный рефактор этого ужаса

async def write_socket(websocket, first_message: str | None = None):
	if first_message:
		await websocket.send(first_message)
	while True:
		message = await asyncio.to_thread(input)
		if message == "exit":
			raise EOFError

		await websocket.send(message)

async def read_socket(websocket):
	async for message in websocket:
		try:
			print(message)
		except websockets.ConnectionClosed:
			print("Connection closed")

async def init() -> dict:
	config = await read_config()
	username = config.get('username', '')
	jwt = keyring.get_password('Messenger-JWT', username)
	if not(username):
		username = await asyncio.to_thread(input, "Введите имя пользователя: ")
		config['username'] = username
	if not (jwt):
		print(config)
		try:
			await refresh(f"{config.get('server', '')}:{config.get('api-port', '')}", config.get('username', ''), str(keyring.get_password('Messenger-Refresh', username)))
			return config

		except ValueError:
			while not(jwt):
				try:
					await login(
						f"{config.get('server', '')}:{config.get('api-port')}",
						username,
						await asyncio.to_thread(getpass.getpass, "Введите пароль: ")
					)
					jwt = keyring.get_password('Messenger-JWT', username)
				except ValueError as e:
					print(e.args)
	return config




async def read_config():
	async with aiofiles.open('config.json') as file:
		config_raw = await file.read()

		try:
			config = json.loads(config_raw)
		except json.JSONDecodeError:
			return {}

		return config

# ! НИКОГДА не вызывать перед read_config(), если не нужно полностью перезаписывать конфиг
# ! ВСЕГДА ждать окончания чтения, чтобы избежать состояния гонки
async def write_config(cfg: dict):
	async with aiofiles.open('config.json', 'w') as file:

		try:
			config_raw = json.dumps(cfg)
			await file.write(config_raw)

		except (json.JSONDecodeError):
			return False

		return True

async def refresh(host: str, username: str, refresh_token: str) -> None:
	async with aiohttp.ClientSession() as session:
		host = f"http://{host}/refresh"
		request = await session.post(host, json={"username": username, "refresh_token": refresh_token})
		response = await request.json()

	match response.get('status'):
		case '200':
			keyring.set_password("Messenger-Refresh", username, response.get('refresh_token', ''))
			keyring.set_password('Messenger-JWT', username, response.get('bearer', ''))
		case '422':
			raise ValueError(response.get('message', ''))
		case '401':
			raise ValueError(response.get('message', ''))
		case _:
			print(response)
			raise RuntimeError('Internal error')


async def login(host: str, username: str, password: str) -> None:
	async with aiohttp.ClientSession() as session:
		host = f"http://{host}/login"
		request = await session.post(host, json={"username": username, "password": password})
		response = await request.json()
		match response.get('status', ''):
			case '200':
				keyring.set_password("Messenger-Refresh", username, response.get('refresh_token', ''))
				keyring.set_password("Messenger-JWT", username, response.get('bearer', ''))
			case '422':
				raise ValueError('Misformating')
			case '401':
				raise ValueError('Invalid credentials')
			case _:
				raise RuntimeError('Internal error')

async def main():
	return_status = "init"
	config = await init()
	await write_config(config)
	uri = "ws://" + config.get('server', '') + ":" + str(config.get('ws-port', ''))
	try:
		async with websockets.connect(uri) as socket, asyncio.TaskGroup() as tg:
			return_status = "running"
			tg.create_task(read_socket(socket))
			tg.create_task(write_socket(socket, json.dumps({"Authorization": f"Bearer {keyring.get_password('Messenger-JWT', config.get('username', ''))}"})))
	except* websockets.ConnectionClosed:
		return_status = "closed_by_server"
	except* EOFError:
		return_status = "closed_by_client"

	return return_status
