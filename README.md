# NLP Analysis API - Backend Documentation

# NLP Analysis API - Backend Documentation

A comprehensive FastAPI backend service for Natural Language Processing (NLP) analysis, providing endpoints for POS tagging, Named Entity Recognition, Dependency Parsing, CFG Parsing, Semantic Role Labeling, and Translation.

## Table of Contents
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [CORS Configuration](#cors-configuration)
- [Frontend Integration Guide](#frontend-integration-guide)

---

## Technology Stack

### Core Framework
- **FastAPI** (>=0.115.0) - Modern, fast web framework for building APIs
- **Uvicorn** (>=0.30.0) - ASGI server for running the FastAPI application
- **Pydantic** (>=2.7.0) - Data validation using Python type annotations

### NLP Libraries
- **spaCy** (>=3.7.0) - Industrial-strength NLP library
  - `en_core_web_sm` - Small English model for NER (13 MB)
  - `en_core_web_trf` - Transformer-based English model for high-accuracy POS tagging (438 MB)
- **NLTK** (>=3.9.2) - Natural Language Toolkit for CFG parsing

### AI & Translation
- **Google Generative AI** (>=1.45.0) - Gemini AI for advanced CFG parsing and semantic analysis
- **googletrans** - Google Translate API wrapper for text translation

### Development Dependencies
- **pytest** (>=8.0.0) - Testing framework
- **httpx** (>=0.27.0) - HTTP client for testing
- **python-dotenv** - Environment variable management

### Python Version
- **Python 3.10+** required

---

## Project Structure

```
nlp-project/
├── main.py                 # FastAPI application and endpoint definitions
├── models.py              # Pydantic models for request/response schemas
├── nlp_engine.py          # Core NLP analysis functions (spaCy, NLTK, Gemini)
├── translation_engine.py  # Translation functionality
├── pyproject.toml         # Project dependencies and configuration
├── .env                   # Environment variables (not in git)
├── README.md              # This file
└── __pycache__/          # Python cache files
```

---

## Installation & Setup

### 1. Create Virtual Environment (Recommended)

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

**Using uv (recommended):**
```powershell
uv sync
```

**Using pip:**
```powershell
pip install -e .
```

### 3. Download spaCy Language Models

```powershell
# Small model for NER (faster, 13 MB)
python -m spacy download en_core_web_sm

# Transformer model for POS tagging (more accurate, 438 MB)
python -m spacy download en_core_web_trf
```

**Alternative installation via URLs:**
```powershell
uv add https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz
uv add https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0.tar.gz
```

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```env
# Gemini AI API Key (required for /cfg-gemini and /semantic endpoints)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your Gemini API key:**
- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create a new API key
- Copy and paste it into your `.env` file

**Note:** If `GEMINI_API_KEY` is not set, the `/cfg-gemini` and `/semantic` endpoints will return error messages.

---

## Running the Server

### Development Mode (with auto-reload)

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 9000
```

### Production Mode

```powershell
uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
```

### Access Points

- **API Base URL:** http://localhost:9000
- **Interactive API Docs (Swagger UI):** http://localhost:9000/docs
- **Alternative API Docs (ReDoc):** http://localhost:9000/redoc
- **OpenAPI JSON Schema:** http://localhost:9000/openapi.json

---

## API Endpoints

### 1. GET `/`
**Health Check Endpoint**

Returns a simple status message to verify the API is running.

**Response:**
```json
{
  "message": "NLP Analysis API is running"
}
```

**Status Codes:**
- `200 OK` - API is running

---

### 2. POST `/pos`
**Part-of-Speech (POS) Tagging**

Analyzes text and returns detailed POS tagging using spaCy's transformer-based model (`en_core_web_trf`) for high accuracy.

**Request Body:**
```json
{
  "text": "The quick brown fox jumps over the lazy dog."
}
```

**Response Model:** `POSAnalysisOut`
```json
{
  "tokens": [
    {
      "text": "The",
      "pos": "DET",
      "tag": "DT",
      "lemma": "the",
      "dep": "det",
      "start": 0,
      "end": 3
    },
    {
      "text": "quick",
      "pos": "ADJ",
      "tag": "JJ",
      "lemma": "quick",
      "dep": "amod",
      "start": 4,
      "end": 9
    }
    // ... more tokens
  ]
}
```

**Token Fields:**
- `text` (string) - The token text
- `pos` (string) - Universal POS tag (e.g., NOUN, VERB, ADJ, DET)
- `tag` (string) - Fine-grained POS tag (e.g., NN, VBD, JJ)
- `lemma` (string) - Base form of the word
- `dep` (string) - Syntactic dependency relation
- `start` (int) - Character offset start position
- `end` (int) - Character offset end position

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - spaCy model not installed

**curl Example:**
```bash
curl -X POST http://localhost:9000/pos \
  -H "Content-Type: application/json" \
  -d '{"text":"Apple is buying a startup in the U.K."}'
```

---

### 3. POST `/ner`
**Named Entity Recognition (NER)**

Identifies and classifies named entities in text using spaCy's small model (`en_core_web_sm`) for fast processing.

**Request Body:**
```json
{
  "text": "Apple is buying a startup in the U.K."
}
```

**Response Model:** `NERAnalysisOut`
```json
{
  "entities": [
    {
      "text": "Apple",
      "label": "ORG",
      "start": 0,
      "end": 5
    },
    {
      "text": "U.K.",
      "label": "GPE",
      "start": 33,
      "end": 37
    }
  ]
}
```

**Entity Fields:**
- `text` (string) - The entity text
- `label` (string) - Entity type (ORG, PERSON, GPE, DATE, MONEY, etc.)
- `start` (int) - Character offset start position
- `end` (int) - Character offset end position

**Common Entity Labels:**
- `PERSON` - People, including fictional characters
- `ORG` - Companies, agencies, institutions
- `GPE` - Countries, cities, states
- `LOC` - Non-GPE locations, mountain ranges, bodies of water
- `DATE` - Absolute or relative dates or periods
- `TIME` - Times smaller than a day
- `MONEY` - Monetary values, including unit
- `QUANTITY` - Measurements
- `ORDINAL` - "first", "second", etc.
- `CARDINAL` - Numerals that do not fall under another type

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - spaCy model not installed

**curl Example:**
```bash
curl -X POST http://localhost:9000/ner \
  -H "Content-Type: application/json" \
  -d '{"text":"Elon Musk founded SpaceX in California in 2002."}'
```

---

### 4. POST `/dependency`
**Dependency Parsing**

Analyzes the grammatical structure of a sentence and returns a visual SVG diagram showing word dependencies.

**Request Body:**
```json
{
  "text": "The cat sits on the mat."
}
```

**Response Model:** `DependencyParseOut`
```json
{
  "sentence": "The cat sits on the mat.",
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\"...></svg>",
  "dependencies": [
    {
      "token": "cat",
      "dep": "nsubj",
      "head": "sits",
      "pos": "NOUN",
      "children": ["The"]
    },
    {
      "token": "sits",
      "dep": "ROOT",
      "head": "sits",
      "pos": "VERB",
      "children": ["cat", "on", "."]
    }
    // ... more dependencies
  ]
}
```

**Dependency Fields:**
- `token` (string) - The token text
- `dep` (string) - Dependency relation (e.g., nsubj, dobj, prep, ROOT)
- `head` (string) - The syntactic head of this token
- `pos` (string) - Part-of-speech tag
- `children` (string[]) - List of dependent tokens

**SVG Field:**
- Contains complete SVG markup that can be directly rendered in HTML using `innerHTML`

**Common Dependency Relations:**
- `nsubj` - Nominal subject
- `dobj` - Direct object
- `prep` - Preposition
- `pobj` - Object of preposition
- `ROOT` - Root of the sentence
- `det` - Determiner
- `amod` - Adjectival modifier

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - spaCy model not installed

**curl Example:**
```bash
curl -X POST http://localhost:9000/dependency \
  -H "Content-Type: application/json" \
  -d '{"text":"She quickly ate the delicious cake."}'
```

---

### 5. POST `/cfg-gemini`
**Context-Free Grammar (CFG) Parsing with AI**

Uses Gemini AI to generate a CFG parse tree in Mermaid diagram format. Works with any sentence without lexicon limitations.

**Request Body:**
```json
{
  "text": "The astronaut explores the distant galaxy."
}
```

**Response Model:** `GeminiCFGParseOut`
```json
{
  "sentence": "The astronaut explores the distant galaxy.",
  "mermaid_code": "graph TD\n    S1[\"S\"]\n    NP1[\"NP\"]\n    Det1[\"Det: the\"]\n    N1[\"N: astronaut\"]\n    VP1[\"VP\"]\n    V1[\"V: explores\"]\n    NP2[\"NP\"]\n    Det2[\"Det: the\"]\n    Adj1[\"Adj: distant\"]\n    N2[\"N: galaxy\"]\n    \n    S1 --> NP1\n    S1 --> VP1\n    NP1 --> Det1\n    NP1 --> N1\n    VP1 --> V1\n    VP1 --> NP2\n    NP2 --> Det2\n    NP2 --> Adj1\n    NP2 --> N2",
  "explanation": "The sentence follows the structure S → NP VP, where the subject NP is 'the astronaut' and the VP contains the verb 'explores' with an object NP 'the distant galaxy'."
}
```

**Response Fields:**
- `sentence` (string) - The input sentence
- `mermaid_code` (string) - Mermaid flowchart code for rendering the parse tree
- `explanation` (string) - Human-readable explanation of the parse structure

**Phrase Labels:**
- `S` - Sentence
- `NP` - Noun Phrase
- `VP` - Verb Phrase
- `PP` - Prepositional Phrase
- `Det` - Determiner
- `N` - Noun
- `V` - Verb
- `Adj` - Adjective
- `Adv` - Adverb
- `P` - Preposition

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - Gemini API error or missing API key

**Dependencies:**
- Requires `GEMINI_API_KEY` environment variable
- Internet connection for Gemini API access

**curl Example:**
```bash
curl -X POST http://localhost:9000/cfg-gemini \
  -H "Content-Type: application/json" \
  -d '{"text":"The robot painted a beautiful picture."}'
```

---

### 6. POST `/ai-help`
**AI-Powered Analysis Helper**

Provides AI-generated insights and explanations about text using Gemini AI.

**Request Body:**
```json
{
  "text": "Your text for analysis"
}
```

**Response:**
Dynamic response based on Gemini AI analysis.

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - Gemini API error

**Dependencies:**
- Requires `GEMINI_API_KEY` environment variable

**curl Example:**
```bash
curl -X POST http://localhost:9000/ai-help \
  -H "Content-Type: application/json" \
  -d '{"text":"Explain this sentence structure"}'
```

---

### 7. POST `/semantic`
**Semantic Role Labeling (SRL)**

Analyzes predicate-argument structures to identify "who did what to whom, with what, where, when" relationships using Gemini AI.

**Request Body:**
```json
{
  "text": "John bought a car from a dealer yesterday."
}
```

**Response Model:** `SemanticRoleOut`
```json
{
  "sentence": "John bought a car from a dealer yesterday.",
  "mermaid_code": "graph LR\n    John[\"John\"]\n    bought[\"bought (Predicate)\"]\n    car[\"a car\"]\n    dealer[\"a dealer\"]\n    yesterday[\"yesterday\"]\n    \n    John -->|Agent| bought\n    bought -->|Theme| car\n    bought -->|Source| dealer\n    bought -->|Time| yesterday",
  "roles": [
    {
      "word": "John",
      "role": "Agent",
      "predicate": "bought"
    },
    {
      "word": "a car",
      "role": "Theme",
      "predicate": "bought"
    },
    {
      "word": "a dealer",
      "role": "Source",
      "predicate": "bought"
    },
    {
      "word": "yesterday",
      "role": "Time",
      "predicate": "bought"
    }
  ],
  "explanation": "John is the Agent performing the action 'bought'. The Theme (what was bought) is 'a car'. The Source (from whom) is 'a dealer', and the Time (when) is 'yesterday'."
}
```

**Response Fields:**
- `sentence` (string) - The input sentence
- `mermaid_code` (string) - Mermaid graph showing semantic relationships
- `roles` (SemanticRole[]) - Array of identified semantic roles
- `explanation` (string) - Explanation of the semantic structure

**SemanticRole Fields:**
- `word` (string) - The word/phrase playing this role
- `role` (string) - The semantic role type
- `predicate` (string) - The action/verb this role relates to

**Common Semantic Roles:**
- `Agent (ARG0)` - Who/what performs the action
- `Patient/Theme (ARG1)` - Who/what is affected by the action
- `Recipient (ARG2)` - To whom/for whom
- `Instrument (ARG-MNR)` - With what tool/means
- `Location (ARG-LOC)` - Where
- `Time (ARG-TMP)` - When
- `Source (ARG-DIR)` - From where/whom
- `Goal (ARG-GOL)` - To where
- `Cause (ARG-CAU)` - Why/because of what
- `Beneficiary (ARG-BNF)` - For whom/what

**Use Cases:**
- Question answering systems
- Information extraction
- Event detection
- Natural language understanding
- Command parsing for chatbots

**Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - Gemini API error or missing API key

**Dependencies:**
- Requires `GEMINI_API_KEY` environment variable
- Internet connection for Gemini API access

**curl Example:**
```bash
curl -X POST http://localhost:9000/semantic \
  -H "Content-Type: application/json" \
  -d '{"text":"She sent the package to her friend using FedEx."}'
```

---

### 8. POST `/translate`
**Text Translation**

Translates text from one language to another using Google Translate API.

**Request Body:**
```json
{
  "text": "Hello world",
  "target_language": "es"
}
```

**Request Fields:**
- `text` (string) - Text to translate (required)
- `target_language` (string) - Target language code (required, e.g., "es", "fr", "de")

**Response Model:** `TranslationOut`
```json
{
  "original_text": "Hello world",
  "translated_text": "Hola mundo",
  "source_language": "en",
  "target_language": "es",
  "confidence": 1.0
}
```

**Response Fields:**
- `original_text` (string) - The input text
- `translated_text` (string) - The translated result
- `source_language` (string) - Detected source language code
- `target_language` (string) - Target language code used
- `confidence` (float) - Translation confidence score (0.0 to 1.0)

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid input (empty text, unsupported language)
- `422 Unprocessable Entity` - Invalid request body format
- `500 Internal Server Error` - Translation service failure

**curl Example:**
```bash
curl -X POST http://localhost:9000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"Good morning","target_language":"fr"}'
```

---

### 9. GET `/languages`
**Supported Languages**

Returns a dictionary of all supported language codes and their names for translation.

**Response:**
```json
{
  "af": "afrikaans",
  "sq": "albanian",
  "ar": "arabic",
  "en": "english",
  "es": "spanish",
  "fr": "french",
  "de": "german",
  "hi": "hindi",
  "ja": "japanese",
  "ko": "korean",
  "pt": "portuguese",
  "ru": "russian",
  "zh-cn": "chinese (simplified)",
  "zh-tw": "chinese (traditional)"
  // ... 100+ more languages
}
```

**Status Codes:**
- `200 OK` - Success

**curl Example:**
```bash
curl -X GET http://localhost:9000/languages
```

---

## Data Models

### Input Models

#### TextInput
```typescript
{
  text: string  // Required
}
```

#### TranslationInput
```typescript
{
  text: string              // Required
  target_language: string   // Required (2-letter language code)
}
```

### Output Models

#### TokenOut
```typescript
{
  text: string      // Token text
  pos: string       // Universal POS tag
  tag: string       // Fine-grained POS tag
  lemma: string     // Base form
  dep: string       // Dependency relation
  start: number     // Character offset start
  end: number       // Character offset end
}
```

#### EntityOut
```typescript
{
  text: string      // Entity text
  label: string     // Entity type
  start: number     // Character offset start
  end: number       // Character offset end
}
```

#### DependencyOut
```typescript
{
  token: string         // Token text
  dep: string           // Dependency relation
  head: string          // Head token
  pos: string           // POS tag
  children: string[]    // Dependent tokens
}
```

#### SemanticRole
```typescript
{
  word: string          // Word/phrase
  role: string          // Semantic role type
  predicate: string     // Related action/verb
}
```

#### POSAnalysisOut
```typescript
{
  tokens: TokenOut[]
}
```

#### NERAnalysisOut
```typescript
{
  entities: EntityOut[]
}
```

#### DependencyParseOut
```typescript
{
  sentence: string
  svg: string
  dependencies: DependencyOut[]
}
```

#### GeminiCFGParseOut
```typescript
{
  sentence: string
  mermaid_code: string
  explanation: string
}
```

#### SemanticRoleOut
```typescript
{
  sentence: string
  mermaid_code: string
  roles: SemanticRole[]
  explanation: string
}
```

#### TranslationOut
```typescript
{
  original_text: string
  translated_text: string
  source_language: string
  target_language: string
  confidence: number
}
```

---

## Error Handling

### Error Response Format

All errors return JSON with a `detail` field:

```json
{
  "detail": "Error description here"
}
```

### HTTP Status Codes

- **200 OK** - Request succeeded
- **400 Bad Request** - Client error (invalid input, validation failed)
- **422 Unprocessable Entity** - Request body format invalid or missing required fields
- **500 Internal Server Error** - Server error (missing dependencies, API failures)

### Common Error Scenarios

1. **Missing spaCy Models (500)**
```json
{
  "detail": "spaCy TRF model 'en_core_web_trf' is not installed. Run: python -m spacy download en_core_web_trf"
}
```

2. **Missing Gemini API Key (500)**
```json
{
  "detail": "Error generating CFG parse with Gemini: API key not found"
}
```

3. **Invalid Translation Language (400)**
```json
{
  "detail": "Unsupported language code: xyz"
}
```

4. **Empty Text Input (400)**
```json
{
  "detail": "Text cannot be empty"
}
```

5. **Malformed JSON (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## CORS Configuration

### Current Settings

The API is configured with CORS middleware to allow cross-origin requests.

**Allowed Origins:**
- `http://localhost:3000`

**Configuration in `main.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Modifying CORS Settings

To allow requests from different origins, edit `main.py`:

```python
# Allow multiple specific origins
allow_origins=["http://localhost:3000", "http://localhost:8080", "https://yourdomain.com"]

# Allow all origins (NOT recommended for production)
allow_origins=["*"]
```

---

## Frontend Integration Guide

### Fetching from the API

#### Basic POST Request
```javascript
const response = await fetch('http://localhost:9000/pos', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Your text here'
  })
});

