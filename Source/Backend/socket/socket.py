import json
from http import HTTPStatus
from json import JSONDecodeError

from jwt.exceptions import DecodeError
from websockets.asyncio.server import serve

from Source.Backend.auth.token import validate_user
from Source.Backend.database.database import clear_unsent, get_group_by_name, get_unsent, get_users_in_group

connected_idle = set()
connected = {}

async def handler(websocket):


	connected_idle.add(websocket)
	# for i, j in websocket.request.headers.raw_items():
	# 	await websocket.send(f"{i}: {j}")

	auth = {}
	auth_raw = await websocket.recv()
	try:
		auth = json.loads(auth_raw)
	except JSONDecodeError:
		await websocket.send('Incorrect auth, JSONDecoderError, 1')
		await websocket.close(code = 4002, reason = "Incorrect auth")

	if not('Authorization' in auth):
		await websocket.send('Incorrect auth, Authorization not in message')
		await websocket.close(code = 4002, reason = "Incorrect auth")

	auth = auth.get('Authorization', '').split()

	if len(auth) != 2:
		await websocket.send(f'Incorrect auth, too many or not enough parts. {auth}')
		await websocket.close(code = 4002, reason = "Incorrect auth")

	user_info = {}

	try:
		user_info = validate_user(auth[1])
	except (DecodeError, IndexError):
		await websocket.send('Incorrect auth')
		await websocket.close(code = 4002, reason = "Incorrect auth")

	if not(user_info):
		await websocket.send('Incorrect auth')
		await websocket.close(code = 4002, reason = "Incorrect auth")

	connected_idle.remove(websocket)
	connected[user_info.get('sub', '')] = websocket

	for message in await get_unsent(user_info.get('sub', '')):
		await websocket.send(message)
		await clear_unsent(user_info.get('sub', ''))

	async for m in websocket:
		m = m.strip()
		if m == "ping":
			await websocket.send('pong')
		elif m == 'exit':
			return
		elif m == "whoami":
			await websocket.send(user_info.get('sub'))
		else:
			request = {}
			try:
				request = json.loads(str(m))
			except json.JSONDecodeError:
				await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': 'Incorrect type field'}))

			request_type = request.get("type", "")
			if request_type:
				match request_type:
					case "message":
						to = request.get("to", "").lower()
						if to:
							websocket_to = connected.get(to, "")
							if websocket_to:
								await websocket_to.send(json.dumps({"from": user_info.get('sub', ''), "message": request.get('message', '')}))
							else:
								await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': 'User is not connected'}))
						else:
							await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': "Incorrect 'to' field"}))
					case "group_message":
						group_name = request.get("grp_name", "")
						if group_name:
							to = (await get_group_by_name(group_name))[1]
							if to:
								users_to = await get_users_in_group(to)
								websockets_to = [connected.get(i, None) for i in users_to]
								websockets_to.remove(connected.get(user_info.get('sub')))
								if websockets_to:
									for i in websockets_to:
										if i: await i.send(json.dumps({"sender": user_info.get('sub'), "message": request.get('message', '')}))
								else:
									pass
							else:
								await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': "No such group"}))
						else:
							await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': "Group name must be provided"}))

async def socket_serve():
	async with serve(handler, "localhost", 9801) as server: # type: ignore
		await server.serve_forever()
