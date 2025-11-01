# Backend Sample Code - NLP Analysis API

This document contains crucial code samples demonstrating the main features of the NLP backend, API endpoint definitions, and frontend integration patterns.

---

## 1. API Server Setup & CORS Configuration

**File: `main.py`**

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NLP Analysis API", version="0.1.0")

# CORS Configuration - Allows frontend on localhost:3000 to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Purpose:** Sets up FastAPI server with CORS middleware to enable cross-origin requests from the frontend application.

---

## 2. API Endpoints

**File: `main.py`**

### 2.1 POS Tagging Endpoint

```python
@app.post("/pos", response_model=POSAnalysisOut)
def pos_tagging(input_data: TextInput) -> POSAnalysisOut:
    """Analyze text for POS tagging only using TRF model"""
    return analyze_pos(input_data.text)
```

**Purpose:** Returns part-of-speech tags for each token in the input text using spaCy's transformer model.

### 2.2 Named Entity Recognition Endpoint

```python
@app.post("/ner", response_model=NERAnalysisOut)
def named_entity_recognition(input_data: TextInput) -> NERAnalysisOut:
    """Analyze text for Named Entity Recognition only using small model"""
    return analyze_ner(input_data.text)
```

**Purpose:** Identifies and classifies named entities (persons, organizations, locations, etc.) in text.

### 2.3 Dependency Parsing Endpoint

```python
@app.post("/dependency", response_model=DependencyParseOut)
def dependency_parse(input_data: TextInput) -> DependencyParseOut:
    """Analyze dependency parsing for a single sentence and return visual diagram"""
    return analyze_dependency(input_data.text)
```

**Purpose:** Analyzes grammatical structure and returns SVG visualization of word dependencies.

### 2.4 AI-Powered CFG Parsing Endpoint

```python
@app.post("/cfg-gemini", response_model=GeminiCFGParseOut)
def cfg_parse_gemini(input_data: TextInput) -> GeminiCFGParseOut:
    """Generate CFG parse tree in Mermaid format using Gemini AI"""
    return analyze_cfg_using_gemini(input_data.text)
```

**Purpose:** Uses Gemini AI to generate Context-Free Grammar parse trees as Mermaid diagrams.

### 2.5 Semantic Role Labeling Endpoint

```python
@app.post("/semantic", response_model=SemanticRoleOut)
def semantic_role_analysis(input_data: TextInput) -> SemanticRoleOut:
    """Analyze semantic roles (who did what to whom) using Gemini AI"""
    return analyze_semantic_roles(input_data.text)
```

**Purpose:** Identifies predicate-argument structures showing semantic relationships (Agent, Patient, Location, Time, etc.).

### 2.6 Translation Endpoint

```python
@app.post("/translate", response_model=TranslationOut)
def translate(input_data: TranslationInput) -> TranslationOut:
    try:
        return translate_text(input_data.text, input_data.target_language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Purpose:** Translates text from detected source language to target language using Google Translate.

---

## 3. Core NLP Analysis Functions

**File: `nlp_engine.py`**

### 3.1 Model Initialization (Singleton Pattern)

```python
_POS_NLP_SINGLETON: Language | None = None
_NER_NLP_SINGLETON: Language | None = None

def get_pos_nlp() -> Language:
    """Get TRF model for POS tagging (better accuracy)"""
    global _POS_NLP_SINGLETON
    if _POS_NLP_SINGLETON is None:
        _POS_NLP_SINGLETON = spacy.load("en_core_web_trf")
    return _POS_NLP_SINGLETON

def get_ner_nlp() -> Language:
    """Get small model for NER (lightweight)"""
    global _NER_NLP_SINGLETON
    if _NER_NLP_SINGLETON is None:
        _NER_NLP_SINGLETON = spacy.load("en_core_web_sm")
    return _NER_NLP_SINGLETON
