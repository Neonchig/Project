import asyncio
from getpass import getpass
from pathlib import Path
import sys

import aiohttp
import keyring
from keyring.credentials import os
from modules.interface import ConsoleApp
from modules.websocket import WebsocketClient
from modules.requests import Authentication
from websockets.exceptions import InvalidStatus

from modules.config import read_config


async def join_socket(iteration: int, config: dict, inp: asyncio.Queue, out: asyncio.Queue, headers: dict[str, str] | None = None):
	if not(headers): headers = {}
	try:
		match iteration:
			case 0:
				pass

			case 1:
				async with aiohttp.ClientSession() as session:
					username = config.get('username', '').lower()
					refresh_token = config.get('refresh')

					url = \
					f"{'https' if config.get('ssl') else 'http'}" + "://" + \
					str(config.get('server', 'localhost')) + ":" + \
					str(config.get('api-port', '8080'))

					updated = await Authentication(session, url).refresh(username, refresh_token)

				if updated.get('status') != 200:
					print(updated)
					print(refresh_token)
					return {'run_flag': True}

				headers['Authorization'] = f"Bearer {updated.get('bearer')}"

			case _:
				async with aiohttp.ClientSession() as session:
					username = config.get('username', '')
					await out.put(getpass("Введите пароль\n>>> "))

					url = \
					f"{'https' if config.get('ssl') else 'http'}" + "://" +\
					str(config.get('server', 'localhost')) + ":" +\
					str(config.get('api-port', '8080'))

					updated = await Authentication(session, url).login(
						username,
						await out.get()
					)

					if updated.get('status') != 200:
						return {'run_flag': True}

					headers['Authorization'] = f"Bearer {updated.get('bearer')}"

		ws_url = \
		f"{'wss' if config.get('ssl') else 'ws'}" + "://" + \
		str(config.get('server', 'localhost')) + ":" + \
		str(config.get('ws-port', '9801'))

		async with WebsocketClient(ws_url, headers) as session:
			tasks = [
				asyncio.create_task(session.sender(inp)),
				asyncio.create_task(session.reader(out))
			]

			done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

			for t in pending:
				t.cancel()
			for t in done:
				t.result()

			return {'status': 500, 'detail': 'Internal server error', 'run_flag': False}

	except EOFError:
		return {'status': 1000, 'detail': 'Closed by user', "run_flag": False}
	except InvalidStatus as e:
		return {'status': e.response.status_code, 'detail': e.response.body, "run_flag": True}


async def main(inp: asyncio.Queue, out: asyncio.Queue):
	# Важные переменные
	run_flag = True
	iteration = 0
	main_path = Path(os.path.abspath(__file__) + "/../config.json").resolve()

	# Работа с конфигом
	config = await read_config(main_path)
	username = config.get('username', '').lower()
	config['bearer'] = keyring.get_password('Messenger-JWT', username)
	config['refresh'] = keyring.get_password('Messenger-Refresh', username)

	# Основной запуск
	while run_flag:

		response = await join_socket(
			iteration = iteration,
			headers = {'Authorization': f'Bearer {config.get("bearer", "")}'},
			config = config,
			inp = inp, out = out
		)

		run_flag = response.get('run_flag', run_flag)
		iteration += 1

if __name__ == '__main__':
	# Объясвление переменных
	inp = asyncio.Queue()
	out = asyncio.Queue()
	tasks = set()
	loop = asyncio.new_event_loop()

	fut = asyncio.run_coroutine_threadsafe(main(inp, out), loop)
	tasks.add(fut)
	ConsoleApp([
		{'name': 'Test_group1', 'id': 'gr_101233', 'image': 'test_avatar.jpg'},
		{'name': 'Test_PM_1', 'id': 'pm_42353', 'image': 'test_avatar_2.jpg'},
		{'name': 'Test_PM_2', 'id': 'pm_12334', 'image': None}
	], inp = inp, out = out).run()
