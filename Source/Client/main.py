import asyncio
import json

import aiofiles
import aiohttp
import keyring


async def init():
	conf = await read_config()
	if conf.get('username', '') == '':
		conf['username'] = input("Введите имя пользователя: ")
	if conf.get('server', '') == '':
		conf['server'] = 'localhost'
	if conf.get('ws-port', '') == '':
		conf['ws-port'] = 9801
	if conf.get('api-port', '') == '':
		conf['api-port'] = 8080
	if conf.get('jwt', '') == '':
		auth = await refresh(
				conf.get('server', ''),
				conf.get('username', ''),
				keyring.get_password('NeoMessenger-Refresh', conf.get('username', ''))
		)
		conf['jwt'] = auth.get('refresh_token', '')
		print(auth)

	username = conf.get('username', '')
	host = conf.get('server', '')
	ws_port = conf.get('ws-port', '')
	api_port = conf.get('api-port', '')
	jwt = conf.get('jwt', '')
	refresh_token = keyring.get_password('NeoMessenger-Refresh', conf.get('username', ''))

	keyring.set_password("NeoMessenger-JWT", username, response.get('bearer', ''))
	keyring.set_password("NeoMessenger-Refresh", username, response.get('refresh_token', ''))

async def read_config():
	async with aiofiles.open('config.json') as file:
		config_raw = await file.read()

		try:
			config = json.loads(config_raw)
		except json.JSONDecodeError:
			return {}

		return config

# ! НИКОГДА не вызывать перед read_config(), если не нужно полностью перезаписывать конфиг
# ! ВСЕГДА ждать окончания чтения, чтобы избежать гонки
async def write_config(cfg: dict):
	async with aiofiles.open('config.json', 'w') as file:

		try:
			config_raw = json.dumps(cfg)
			await file.write(config_raw)

		except (json.JSONDecodeError):
			return False

		return True

async def refresh(host: str, username: str, refresh_token: str | None) -> dict:
	if not (host and username and refresh_token):
		return {}
	async with aiohttp.ClientSession() as session:
		request = await session.post(host, json={"username": username, "refresh_token": refresh_token})
		response = await request.json()
		return response

async def login(host: str, username: str, password: str):
	async with aiohttp.ClientSession() as session:
		request = await session.post(host, json={"username": username, "password": password})
		response = await request.json()
		return response

async def main():



if __name__ == "__main__":
	asyncio.run(init())
	asyncio.run(main())
