import asyncio
import sys
import websockets

from client import client_handler
from state import State
from twilio import twilio_handler

state = State()

async def router(websocket, path):
    if path == '/client':
        print('client connection incoming')
        await client_handler(websocket, state)
    elif path == '/twilio':
        print('twilio connection incoming')
        await twilio_handler(websocket, state)

def main():
    server = websockets.serve(router, 'localhost', 5000)

    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    sys.exit(main() or 0)