const data = await response.json();
```

#### With Error Handling
```javascript
try {
  const response = await fetch('http://localhost:9000/ner', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'Apple Inc. is in California.' })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  const data = await response.json();
  console.log(data.entities);
} catch (error) {
  console.error('Error:', error.message);
}
```

### Rendering SVG Diagrams

For `/dependency` endpoint:

```javascript
const res = await fetch('http://localhost:9000/dependency', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'The cat sat on the mat.' })
});

const data = await res.json();

// Inject SVG directly into DOM
document.getElementById('diagram').innerHTML = data.svg;
```

### Rendering Mermaid Diagrams

For `/cfg-gemini` and `/semantic` endpoints:

**Include Mermaid.js in HTML:**
```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

**Render Mermaid Code:**
```javascript
const res = await fetch('http://localhost:9000/cfg-gemini', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'The student reads the book.' })
});

const data = await res.json();

// Method 1: Direct injection
document.getElementById('diagram').innerHTML = `
  <pre class="mermaid">
    ${data.mermaid_code}
  </pre>
`;
mermaid.init();

// Method 2: Using mermaid.render()
const { svg } = await mermaid.render('my-diagram', data.mermaid_code);
document.getElementById('diagram').innerHTML = svg;
```

### Translation Example
```javascript
const res = await fetch('http://localhost:9000/translate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello world',
    target_language: 'es'
  })
});

const data = await res.json();
console.log(data.translated_text); // "Hola mundo"
```

