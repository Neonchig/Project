import asyncio

from Source.Server.api.api import api_serve  # Port - 8080
from Source.Server.socket.socket import socket_serve  # Port - 9801


async def main():
    await asyncio.gather(socket_serve(), api_serve())

if __name__ == "__main__":
    asyncio.run(main())
