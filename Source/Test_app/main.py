import asyncio
import copy
import json
import sys

import requests
import websockets
from websockets.exceptions import ConnectionClosed


def register_user(username: str | None = None, password: str | None = None, email: str | None = None):

	if username is None:
		username = input('Введите username: ')
	if password is None:
		password = input('Введите password: ')
	if email is None:
		email = input('Введите email: ')

	req = requests.request('POST', 'http://localhost:8080/register', json = {"username": username, "password": password, "email": email})
	resp = req.text

	print(resp)


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

async def ws_connect(token: str):
	uri = "ws://localhost:9801"
	if not token:
		return "connection_closed"

	return_status = "working"

	async with websockets.connect(uri) as websocket:
		try:
			async with asyncio.TaskGroup() as tg:
				tg.create_task(write_socket(websocket, json.dumps({"Authorization": f"Bearer {token}"})))
				tg.create_task(read_socket(websocket))
		except* ConnectionClosed:
			return_status = "connection_closed"
		except* EOFError:
			return_status = "self_closed_connection"

	return return_status


def con_chain_imit(jwt_flag = True, refresh_flag = True, creds_flag = True, input_flag = False, *args, debug: bool = False):
	with open('properties', 'r+') as file:

		data = json.load(file)
		modified_data = copy.deepcopy(data)

		if debug_flag:
			print(f"jwt: {data.get('jwt')}\nrefresh: {data.get('refresh_token')}\nusername: {data.get('username')}")

		output = asyncio.run(ws_connect(data.get('jwt', '') if jwt_flag else ''))

		if output == "connection_closed":
			print("jwt невалиден, переход к refresh token")

			if not(input_flag):
				username = data.get('username', '')
				refresh_token = data.get('refresh_token')
			else:
				username = input('Введите username: ')
				refresh_token = input('Введите refresh token: ')

			refresh = requests.request('POST', 'http://localhost:8080/refresh', json = {"username": username, "refresh_token": refresh_token})
			refresh_data = json.loads(refresh.text)

			if debug_flag:
				print(f"refresh info:\n\tresponse: {refresh_data}\n\t(username, token): ({username}, {refresh_token})\n\n")

			if ((int(refresh_data.get('status')) < 400) and refresh_flag):
				modified_data['jwt'] = refresh_data.get('bearer')
				modified_data['refresh_token'] = refresh_data.get('refresh_token')

				file.truncate(0)
				file.seek(0)
				file.write(json.dumps(modified_data))


			else:
				print("refresh token невалиден, переход к аутентификации")

				if not(input_flag):
					password = data.get('password', '')
				else:
					password = input('Введите пароль: ')

				login = requests.request('POST', 'http://localhost:8080/login', json = {"username": username, "password": password})
				login_data = json.loads(login.text)

				if ((login_data.get('status', '') < 400) and creds_flag):

					modified_data['jwt'] = login_data.get('bearer', '')
					modified_data['refresh_token'] = login_data.get('refresh_token')


					file.truncate(0)
					file.seek(0)
					file.write(json.dumps(modified_data))

				else:
					print('Учетные данные невалидны, отказ в подключении')
					return


			if debug_flag:
				print(f"new refresh: {modified_data.get('refresh_token', '')}\n\n")
				print(f"new jwt: {modified_data.get('jwt', '')}\n\n")

			asyncio.run(ws_connect(modified_data.get('jwt', '')))

def user_login(username: str | None = None, password: str | None = None):
	if not(username):
		username = input()
	if not(password):
		password = input()

	login = requests.request('POST', 'http://localhost:8080/login', json = {"username": username, "password": password})
	login_data = json.loads(login.text)

	if (login_data.get('status', '') > 400):
		print('User not found')
		return

	asyncio.run(ws_connect(login_data.get('bearer', '')))


if __name__ == "__main__":
	debug_flag = False
	while True:
		choice = int(input(f"МЕНЮ ТЕСТОВОГО КЛИЕНТА:\n0. Выход\n1. Имитация цепочки логина (стандарт)\n2. Имитация цепочки логина (без начального jwt)\n3. Имитация цепочки логина (без начального jwt и refresh_token)\n4. Имитация цепочки логина (без начальных данных, гарантированный отказ в подключении)\n5. Регистрация пользователя\n6. Логин по учетным данным\n7. Переключить режим отладки ({"ВКЛ" if debug_flag else "ВЫКЛ"})\n>>> "))
		match choice:
			case 0:
				sys.exit()
			case 1:
				con_chain_imit(debug=debug_flag)
			case 2:
				con_chain_imit(False, debug=debug_flag)
			case 3:
				con_chain_imit(False, False, debug=debug_flag)
			case 4:
				con_chain_imit(False, False, False, debug=debug_flag)
			case 5:
				register_user()
			case 6:
				user_login()
			case 7:
				debug_flag = not(debug_flag)
