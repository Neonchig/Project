import json
from http import HTTPStatus

from jwt.exceptions import DecodeError
from websockets.asyncio.server import serve
from websockets.datastructures import Headers
from websockets.http11 import Response

from Source.Backend.auth.token import validate_user

connected = set()


async def process_request(conn, request) -> Response | None:

	body = json.dumps({ "error": "auth_fail", "message": "Authorization failed" })
	body = body.encode('utf-8')

	if "Authorization" not in request.headers:
		return Response(HTTPStatus.UNAUTHORIZED, "Unauthorized", Headers({"ContentType": "application/json"}, body = body))

	auth = request.headers.get("Authorization", "").split()
	try:
		if not(len(auth) == 2 and auth[0].lower() == "bearer" and auth[1]):
			return Response(HTTPStatus.UNAUTHORIZED, "Unauthorized", Headers({"ContentType": "application/json"}, body = body))
	except IndexError:
		return Response(HTTPStatus.UNAUTHORIZED, "Unauthorized", Headers({"ContentType": "application/json"}, body = body))
	try:
		if not(validate_user(auth[1])):
			return Response(HTTPStatus.UNAUTHORIZED, "Unauthorized", Headers({"ContentType": "application/json"}, body = body))
	except DecodeError:
		return Response(HTTPStatus.UNAUTHORIZED, "Unauthorized", Headers({"ContentType": "application/json"}, body = body))

	return None

async def handler(websocket):


	connected.add(websocket)
	# for i, j in websocket.request.headers.raw_items():
	# 	await websocket.send(f"{i}: {j}")

	async for m in websocket:
		m = m.strip()
		if m == "ping":
			await websocket.send("pong")
		elif m == 'exit':
			return
		else:
			try:
				request = json.loads(str(m))
			except json.JSONDecodeError:
				await websocket.send(json.dumps({'status': HTTPStatus.UNPROCESSABLE_CONTENT, 'message': 'Incorrect "type" field'}))

			# request_type = request.get("type", "")
			# if request_type:
			# 	match request_type:
			# 		case "pers_mess":
			# 			pass # TODO
			# 		case "grp_mess":
			# 			pass # TODO

async def socket_serve():
	async with serve(handler, "localhost", 9801, process_request=process_request) as server: # type: ignore
		await server.serve_forever()