### Semantic Role Analysis Example
```javascript
const res = await fetch('http://localhost:9000/semantic', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'John bought a car from a dealer yesterday.'
  })
});

const data = await res.json();

// Access structured role data
data.roles.forEach(role => {
  console.log(`${role.word} is the ${role.role} of ${role.predicate}`);
});

// Render semantic graph
document.getElementById('graph').innerHTML = `
  <pre class="mermaid">${data.mermaid_code}</pre>
`;
mermaid.init();
```

---

## Best Practices

### Performance Optimization

1. **Debounce API Calls**: For text inputs, debounce requests to avoid overwhelming the server
```javascript
const debounce = (func, wait) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

const analyzeText = debounce(async (text) => {
  // API call here
}, 300); // 300ms delay
```

2. **Use Appropriate Endpoints**: 
   - Use `/pos` only when you need POS tagging
   - Use `/ner` only when you need entity recognition
   - Don't call both if you don't need both analyses

3. **Cache Results**: Cache API responses for identical inputs

### Security Considerations

1. **Never Expose API Keys in Frontend**: Keep `GEMINI_API_KEY` on the backend only
2. **Validate Input Length**: Add client-side validation to limit text length
3. **Rate Limiting**: Implement rate limiting on the frontend to prevent abuse
4. **HTTPS in Production**: Always use HTTPS in production environments

