import datetime

import jwt
from jwt.exceptions import DecodeError

from Source.Backend.core.config import env


def token_generator(sub: str, aud: str):

	if not env['ServUUID']:
		raise UnboundLocalError('Server UUID not found in .env')

	payload = {
		"iss": env['ServUUID'],
		"sub": sub.lower(),
		"aud": aud.lower(),
		"iat": datetime.datetime.now(datetime.UTC).timestamp(),
		"exp": (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)).timestamp()
	}

	"""
	Полезная нагрузка для jwt токена = {
		iss - выдан (в этом случае UUID сервера, полезно при масштабировании, при одиночном сервере - не слишком полезное поле)
		sub - получатель (в этом случае username пользователя)
		aud - к каким функциям токену следует давать доступ, на данный момент только user
		iat - выдан (время в UTC, формат - UNIX Timestamp)
		exp - истекает (время в UTC, формат - UNIX Timestamp)
	}
	"""
	if not env['Secret']:
		raise UnboundLocalError('Secret not found in .env file')

	token = jwt.encode(payload, env['Secret'], 'HS256')

	return token

def validate_user(token: str):
	if not(env['Secret']) or not(env['ServUUID']):
		raise UnboundLocalError('Secret not found in .env file')
	try:
		data = jwt.decode(token, env['Secret'], 'HS256', audience="user")
	except DecodeError:
		raise DecodeError

	if data['iss'] != env['ServUUID']:
		raise jwt.InvalidIssuerError

	return data

if __name__ == "__main__":
	print(token_generator("Neoniche", "user"))
