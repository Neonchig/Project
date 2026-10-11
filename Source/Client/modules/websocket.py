
import asyncio
import json

import websockets
from websockets.exceptions import InvalidStatus


class WebsocketClient:
	"""Class for using websocket"""
	def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
		"""
		`base_url` - URL in format ws(s?)://host:port
		"""
		self._headers = headers
		self._base_url = base_url
		self._ws: websockets.ClientConnection | None = None

	@property
	def _websocket(self):
		if self._ws is None:
			raise RuntimeError('Client is not commected')
		else:
			return self._ws

	@property
	def base_url(self):
		return self._base_url

	async def __aenter__(self):
		self._ws = await websockets.connect(self._base_url, additional_headers = self._headers)
		return self

	async def __aexit__(self, *exc):
		await self._websocket.close()


	async def sender(self, inp: asyncio.Queue):
		while True:
			await self._websocket.send(await inp.get())

	async def reader(self, output: asyncio.Queue):
		async for message in self._websocket:
			await output.put(message)

	# ====================================================== #
	# Тестовые функции, работают исключительно для терминала #
	# ====================================================== #

	async def printer(self, output: asyncio.Queue):
		while True:
			print(await output.get())

	async def inputer(self, inp: asyncio.Queue):
		while True:
			await inp.put(await asyncio.to_thread(input))

async def main(bearer: str = ''):
	inp = asyncio.Queue()
	out = asyncio.Queue()
	try:
		async with WebsocketClient('ws://192.168.1.143:9801', {'Authorization': f'Bearer {bearer}'}) as session:
			tasks = [
				asyncio.create_task(session.reader(out)),
				asyncio.create_task(session.printer(out)),
				asyncio.create_task(session.sender(inp)),
				asyncio.create_task(session.inputer(inp))
			]

			done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

			for t in pending:
				t.cancel()

			for t in done:
				t.result()
	except EOFError as e:
		print('closed by user')
	except InvalidStatus as e:
		print(e.response.status_code)


if __name__ == "__main__":
	asyncio.run(main())
