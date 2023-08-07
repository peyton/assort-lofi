import json
import os
import websockets
from dotenv import load_dotenv

from config import DEEPGRAM

load_dotenv()

def deepgram_connect():
    deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
    if not deepgram_api_key:
        raise Exception("Set DEEPGRAM_API_KEY environment variable")

    extra_headers = {
        'Authorization': f'Token {deepgram_api_key}'
    }
    # deepgram_ws = websockets.connect(f'{DEEPGRAM.listen_endpoint}?encoding=mulaw&sample_rate=8000&punctuate={DEEPGRAM.punctuate}&numerals={DEEPGRAM.numerals}', extra_headers = extra_headers)
    deepgram_ws = websockets.connect(f'{DEEPGRAM.listen_endpoint}?encoding=mulaw&sample_rate=8000', extra_headers = extra_headers)


    return deepgram_ws

async def deepgram_receiver(deepgram_ws, state, callsid_queue):
    print('deepgram_receiver started')
    # we will wait until the twilio ws connection figures out the callsid
    # then we will initialize our subscribers list for this callsid
    callsid = await callsid_queue.get()
    state.subscribers[callsid] = []
    # for each final deepgram result received, forward it on to all
    # queues subscribed to the twilio callsid
    async for message in deepgram_ws:
        data = json.loads(message)
        print(message)
        if not data['is_final'] or not data['speech_final']:
            continue
        alternatives = data['channel']['alternatives']
        if not alternatives:
            continue
        if not len(alternatives):
            continue
        transcript = alternatives[0]['transcript]']
        for client in state.subscribers[callsid]:
            client.put_nowait(transcript)

    # once the twilio call is over, tell all subscribed clients to close
    # and remove the subscriber list for this callsid
    for client in state.subscribers[callsid]:
        client.put_nowait('close')

    del state.subscribers[callsid]

async def deepgram_sender(deepgram_ws, audio_queue):
    print('deepgram_sender started')
    while True:
        chunk = await audio_queue.get()
        await deepgram_ws.send(chunk)
