import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from fetcher import fetch_in_processes
from datetime import date
from aiofile import async_open
from aiopath import AsyncPath
from pathlib import Path
import json
import os

logging.basicConfig(level=logging.INFO)
# Get the directory of the current script
script_directory = Path(os.path.dirname(os.path.abspath(__file__)))
# Set the working directory to the script's directory
os.chdir(script_directory)

os.chdir("./")

AVAILABLE_COMMANDS = ['exchange']
LOGS_PATH = "./logs.txt"


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            command_splitted = message.split(' ')
            command, *rest = command_splitted
            days_range = 0

            if len(rest) >= 1:
                days_range = rest[0]

            if not command in AVAILABLE_COMMANDS:
                continue

            apath = AsyncPath(LOGS_PATH)

            if not await apath.exists():
                continue

            async with async_open(apath, 'w+') as afp:
                await afp.write(f"{date.today().strftime('%d.%m.%Y')} - {command}")

            await self.send_to_clients(json.dumps(({"loading": "true", "rates": []})))

            rates = await fetch_in_processes(int(days_range))

            await self.send_to_clients(json.dumps(({"rates": rates, "loading": "false"})))


async def main():
    server = Server()

    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