### Error Handling

1. **Check HTTP Status**: Always check `response.ok` before parsing JSON
2. **Handle Network Errors**: Wrap API calls in try-catch blocks
3. **Display User-Friendly Messages**: Don't expose raw error messages to end users
4. **Implement Retries**: For transient errors (500), implement exponential backoff

---

## Troubleshooting

### Server Won't Start

**Issue:** `RuntimeError: spaCy model 'en_core_web_trf' is not installed`

**Solution:**
```powershell
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
```

---

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```powershell
pip install -e .
# or
uv sync
```

---

**Issue:** Gemini endpoints return errors

**Solution:**
1. Check `.env` file exists with `GEMINI_API_KEY`
2. Verify API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Ensure you have internet connectivity

---

### CORS Errors in Browser

**Issue:** `Access to fetch at 'http://localhost:9000/pos' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solution:** Add your frontend origin to the CORS middleware in `main.py`:
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

---

### Slow Response Times

**Issue:** `/pos` endpoint is slow

**Cause:** The transformer model (`en_core_web_trf`) is computationally expensive

**Solutions:**
1. Use shorter text inputs
2. Implement request debouncing on frontend
3. Consider using a smaller model for less critical use cases
4. Deploy with more CPU resources or GPU acceleration

---

## Development Tools

### Interactive API Documentation

Access Swagger UI at http://localhost:9000/docs to:
- View all endpoints
- Test endpoints directly in browser
- See request/response schemas
- Generate code samples

### Testing with curl

All endpoints can be tested with curl. Examples are provided in each endpoint section.

### Testing with Postman

1. Import OpenAPI schema from http://localhost:9000/openapi.json
2. Create a collection from the schema
3. Test all endpoints with Postman's interface

---

## Production Deployment Checklist

- [ ] Set `GEMINI_API_KEY` in production environment
- [ ] Update CORS `allow_origins` to production frontend URLs
- [ ] Use HTTPS for all communications
- [ ] Set up proper logging (not included in this version)
- [ ] Implement rate limiting
- [ ] Set up monitoring and health checks
- [ ] Use a production ASGI server (uvicorn with --workers)
- [ ] Configure firewall rules
- [ ] Implement authentication if needed
- [ ] Set up automated backups of any stored data
- [ ] Document API versioning strategy

---

## API Versioning

**Current Version:** 0.1.0

Version is defined in `main.py`:
```python
app = FastAPI(title="NLP Analysis API", version="0.1.0")
```

---

## License & Credits

This project uses the following open-source libraries:
- FastAPI - MIT License
- spaCy - MIT License
- NLTK - Apache 2.0 License
- Google Generative AI - Google Terms of Service

---

## Support & Contact

For issues, questions, or feature requests:
- Check the troubleshooting section
- Review the interactive API docs at `/docs`
- Refer to the technology stack documentation

---

**Last Updated:** October 2025

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

2a. (Optional) Install NLTK for CFG parsing endpoint:

```powershell
pip install nltk
```

2b. (Optional) Set up Gemini API key for AI-powered CFG parsing:

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

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

4) POST /dependency
- Purpose: Analyze dependency parsing for a single sentence and return a visual diagram with detailed dependency relationships.
- Request (application/json): { "text": "string" }
  - Note: Works best with a single sentence. For multiple sentences, only the first will be properly visualized.
- Response 200 (application/json) matches model `DependencyParseOut`:
    - sentence: string (the input sentence)
    - svg: string (SVG markup of the dependency diagram - can be rendered directly in HTML)
    - dependencies: DependencyOut[]
        - DependencyOut: { token: string, dep: string, head: string, pos: string, children: string[] }
        - `dep`: dependency relation label (e.g., "nsubj", "dobj", "prep")
        - `head`: the syntactic head token
        - `children`: list of dependent tokens
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 500 Internal Server Error — spaCy TRF model not installed or other runtime error

5) POST /constituency
- Purpose: Analyze constituency parsing for a single sentence and return a tree structure showing phrase-level organization.
- Request (application/json): { "text": "string" }
  - Note: Works best with a single sentence.
- Response 200 (application/json) matches model `ConstituencyParseOut`:
    - sentence: string (the input sentence)
    - svg: string (SVG visualization of the parse tree)
    - text_tree: string (text representation of the constituency tree with phrase labels like NP, VP, etc.)
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 500 Internal Server Error — spaCy TRF model not installed or other runtime error

6) POST /cfg
- Purpose: Parse sentence using formal Context-Free Grammar (CFG) rules with NLTK.
- Request (application/json): { "text": "string" }
  - Note: Uses a predefined English grammar. Works best with simple, grammatically correct sentences.
- Response 200 (application/json) matches model `CFGParseOut`:
    - sentence: string (the input sentence)
    - trees: string[] (array of all possible parse trees found - may be multiple if sentence is ambiguous)
    - grammar_rules: string (the CFG rules used for parsing)
    - success: boolean (true if parsing succeeded, false otherwise)
    - error_message: string (empty if success=true, otherwise contains error details)
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 200 with success=false — sentence cannot be parsed with the given grammar (words not in lexicon or invalid structure)
- Note: Requires NLTK to be installed (`pip install nltk`)

7) POST /cfg-gemini
- Purpose: Generate CFG parse tree in Mermaid diagram format using Gemini AI.
- Request (application/json): { "text": "string" }
  - Note: Uses AI to analyze any sentence - no lexicon limitations like /cfg endpoint.
- Response 200 (application/json) matches model `GeminiCFGParseOut`:
    - sentence: string (the input sentence)
    - mermaid_code: string (Mermaid flowchart code for the CFG parse tree)
    - explanation: string (brief explanation of the parse structure)
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 500 Internal Server Error — Gemini API error or configuration issue
- Note: Requires `GEMINI_API_KEY` environment variable to be set
- The `mermaid_code` can be rendered using Mermaid.js in your frontend

8) POST /semantic
- Purpose: Perform Semantic Role Labeling (SRL) to show predicate-argument structures using Gemini AI.
- Request (application/json): { "text": "string" }
  - Note: Identifies "who did what to whom, with what, where, when" relationships.
- Response 200 (application/json) matches model `SemanticRoleOut`:
    - sentence: string (the input sentence)
    - mermaid_code: string (Mermaid graph code showing semantic roles as directed graph)
    - roles: SemanticRole[] (array of semantic roles)
        - SemanticRole: { word: string, role: string, predicate: string }
        - Common roles: Agent, Patient/Theme, Recipient, Instrument, Location, Time, Source, Goal
    - explanation: string (explanation of the semantic structure)
- Error cases:
    - 422 Unprocessable Entity — request JSON missing `text` or invalid
    - 500 Internal Server Error — Gemini API error or configuration issue
- Note: Requires `GEMINI_API_KEY` environment variable to be set
- Use cases: Question answering, information extraction, event detection, understanding "who did what"

9) POST /analyze (deprecated - kept for backward compatibility)
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

10) POST /translate
- Purpose: Translate input text to a target language using `googletrans`.
- Request (application/json): { "text": "string", "target_language": "es" }
    - `target_language` must be a supported language code (see /languages)
- Response 200 (application/json) matches `TranslationOut`:
    - { original_text: string, translated_text: string, source_language: string, target_language: string, confidence: number }
- Error cases:
    - 400 Bad Request — invalid input (empty text, unsupported language)
    - 500 Internal Server Error — translation service failure or network error

11) GET /languages
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

Dependency parsing example (curl):

```bash
curl -X POST http://localhost:9000/dependency \
    -H "Content-Type: application/json" \
    -d '{"text":"The quick brown fox jumps over the lazy dog."}'
