import json
from typing import Any

import aiohttp
import keyring


class Authentication:

	def __init__(self, session: aiohttp.ClientSession, base_url: str):
		self._session = session
		self._base_url = base_url



	async def __async_post_request(self, path: str, additional_headers: dict[str, str], body: dict[str, Any], **kwargs):
		"""Sends request on base_url wuth givn path"""

		request = await self._session.post(
			url = f"{self._base_url}{path}",
			headers = additional_headers,
			json = body,
			**kwargs
		)

		return request



	async def __register(self, username: str, password: str, email: str | None = None):

		request = await self.__async_post_request("/register", {}, {"username": username, "password": password, "email": (email if email else None)})

		json_response = await request.json()

		match request.status:
			case 201:
				output = {
					"status": 201,
					"bearer": json_response.get('bearer', ''),
					'refresh_token': json_response.get('response_token', '')
				}

			case _:
				output = {
					"status": request.status,
					'detail': json_response.get('detail', 'Internal server error')
				}

		return output



	async def register(self, username: str, password: str, email: str | None = None):
		response = await self.__register(username, password, email)
		keyring.set_password(
			'Messenger-JWT', username,
			response.get('bearer', '')
		)
		keyring.set_password(
			'Messenger-Refresh', username,
			response.get('refresh_token', '')
		)
		return response



	async def __refresh(self, username: str, refresh_token: str):

		request = await self.__async_post_request("/refresh", {}, {'username': username, 'refresh_token': refresh_token})

		json_response = await request.json()

		match request.status:
			case 200:
				output = {
					"status": 200,
					"bearer": json_response.get('bearer', ''),
					'refresh_token': json_response.get('refresh_token', '')
				}

			case _:
				output = {
					"status": request.status,
					'detail': json_response.get('detail', 'Internal server error')
				}

		return output



	async def refresh(self, username: str, refresh_token: str | None):
		if not(refresh_token): refresh_token = ''
		response = await self.__refresh(username, refresh_token)
		keyring.set_password(
			'Messenger-JWT', username.lower(),
			response.get('bearer', '')
		)
		keyring.set_password(
			'Messenger-Refresh', username.lower(),
			response.get('refresh_token', '')
		)
		return response


	async def __login(self, username: str, password: str):

		request = await self.__async_post_request("/login", {}, {"username": username, "password": password})

		json_response = await request.json()

		match request.status:

			case 200:
				output = {
					"status": 200,
					"bearer": json_response.get('bearer'),
					"refresh_token": json_response.get('refresh_token')
				}

			case _:
				output = {
					"status": request.status,
					'detail': json_response.get('detail', 'Internal server error')
				}

		return output

	async def login(self, username: str, password: str):
		response = await self.__login(username, password)
		keyring.set_password(
			'Messenger-JWT', username.lower(),
			response.get('bearer', '')
		)
		keyring.set_password(
			'Messenger-Refresh', username.lower(),
			response.get('refresh_token', '')
		)
		return response
