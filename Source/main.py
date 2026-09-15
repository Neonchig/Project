import asyncio
from Backend.api.main import api_serve
from Backend.socket.socket import socket_serve

async def main():
    await asyncio.gather(socket_serve(), api_serve())

if __name__ == "__main__":
    asyncio.run(main())