```

Dependency parsing example (fetch in browser / frontend):

```javascript
const res = await fetch('http://localhost:9000/dependency', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'The cat sat on the mat.' }),
});
const data = await res.json();
// Render the SVG diagram in your HTML
document.getElementById('diagram').innerHTML = data.svg;
// Access dependency details
console.log(data.dependencies);
```

Constituency parsing example (curl):

```bash
curl -X POST http://localhost:9000/constituency \
    -H "Content-Type: application/json" \
    -d '{"text":"The quick brown fox jumps over the lazy dog."}'
```

Constituency parsing example (fetch in browser / frontend):

```javascript
const res = await fetch('http://localhost:9000/constituency', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'The student reads the book.' }),
});
const data = await res.json();
// Render the SVG tree in your HTML
document.getElementById('tree').innerHTML = data.svg;
// Display text tree structure
console.log(data.text_tree);
// Example output:
// (S
//   (NP The student)
//   (VP reads)
//   (NP the book)
// )
```

CFG parsing example (curl):

```bash
curl -X POST http://localhost:9000/cfg \
    -H "Content-Type: application/json" \
    -d '{"text":"The cat sits on the mat."}'
```

CFG parsing example (fetch in browser / frontend):

```javascript
const res = await fetch('http://localhost:9000/cfg', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'The cat sits on the mat.' }),
});
const data = await res.json();

