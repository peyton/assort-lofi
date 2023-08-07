from types import SimpleNamespace

DEEPGRAM = SimpleNamespace(
    **{
        'confidence_threshold': 0.6,
        'listen_endpoint': 'wss://api.deepgram.com/v1/listen',
        'numerals': 'false',
        'punctuate': 'false',
    }
)
