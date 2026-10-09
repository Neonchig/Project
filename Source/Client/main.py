import asyncio
import getpass
import json
import logging

import aiofiles
import aiohttp
import keyring
import websockets
from websockets.exceptions import ConnectionClosed

# WIP: Полный рефактор этого ужаса

logging.basicConfig(
		level = logging.DEBUG,
		format = "%(asctime)s %(levelname)s [%(taskName)s] %(message)s",
		force = True
	)
logger = logging.getLogger(__name__)



async def main():

	response = {'status': -1}
	config = await init()
	await write_config(config)

	logger.debug('Initialization complete')

	uri = "ws://" + config.get('server', '') + ":" + str(config.get('ws-port', ''))

	while response.get('status') != 1000:
		response = await connect(uri, config.get('username', ''))
		if response.get('status') != 1000:
			keyring.set_password('Messenger-JWT', config.get('username', ''), '')
			await init(False)



async def init(get_jwt: bool = True) -> dict:
	logger.debug('Trying to get config.')

	config = await read_config()
	logger.debug('Config successfully read!')

	username = config.get('username', '')

	if not(username):
		username = await asyncio.to_thread(input, "Введите имя пользователя: ")
		config['username'] = username

	logger.debug('Trying to get JWT and Refresh.')

	jwt = keyring.get_password('Messenger-JWT', username)

	if not (jwt and get_jwt):

		try:
			logger.info('Refreshing JWT')
			await refresh(
				f"{config.get('server', '')}:{config.get('api-port', '')}",
				config.get('username', ''), str( keyring.get_password('Messenger-Refresh', username) )
			)
			if not(keyring.get_password('Messenger-JWT', username)):
				logger.debug('Refreshing JWT Failed')
				raise ValueError

			return config

		except ValueError:
			logger.info('Requesting users password for auth')
			while not(jwt):
				try:
					await login(
						f"{config.get('server', '')}:{config.get('api-port')}",
						username,
						await asyncio.to_thread(getpass.getpass, "Введите пароль: ")
					)
					jwt = keyring.get_password('Messenger-JWT', username)
				except ValueError:
					...

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
		server = f"http://{host}/refresh"
		request = await session.post(server, json={"username": username, "refresh_token": refresh_token})
		response = await request.json()

	match response.get('status'):
		case '200':
			logger.info('Successfully updated JWT with refresh')
			keyring.set_password("Messenger-Refresh", username, response.get('refresh_token', ''))
			keyring.set_password('Messenger-JWT', username, response.get('bearer', ''))
		case '422':
			logger.info(response.get('detail', ''))
			raise ValueError(response.get('message', ''))
		case '401':
			logger.info(response.get('detail', ''))
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



async def connect(uri: str, username: str):
	output = {'status': 1000}
	try:
		async with websockets.connect(uri) as socket, asyncio.TaskGroup() as tg:
			logger.info('Trying to run client.')

			tg.create_task(read_socket(socket))

			tg.create_task(write_socket(
				socket,
				json.dumps(
					{"Authorization": f"Bearer {keyring.get_password('Messenger-JWT', username)}"}
				))
			)
			logger.info('Client is running')
	except* EOFError:
		output = {'status': 1000}

	except* ConnectionClosed as eg:
		for e in eg.exceptions:
			if isinstance(e, ConnectionClosed) and e.code != 1000:
				output = {'status': e.code, 'detail': e.reason}

	return output



async def read_socket(websocket):
	logger.debug("Started to reading socket!")

	try:
		async for message in websocket:
			print(message)

	except websockets.ConnectionClosed as e:
		if e.code in (1008, 1003):
			logger.debug('Invalid auth data. Restarting with password')
			raise websockets.exceptions.ConnectionClosed(*e.args)



async def write_socket(websocket, first_message: str | None = None):
	logger.debug("Started to writing in socket!")
	if first_message:
		await websocket.send(first_message)
	while True:
		message = await asyncio.to_thread(input)
		if message == "exit":
			raise EOFError

		await websocket.send(message)

if __name__ == '__main__':
	asyncio.run(main())
