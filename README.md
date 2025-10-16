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

# NLP Project

This repository contains a small FastAPI backend that exposes NLP analysis and translation endpoints. The README below is written for frontend engineers who need to integrate with the backend: it covers endpoints, request/response schemas, examples, running locally, TypeScript types, error handling, and recommended integration practices.

## Quick start (developer)

1. Create & activate a virtual environment (optional but recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies. The project uses `pyproject.toml`; you can install with your normal tooling. Example using pip and the project's editable install:

```powershell
pip install -e .
# or use the project's uv helper if present:
uv sync
```

3. Install spaCy models required by the backend (the code will raise a clear RuntimeError if missing):

```powershell
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_trf
```

4. Run the API server locally:

```powershell
uvicorn main:app --reload
```

By default the server listens on http://localhost:9000 (see `main.py`).

## OpenAPI / Interactive docs

FastAPI exposes interactive API docs when the server is running:

- Swagger UI: http://localhost:9000/docs
- ReDoc: http://localhost:9000/redoc
- OpenAPI JSON: http://localhost:9000/openapi.json

Use the OpenAPI JSON to auto-generate clients or TypeScript types (tools: openapi-generator, openapi-typescript, Swagger Codegen).

## Endpoints (complete reference)

Base URL for local development: http://localhost:9000

1) GET /
- Purpose: Basic health / sanity endpoint
- Response 200 JSON: { "message": "NLP Analysis API is running" }

2) POST /pos
- Purpose: Run POS (Part-of-Speech) tokenization on English text using spaCy TRF model for higher accuracy.
- Request (application/json): { "text": "string" }
- Response 200 (application/json) matches model `POSAnalysisOut`:
    - tokens: TokenOut[]
        - TokenOut: { text: string, pos: string, tag: string, lemma: string, dep: string, start: number, end: number }
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 500 Internal Server Error — spaCy TRF model not installed or other runtime error

3) POST /ner
- Purpose: Run Named Entity Recognition on English text using spaCy small model for faster processing.
- Request (application/json): { "text": "string" }
- Response 200 (application/json) matches model `NERAnalysisOut`:
    - entities: EntityOut[]
        - EntityOut: { text: string, label: string, start: number, end: number }
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 500 Internal Server Error — spaCy small model not installed or other runtime error

4) POST /analyze (deprecated - kept for backward compatibility)
- Purpose: Run both POS tokenization and NER on English text (combines /pos and /ner).
- Request (application/json): { "text": "string" }
- Response 200 (application/json) matches model `NLPAnalysisOut`:
    - tokens: TokenOut[]
        - TokenOut: { text: string, pos: string, tag: string, lemma: string, dep: string, start: number, end: number }
    - entities: EntityOut[]
        - EntityOut: { text: string, label: string, start: number, end: number }
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 500 Internal Server Error — spaCy model not installed or other runtime error
- Note: For better performance, use /pos and /ner separately when you only need one type of analysis.

5) POST /translate
- Purpose: Translate input text to a target language using `googletrans`.
- Request (application/json): { "text": "string", "target_language": "es" }
    - `target_language` must be a supported language code (see /languages)
- Response 200 (application/json) matches `TranslationOut`:
    - { original_text: string, translated_text: string, source_language: string, target_language: string, confidence: number }
- Error cases:
    - 400 Bad Request — invalid input (empty text, unsupported language)
    - 500 Internal Server Error — translation service failure or network error

6) GET /languages
- Purpose: Return mapping of supported language codes to names from googletrans
- Response example: { "en": "english", "es": "spanish", ... }

## Request / response examples

POS tagging example (curl):

```bash
curl -X POST http://localhost:9000/pos \
    -H "Content-Type: application/json" \
    -d '{"text":"Apple is buying a startup in the U.K."}'
```

NER example (curl):

```bash
curl -X POST http://localhost:9000/ner \
    -H "Content-Type: application/json" \
    -d '{"text":"Apple is buying a startup in the U.K."}'
```

Combined analysis example (fetch in browser / frontend):

```javascript
const res = await fetch('http://localhost:9000/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'Apple is buying a startup in the U.K.' }),
});
const data = await res.json();
console.log(data); // Contains both tokens and entities
```

Translate example (fetch in browser / frontend):

```javascript
const res = await fetch('http://localhost:9000/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'Hello world', target_language: 'es' }),
});
if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Translation failed');
}
const data = await res.json();
console.log(data);
```

GET languages example:

```javascript
const res = await fetch('http://localhost:9000/languages');
const languages = await res.json();
```

## Error handling guidance for frontend

- Check HTTP status codes before parsing JSON. FastAPI returns JSON error responses with `detail` fields for `HTTPException` and validation errors.
- For 422 validation errors, the response contains a structured description of which fields failed validation.
- For 5xx errors, show a friendly generic message and include an option to retry.

## CORS and authentication

- Current backend has CORS configured for http://localhost:3000. If your frontend runs on a different origin, update the `allow_origins` list in `main.py`.
- For production, add authentication (JWT/OAuth/session) and restrict CORS to trusted origins.

## TypeScript interfaces (copy-paste for frontend)

```ts
export interface TokenOut {
  text: string;
  pos: string;
  tag: string;
  lemma: string;
  dep: string;
  start: number;
  end: number;
}

export interface EntityOut {
  text: string;
  label: string;
  start: number;
  end: number;
}

export interface POSAnalysisOut {
  tokens: TokenOut[];
}

export interface NERAnalysisOut {
  entities: EntityOut[];
}

export interface NLPAnalysisOut {
  tokens: TokenOut[];
  entities: EntityOut[];
}

export interface TranslationOut {
  original_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
  confidence: number;
}
```

## Integration recommendations

- Use `/pos` when you only need tokenization and part-of-speech tagging (more efficient).
- Use `/ner` when you only need named entity recognition (faster, uses smaller model).
- Use `/analyze` only when you need both POS and NER results in a single call.
- Use the OpenAPI (`/openapi.json`) to auto-generate clients or typed models.
- Debounce / throttle calls to analysis endpoints (e.g., 300-500ms) when integrating with text inputs.
- For long texts, consider implementing optimistic UI patterns as NLP analysis can be CPU-bound.
