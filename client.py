import asyncio
import json

async def client_handler(client_ws, state):
    client_queue = asyncio.Queue()

    # first tell the client all active calls
    await client_ws.send(json.dumps(list(state.subscribers.keys())))

    # then recieve from the client which call they would like to subscribe to
    # and add our client's queue to the subscriber list for that call
    try:
        # you may want to parse a proper json input here
        # instead of grabbing the entire message as the callsid verbatim
        callsid = await client_ws.recv()
        callsid = callsid.strip()
        if callsid in state.subscribers:
            state.subscribers[callsid].append(client_queue)
        else:
            await client_ws.close()
    except:
        await client_ws.close()

    async def client_sender(client_ws):
        while True:
            message = await client_queue.get()
            if message == 'close':
                break
            try:
                await client_ws.send(message)
            except:
                # if there was an error, remove this client queue
                state.subscribers[callsid].remove(client_queue)
                break

    await asyncio.wait([
        asyncio.ensure_future(client_sender(client_ws)),
    ])

    await client_ws.close()