if (data.success) {
    console.log('Parse successful!');
    console.log('Number of possible parses:', data.trees.length);
    data.trees.forEach((tree, index) => {
        console.log(`Parse ${index + 1}:`, tree);
    });
    // Example output:
    // Parse 1: (S (NP (Det the) (N cat)) (VP (V sits) (PP (P on) (NP (Det the) (N mat)))))
} else {
    console.log('Parse failed:', data.error_message);
}

// View grammar rules used
console.log('Grammar rules:', data.grammar_rules);
```

CFG Gemini parsing example (curl):

```bash
curl -X POST http://localhost:9000/cfg-gemini \
    -H "Content-Type: application/json" \
    -d '{"text":"The quick brown fox jumps over the lazy dog."}'
```

CFG Gemini parsing example (fetch in browser / frontend):

```javascript
const res = await fetch('http://localhost:9000/cfg-gemini', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'The astronaut explores the distant galaxy.' }),
});
const data = await res.json();

console.log('Mermaid code:', data.mermaid_code);
console.log('Explanation:', data.explanation);

// Render using Mermaid.js in your HTML
// Option 1: Using mermaid.render()
const { svg } = await mermaid.render('cfg-diagram', data.mermaid_code);
document.getElementById('diagram-container').innerHTML = svg;

