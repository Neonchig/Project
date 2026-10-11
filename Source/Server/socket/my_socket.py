import asyncio
import json
from http import HTTPStatus
from json import JSONDecodeError

from jwt.exceptions import DecodeError
from websockets.asyncio.server import serve

from Source.Server.auth.token import validate_user
from Source.Server.database.database import (
	clear_unsent,
	get_group_by_name,
	get_unsent,
	get_users_in_group,
	move_to_unsent,
)

pipe = asyncio.Queue()
connected = {}

async def process_request(conn, request) -> int | None:

	if "Authorization" not in request.headers:
		return conn.respond(HTTPStatus.UNAUTHORIZED, 'No "Authorization" field\n')

	auth = request.headers.get("Authorization", "").split()
	try:
		match auth[0].lower():
			case 'bearer':
				user_info = validate_user(auth[1])
			case _:
				return conn.respond(HTTPStatus.UNAUTHORIZED, 'Invalid authorization scheme. Only bearer supported')
	except IndexError:
		return conn.respond(HTTPStatus.UNAUTHORIZED, 'Invalid authorization scheme. Only bearer supported')


	if user_info.get('status') != 200:
		return conn.respond(HTTPStatus.UNAUTHORIZED, user_info.get('detail'))

	await pipe.put(user_info)

	return None

async def handler(websocket):

	user_info = await pipe.get()
	connected[user_info.get('sub')] = websocket
	for m in await get_unsent(user_info.get('sub', '')):
		await websocket.send(m)

	await clear_unsent(user_info.get('sub'))

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
								await move_to_unsent(request.get('message', ''), user_info.get('sub', ''), request.get('to', ''))
						else:
							await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': "Incorrect 'to' field"}))
					case "group_message":
						group_name = request.get("group_name", "")
						if group_name:
							to = (await get_group_by_name(group_name))[1]
							if to:
								users_to = await get_users_in_group(to)
								websockets_to = [connected.get(i, None) for i in users_to]
								websockets_to.remove(connected.get(user_info.get('sub')))
								if websockets_to:
									for i in websockets_to:
										if i: await i.send(json.dumps({"from": user_info.get('sub'), "message": request.get('message', '')}))
								else:
									pass
							else:
								await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': "No such group"}))
						else:
							await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': "Group name must be provided"}))

async def socket_serve():
	async with serve(handler, "0.0.0.0", 9801, process_request=process_request) as server: # type: ignore
		await server.serve_forever()
