## NLP Project

### Setup

1. Create and activate a virtual environment (optional but recommended)
2. Install dependencies:

```bash
uv sync
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
                    or
uv add https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0.tar.gz
uv add https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz
```

### Console script

Run the demo analyzer:

```bash
python analyze_console.py "Apple is buying a startup in the U.K."
```

### Run API

```bash
uvicorn main:app --reload
```

POST to `/analyze` with:

```json
{"text": "Apple is buying a startup in the U.K."}
```

POST to `/translate` with:

```json
{"text": "Hello world", "target_language": "es"}
```

GET `/languages` to see supported language codes.

### Test

```bash
pytest -q
```


