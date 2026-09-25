import json
from http import HTTPStatus

from websockets.asyncio.server import serve

from Source.Backend.auth.token import validate_user

connected = set()


async def process_request(conn, request) -> int | None:

	if "Authorization" not in request.headers:
		return HTTPStatus.UNAUTHORIZED

	auth = request.headers.get("Authorization", "").split()
	try:
		if not(len(auth) == 2 and auth[0].lower() == "bearer" and auth[1]):
			return HTTPStatus.UNAUTHORIZED
	except IndexError:
		return HTTPStatus.UNAUTHORIZED

	if not(validate_user(auth[1])):
		return HTTPStatus.UNAUTHORIZED

	return None

async def handler(websocket):


	connected.add(websocket)
	# for i, j in websocket.request.headers.raw_items():
	# 	await websocket.send(f"{i}: {j}")

	async for m in websocket:
		m = m.strip()
		if m == "ping":
			await websocket.send("pong")
		else:
			try:
				request = json.loads(m)
			except json.JSONDecodeError:
				return json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': 'Incorrect "type" field'})

			request_type = request.get("type", "")
			if request_type:
				match request_type:
					case "pers_mess":
						pass # TODO
					case "grp_mess":
						pass # TODO

async def socket_serve():
	async with serve(handler, "localhost", 9801, process_request=process_request) as server:
		await server.serve_forever()
