from types import SimpleNamespace

DEEPGRAM = SimpleNamespace(
    **{
        'listen_endpoint': 'wss://api.deepgram.com/v1/listen',
        'numerals': 'false',
        'punctuate': 'false',
    }
)
