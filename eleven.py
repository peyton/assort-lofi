import asyncio
from dotenv import load_dotenv
from elevenlabs import generate
from pydub import AudioSegment

from config import ELEVEN

load_dotenv()

async def eleven_handler(transcript_queue, audio_queue):
    print('eleven_handler started')
    while True:
        transcript = await transcript_queue.get()
        generate_task = asyncio.create_task(
            generate(
                text=transcript,
                model=ELEVEN.model,
                voice=ELEVEN.voice
            )
        )
        raw_audio = await generate_task
        outbound_audio = AudioSegment(raw_audio, sample_width=1, frame_rate=8000, channels=1)
        audio_queue.put_nowait(outbound_audio)
