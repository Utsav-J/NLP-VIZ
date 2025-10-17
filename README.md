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