// Option 2: Using mermaid class
document.getElementById('diagram-container').innerHTML = `
    <pre class="mermaid">
        ${data.mermaid_code}
    </pre>
`;
mermaid.init();
```

Semantic role analysis example (curl):

```bash
curl -X POST http://localhost:9000/semantic \
    -H "Content-Type: application/json" \
    -d '{"text":"John bought a car from a dealer yesterday."}'
```

Semantic role analysis example (fetch in browser / frontend):

```javascript
const res = await fetch('http://localhost:9000/semantic', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'John bought a car from a dealer yesterday.' }),
});
const data = await res.json();

console.log('Semantic roles:', data.roles);
// Example output:
// [
//   { word: "John", role: "Agent", predicate: "bought" },
//   { word: "a car", role: "Theme", predicate: "bought" },
//   { word: "a dealer", role: "Source", predicate: "bought" },
//   { word: "yesterday", role: "Time", predicate: "bought" }
// ]

console.log('Explanation:', data.explanation);

// Render the semantic role graph using Mermaid
document.getElementById('semantic-graph').innerHTML = `
    <pre class="mermaid">
        ${data.mermaid_code}
    </pre>
`;
mermaid.init();

// Or programmatically access roles
data.roles.forEach(role => {
    console.log(`${role.word} is the ${role.role} of ${role.predicate}`);
});
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

## Understanding Semantic Roles (for /semantic endpoint)

Semantic Role Labeling (SRL) identifies the predicate-argument structure of sentences - answering "who did what to whom, with what, where, when, why?"

