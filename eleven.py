import audioop
import io
import numpy as np
from dotenv import load_dotenv
from elevenlabs import generate, play
from pydub import AudioSegment

from config import ELEVEN

load_dotenv()

async def eleven_handler(transcript_queue, audio_queue):
    print('eleven_handler started')
    while True:
        transcript = await transcript_queue.get()
        print(f'generating audio for {transcript}')
        raw_audio = generate(
            text=transcript,
            model=ELEVEN.model,
            voice=ELEVEN.voice
        )

        chunk_ulaw = wav_to_mulaw(raw_audio)
        audio_queue.put_nowait(chunk_ulaw)

def wav_to_mulaw(input_audio):
    # Load the audio file
    audio = AudioSegment.from_file_using_temporary_files(io.BytesIO(input_audio))
    # Convert to 8kHz sample rate
    # audio = audio.set_frame_rate(8000)
    # audio = audio.set_channels(1).set_sample_width(2)
    chunk_8khz, _ = audioop.ratecv(audio.raw_data, audio.sample_width, 1, audio.frame_rate, 8000, None)
    # μ-law conversion
    chunk_ulaw = audioop.lin2ulaw(chunk_8khz, 2)
    return chunk_ulaw