```

**Purpose:** Singleton pattern ensures NLP models are loaded only once, improving performance and memory usage.

### 3.2 POS Tagging Analysis

```python
def analyze_pos(text: str) -> POSAnalysisOut:
    """Analyze text for POS tagging using TRF model"""
    pos_nlp = get_pos_nlp()
    pos_doc = pos_nlp(text)

    tokens: List[TokenOut] = []
    for tok in pos_doc:
        tokens.append(
            TokenOut(
                text=tok.text,
                pos=tok.pos_,
                tag=tok.tag_,
                lemma=tok.lemma_,
                dep=tok.dep_,
                start=tok.idx,
                end=tok.idx + len(tok.text),
            )
        )
    return POSAnalysisOut(tokens=tokens)
```

**Purpose:** Extracts tokens with their part-of-speech tags, lemmas, and dependency information.

### 3.3 Named Entity Recognition

```python
def analyze_ner(text: str) -> NERAnalysisOut:
    """Analyze text for Named Entity Recognition using small model"""
    ner_nlp = get_ner_nlp()
    ner_doc = ner_nlp(text)

    entities: List[EntityOut] = []
    for ent in ner_doc.ents:
        entities.append(
            EntityOut(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
            )
        )
    return NERAnalysisOut(entities=entities)
```

**Purpose:** Identifies named entities with their types (ORG, PERSON, GPE, etc.) and positions in text.

### 3.4 Dependency Parsing with SVG Visualization

```python
def analyze_dependency(sentence: str) -> DependencyParseOut:
    """Analyze dependency parsing for a single sentence and generate visualization"""
    from spacy import displacy
    
    nlp = get_pos_nlp()
    doc = nlp(sentence)
    
    # Generate SVG visualization using displaCy
    svg = displacy.render(doc, style="dep", jupyter=False, options={
        "compact": False,
        "bg": "#ffffff",
        "color": "#000000",
        "font": "Arial"
    })
    
    # Extract dependency information
    dependencies: List[DependencyOut] = []
    for token in doc:
        children = [child.text for child in token.children]
        dependencies.append(
            DependencyOut(
                token=token.text,
                dep=token.dep_,
                head=token.head.text,
                pos=token.pos_,
                children=children
            )
        )
    
    return DependencyParseOut(
        sentence=sentence,
        svg=svg,
        dependencies=dependencies
    )
```

**Purpose:** Generates both structured dependency data and SVG visualization diagram for sentence structure.

### 3.5 AI-Powered CFG Parsing with Gemini

```python
def analyze_cfg_using_gemini(sentence: str) -> GeminiCFGParseOut:
    """Use Gemini AI to generate a CFG parse tree in Mermaid diagram format."""
    prompt = f"""
    You are a linguistic expert specializing in Context-Free Grammar (CFG) parsing.
    Analyze the following sentence and create a CFG parse tree in Mermaid flowchart format:
    Sentence: "{sentence}"
    ...
    """
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GeminiCFGParseOut,
        }
    )
    
    result = GeminiCFGParseOut.model_validate_json(response.text)
    return result
```

**Purpose:** Uses Gemini AI with structured output to generate Mermaid-formatted parse trees for any sentence.

### 3.6 Semantic Role Labeling with Gemini

```python
def analyze_semantic_roles(sentence: str) -> SemanticRoleOut:
    """Use Gemini AI to perform semantic role labeling (SRL)"""
    prompt = f"""
    You are a linguistic expert specializing in Semantic Role Labeling (SRL).
    Analyze the following sentence and identify the semantic roles:
    Sentence: "{sentence}"
    ...
    Requirements:
    1. Generate a Mermaid graph code showing semantic roles
    2. Create a roles array listing each role with word, role type, and predicate
    ...
    """
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": SemanticRoleOut,
        }
    )
    
    result = SemanticRoleOut.model_validate_json(response.text)
    return result
```

**Purpose:** Identifies semantic roles (Agent, Patient, Location, Time, etc.) and generates visual graph showing predicate-argument relationships.

---

## 4. Translation Functions

**File: `translation_engine.py`**

### 4.1 Text Translation

```python
def translate_text(text: str, target_language: str) -> TranslationOut:
    """Translate text to target language using Google Translate"""
    if not text.strip():
        raise ValueError("Text cannot be empty")
    
    supported_langs = get_supported_languages()
    if target_language not in supported_langs:
        raise ValueError(f"Unsupported language code: {target_language}")
    
    translator = Translator()
    result = asyncio.run(translator.translate(text, dest=target_language))
    
    return TranslationOut(
        original_text=text,
        source_language=str(result.src),
        translated_text=str(result.text),
        target_language=str(result.dest),
        confidence=getattr(result, 'confidence', 0.0) or 0.0
    )
