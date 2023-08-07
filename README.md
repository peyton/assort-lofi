# Assort LoFi Demo

### Running

Populate `.env` using keys from `.env.example`, then run:

```sh
python app.py
```

### Polish

Overall:
- instrumentation & logging
- state management
- failure handling

Deepgram:
- send keepalive and closestream
- employ keywords (provider name, pt name, etc)

Testing:
- unit tests
- regression/perf tests
