from types import SimpleNamespace

DEEPGRAM = SimpleNamespace(
    **{
        'confidence_threshold': 0.5,
        'endpointing': '500',
        'listen_endpoint': 'wss://api.deepgram.com/v1/listen',
        'model': 'phonecall',
        'smart_format': 'true',
        'tier': 'nova'
    }
)

ELEVEN = SimpleNamespace(
    **{
        'model': 'eleven_monolingual_v1',
        'voice': 'Bella'
    }
)
