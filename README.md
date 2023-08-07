# Assort LoFi Demo

## Running

1. Populate `.env` using keys from `.env.example`.

2. Create a Twilio TwiML bin from the contents of `twimlbin.xml`.

3. Run:

```sh
python app.py
```

## Polish

#### Overall
- optimize latency
- instrumentation & logging
- state management
- de-spaghettify and pipeline processing
- failure handling

#### Deepgram
- send keepalive and closestream
- employ keywords (provider name, pt name, etc)
- store transcript & audio

#### Testing
- unit tests
- regression/perf tests
