import json

import aiohttp
from websockets.asyncio.server import serve

connected = set()

async def handler(websocket):

	connected.add(websocket)

	for i, j in websocket.request.headers.raw_items():
		await websocket.send(f"{i}: {j}")

	async for m in websocket:
		m = m.strip()
		if m == "ping":
			await websocket.send("pong")
		else:
			try:
				mess = json.loads(m)

				match mess['type']:

					case 'send':
						pass

					case 'login':
						pass #TODO

					case 'register':
						aiohttp.request("POST", "http://localhost:8000", data={})

					case _:
						await websocket.send('{"code": 418; "details": "incorrect "type" field"}')

			except json.decoder.JSONDecodeError:
				print("str")

async def socket_serve():
	async with serve(handler, "localhost", 9801) as server:
		await server.serve_forever()