```

**Purpose:** Translates text using Google Translate API with validation and error handling.

---

## 5. Data Models

**File: `models.py`**

### 5.1 Input Models

```python
class TextInput(BaseModel):
    text: str

class TranslationInput(BaseModel):
    text: str
    target_language: str
```

**Purpose:** Pydantic models for request validation and type safety.

### 5.2 Output Models

```python
class TokenOut(BaseModel):
    text: str
    pos: str
    tag: str
    lemma: str
    dep: str
    start: int
    end: int

class EntityOut(BaseModel):
    text: str
    label: str
    start: int
    end: int

class DependencyParseOut(BaseModel):
    sentence: str
    svg: str  # SVG markup for visualization
    dependencies: List[DependencyOut]

class GeminiCFGParseOut(BaseModel):
    sentence: str
    mermaid_code: str  # Mermaid diagram code
    explanation: str

class SemanticRoleOut(BaseModel):
    sentence: str
    mermaid_code: str
    roles: List[SemanticRole]
    explanation: str
```

**Purpose:** Structured response models ensuring consistent API responses with type validation.

---

## 6. Frontend API Integration

### 6.1 Basic API Call Pattern

```javascript
// POST request with error handling
async function analyzeText(endpoint, text) {
    try {
        const response = await fetch(`http://localhost:9000/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Error:', error.message);
        throw error;
    }
}
```

**Purpose:** Reusable function pattern for making API calls with proper error handling.

### 6.2 POS Tagging - Frontend Integration

```javascript
// Call POS endpoint
const result = await analyzeText('pos', 'Apple is buying a startup in the U.K.');

// Display tokens in frontend
result.tokens.forEach(token => {
    console.log(`${token.text}: ${token.pos} (${token.tag})`);
    // Render in UI: <span class="pos-${token.pos}">${token.text}</span>
});
```

**Purpose:** Demonstrates how to call POS endpoint and display results in UI with visual tagging.

### 6.3 NER - Frontend Integration

```javascript
// Call NER endpoint
const result = await analyzeText('ner', 'Apple is buying a startup in the U.K.');

// Highlight entities in text
result.entities.forEach(entity => {
    console.log(`${entity.text} (${entity.label})`);
    // Render with entity highlighting: <mark data-entity="${entity.label}">${entity.text}</mark>
});
```

**Purpose:** Shows how to identify and visually highlight named entities in the frontend.

### 6.4 Dependency Parsing - Rendering SVG

```javascript
// Call dependency endpoint
const result = await analyzeText('dependency', 'The cat sat on the mat.');

// Render SVG diagram directly in DOM
document.getElementById('diagram').innerHTML = result.svg;

// Access structured dependency data
result.dependencies.forEach(dep => {
    console.log(`${dep.token} -> ${dep.head} (${dep.dep})`);
});
```

**Purpose:** Renders SVG dependency diagram directly in HTML and accesses structured dependency relationships.

### 6.5 CFG Parsing - Rendering Mermaid Diagrams

```javascript
// Include Mermaid.js library
// <script type="module">
//   import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
//   mermaid.initialize({ startOnLoad: true });
// </script>

// Call CFG Gemini endpoint
const result = await analyzeText('cfg-gemini', 'The student reads the book.');

// Render Mermaid diagram
document.getElementById('diagram-container').innerHTML = `
    <pre class="mermaid">${result.mermaid_code}</pre>
`;
mermaid.init();

// Display explanation
console.log(result.explanation);
```

**Purpose:** Renders Mermaid flowchart diagrams for CFG parse trees and displays linguistic explanations.

### 6.6 Semantic Role Labeling - Frontend Display

```javascript
// Call semantic endpoint
const result = await analyzeText('semantic', 'John bought a car from a dealer yesterday.');

// Render semantic role graph
document.getElementById('semantic-graph').innerHTML = `
    <pre class="mermaid">${result.mermaid_code}</pre>
`;
mermaid.init();

// Display semantic roles as structured data
result.roles.forEach(role => {
    console.log(`${role.word} is the ${role.role} of ${role.predicate}`);
    // Render as: <div class="semantic-role">
    //   <span class="word">${role.word}</span>
    //   <span class="role">${role.role}</span>
    //   <span class="predicate">${role.predicate}</span>
    // </div>
});

// Display explanation
console.log(result.explanation);
```

**Purpose:** Visualizes semantic relationships using Mermaid graphs and displays structured role information.

### 6.7 Translation - Frontend Integration

```javascript
// Get supported languages
const languages = await fetch('http://localhost:9000/languages').then(r => r.json());

// Call translate endpoint
const response = await fetch('http://localhost:9000/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: 'Hello world',
        target_language: 'es'
    })
});

const result = await response.json();

// Display translation
console.log(`Original (${result.source_language}): ${result.original_text}`);
console.log(`Translation (${result.target_language}): ${result.translated_text}`);
// Render in UI:
// <div class="translation">
//   <p class="original">${result.original_text}</p>
//   <p class="translated">${result.translated_text}</p>
// </div>
```

**Purpose:** Demonstrates translation workflow including language selection and result display.

---

## 7. Data Presentation Patterns

### 7.1 Token Visualization

```javascript
// Render POS tokens with color coding
function renderTokens(tokens) {
    return tokens.map(token => {
        const colorClass = `pos-${token.pos.toLowerCase()}`;
        return `<span class="${colorClass}" title="${token.tag}">${token.text}</span>`;
    }).join(' ');
}

// CSS example for POS colors
// .pos-noun { background-color: #e3f2fd; }
// .pos-verb { background-color: #fff3e0; }
// .pos-adj { background-color: #f3e5f5; }
```

**Purpose:** Visual representation of tokens with POS-based color coding.

### 7.2 Entity Highlighting

```javascript
// Highlight named entities in text
function highlightEntities(text, entities) {
    let highlighted = text;
    // Sort by start position (reverse) to maintain indices
    const sorted = [...entities].sort((a, b) => b.start - a.start);
    
    sorted.forEach(entity => {
        const before = highlighted.substring(0, entity.start);
        const after = highlighted.substring(entity.end);
        const entityText = highlighted.substring(entity.start, entity.end);
        highlighted = `${before}<mark data-entity="${entity.label}">${entityText}</mark>${after}`;
    });
    
    return highlighted;
}
```

**Purpose:** Overlays entity highlights on original text while preserving positions.

### 7.3 Dependency Tree Display

```javascript
// Display dependency relationships as tree structure
function renderDependencyTree(dependencies) {
    const root = dependencies.find(d => d.dep === 'ROOT');
    if (!root) return '';
    
    function buildNode(token, deps) {
        const children = deps.filter(d => d.head === token);
        const childrenHtml = children.map(child => 
            `<li>${child.token} (${child.dep}) ${buildNode(child.token, deps)}</li>`
        ).join('');
        return childrenHtml ? `<ul>${childrenHtml}</ul>` : '';
    }
    
    return `<div class="dependency-tree">
        <span class="root">${root.token}</span>
        ${buildNode(root.token, dependencies)}
    </div>`;
}
```

**Purpose:** Creates hierarchical tree visualization from dependency data.

---

## Summary

This backend provides:
- **NLP Analysis**: POS tagging, NER, dependency parsing, CFG parsing, semantic role labeling
- **AI Integration**: Gemini AI for advanced parsing and semantic analysis
- **Translation**: Multi-language text translation
- **Visualization**: SVG diagrams for dependencies, Mermaid diagrams for parse trees and semantic roles
- **Structured Data**: Type-safe models with Pydantic validation

The frontend integration patterns show how to:
- Make API calls with error handling
- Render visualizations (SVG, Mermaid)
- Display structured NLP data (tokens, entities, dependencies)
- Present translation results
- Create interactive UI components for NLP analysis

