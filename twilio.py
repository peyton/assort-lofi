import asyncio
import base64
import json
from pydub import AudioSegment

from deepgram import deepgram_connect, deepgram_sender, deepgram_receiver

async def twilio_handler(twilio_ws, state):
    audio_queue = asyncio.Queue()
    callsid_queue = asyncio.Queue()
    response_queue = asyncio.Queue()

    async with deepgram_connect() as deepgram_ws:
        async def twilio_receiver(twilio_ws):
            print('twilio_receiver started')
            # twilio sends audio data as 160 byte messages containing 20ms of audio each
            # we will buffer 20 twilio messages corresponding to 0.4 seconds of audio to improve throughput performance
            BUFFER_SIZE = 20 * 160
            # the algorithm to deal with mixing the two channels is somewhat complex
            # here we implement an algorithm which fills in silence for channels if that channel is either
            #   A) not currently streaming (e.g. the outbound channel when the inbound channel starts ringing it)
            #   B) packets are dropped (this happens, and sometimes the timestamps which come back for subsequent packets are not aligned)
            inbuffer = bytearray(b'')
            inbound_chunks_started = False
            latest_inbound_timestamp = 0
            async for message in twilio_ws:
                try:
                    data = json.loads(message)
                    if data['event'] == 'start':
                        start = data['start']
                        callsid = start['callSid']
                        print(f'>>> CALL STARTING >>>\n{data}\n<<< CALL STARTING <<<')
                        callsid_queue.put_nowait(callsid)
                    if data['event'] == 'connected':
                        print(f'>>> CALL CONNECTED >>>\n{data}\n<<< CALL CONNECTED <<<')
                        continue
                    if data['event'] == 'media':
                        media = data['media']
                        chunk = base64.b64decode(media['payload'])
                        if media['track'] == 'inbound':
                            # fills in silence if there have been dropped packets
                            if inbound_chunks_started:
                                if latest_inbound_timestamp + 20 < int(media['timestamp']):
                                    bytes_to_fill = 8 * (int(media['timestamp']) - (latest_inbound_timestamp + 20))
                                    # NOTE: 0xff is silence for mulaw audio
                                    # and there are 8 bytes per ms of data for our format (8 bit, 8000 Hz)
                                    inbuffer.extend(b'\xff' * bytes_to_fill)
                            else:
                                # make it known that inbound chunks have started arriving
                                inbound_chunks_started = True
                                latest_inbound_timestamp = int(media['timestamp'])
                            latest_inbound_timestamp = int(media['timestamp'])
                            # extend the inbound audio buffer with data
                            inbuffer.extend(chunk)
                    if data['event'] == 'stop':
                        print(f'>>> CALL STOPPING >>>\n{data}\n<<< CALL STOPPING <<<')
                        break

                    # check if our buffer is ready to send to our audio_queue (and, thus, then to deepgram)
                    while len(inbuffer) >= BUFFER_SIZE:
                        asinbound = AudioSegment(inbuffer[:BUFFER_SIZE], sample_width=1, frame_rate=8000, channels=1)

                        # sending to deepgram via the audio_queue
                        audio_queue.put_nowait(asinbound.raw_data)

                        # clearing buffers
                        inbuffer = inbuffer[BUFFER_SIZE:]
                except:
                    break

            # the async for loop will end if the ws connection from twilio dies
            # and if this happens, we should forward an empty byte to deepgram
            # to signal deepgram to send back remaining messages before closing
            audio_queue.put_nowait(b'')

        await asyncio.wait([
            asyncio.ensure_future(deepgram_sender(deepgram_ws, audio_queue)),
            asyncio.ensure_future(deepgram_receiver(deepgram_ws, state, callsid_queue)),
            asyncio.ensure_future(twilio_receiver(twilio_ws))
        ])

        await twilio_ws.close()