**Common semantic roles:**
- **Agent (ARG0)**: Who/what performs the action (e.g., "John" in "John bought a car")
- **Patient/Theme (ARG1)**: Who/what is affected by the action (e.g., "a car" in "John bought a car")
- **Recipient (ARG2)**: To whom/for whom (e.g., "Mary" in "John gave a book to Mary")
- **Instrument (ARG-MNR)**: With what tool/means (e.g., "a hammer" in "He broke it with a hammer")
- **Location (ARG-LOC)**: Where (e.g., "the park" in "They met in the park")
- **Time (ARG-TMP)**: When (e.g., "yesterday" in "It happened yesterday")
- **Source (ARG-DIR)**: From where/whom (e.g., "the dealer" in "bought from the dealer")
- **Goal (ARG-GOL)**: To where (e.g., "London" in "traveled to London")

**Use cases:**
- Question Answering: Extract answers to "who", "what", "where", "when", "how" questions
- Information Extraction: Identify events, participants, and relationships in text
- Text Summarization: Understand key actors and actions
- Command Understanding: Parse user intents in chatbots/voice assistants

## Rendering Mermaid diagrams (for /cfg-gemini and /semantic endpoints)

To render Mermaid diagrams in your frontend, include Mermaid.js:

```html
<!-- Add to your HTML head -->
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

Then render the diagram:

```javascript
// Method 1: Direct injection with mermaid class
document.getElementById('diagram').innerHTML = `
  <pre class="mermaid">
    ${data.mermaid_code}
  </pre>
`;
mermaid.init();

// Method 2: Using mermaid.render() for more control
const { svg } = await mermaid.render('my-diagram', data.mermaid_code);
document.getElementById('diagram').innerHTML = svg;
```

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

export interface DependencyOut {
  token: string;
  dep: string;
  head: string;
  pos: string;
  children: string[];
}

export interface DependencyParseOut {
  sentence: string;
  svg: string;
  dependencies: DependencyOut[];
}

export interface ConstituencyParseOut {
  sentence: string;
  svg: string;
  text_tree: string;
}

export interface CFGParseOut {
  sentence: string;
  trees: string[];
  grammar_rules: string;
  success: boolean;
  error_message: string;
}

export interface GeminiCFGParseOut {
  sentence: string;
  mermaid_code: string;
  explanation: string;
}

export interface SemanticRole {
  word: string;
  role: string;
  predicate: string;
}

export interface SemanticRoleOut {
  sentence: string;
  mermaid_code: string;
  roles: SemanticRole[];
  explanation: string;
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
- Use `/dependency` when you need to visualize or analyze grammatical structure and relationships between words in a sentence.
  - The SVG output can be directly injected into your HTML using `innerHTML` or rendered in an `<img>` tag with data URI.
  - Use the `dependencies` array for programmatic analysis of sentence structure.
- Use `/constituency` when you need phrase-level syntactic structure (noun phrases, verb phrases, etc.).
  - Shows hierarchical organization of sentences into constituents.
  - The `text_tree` field provides a readable tree structure with phrase labels (NP, VP, S, etc.).
  - Useful for understanding sentence structure, parsing grammar, or building syntax-aware applications.
- Use `/cfg` for formal grammar-based parsing with explicit Context-Free Grammar rules.
  - Best for educational purposes, grammar checking, or when you need to verify if a sentence follows specific grammatical rules.
  - Returns all possible parse trees (handles ambiguous sentences).
  - Note: Limited to words in the predefined lexicon - extend the grammar rules in `nlp_engine.py` as needed.
  - Check the `success` field to determine if parsing succeeded.
- Use `/cfg-gemini` for AI-powered CFG parsing with visual Mermaid diagrams.
  - Works with any sentence - no lexicon limitations.
  - Generates beautiful, renderable Mermaid flowchart diagrams.
  - Best for visualizing parse trees in educational apps or demos.
  - Requires Gemini API key (set `GEMINI_API_KEY` environment variable).
  - Uses Gemini's structured output with Pydantic for reliable JSON responses.
- Use `/semantic` for semantic role labeling (SRL) - understanding "who did what to whom".
  - Identifies predicate-argument structures (Agent, Patient, Instrument, Location, Time, etc.).
  - Returns both a visual Mermaid graph and structured role data.
  - Perfect for: question answering systems, information extraction, event detection, natural language understanding.
  - Example use case: Extract actors and actions from news articles or user commands.
  - The `roles` array provides programmatic access to all semantic relationships.
- Use `/analyze` only when you need both POS and NER results in a single call.
- Use the OpenAPI (`/openapi.json`) to auto-generate clients or typed models.
- Debounce / throttle calls to analysis endpoints (e.g., 300-500ms) when integrating with text inputs.
- For long texts, consider implementing optimistic UI patterns as NLP analysis can be CPU-bound.
