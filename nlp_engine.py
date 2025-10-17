from __future__ import annotations

from typing import Any, List

import spacy
from spacy.language import Language
from google.genai.client import Client
from models import NLPAnalysisOut, TokenOut, EntityOut, POSAnalysisOut, NERAnalysisOut, DependencyOut, DependencyParseOut, ConstituencyParseOut, CFGParseOut, GeminiCFGParseOut, SemanticRoleOut, SemanticRole
from dotenv import load_dotenv
import os

load_dotenv()
gemini_client = Client(api_key=os.getenv("GEMINI_API_KEY"))

_POS_NLP_SINGLETON: Language | None = None
_NER_NLP_SINGLETON: Language | None = None


def get_pos_nlp() -> Language:
    """Get TRF model for POS tagging (better accuracy)"""
    global _POS_NLP_SINGLETON
    if _POS_NLP_SINGLETON is None:
        try:
            _POS_NLP_SINGLETON = spacy.load("en_core_web_trf")
        except OSError as exc:
            raise RuntimeError(
                "spaCy TRF model 'en_core_web_trf' is not installed. "
                "Run: python -m spacy download en_core_web_trf"
            ) from exc
    return _POS_NLP_SINGLETON


def get_ner_nlp() -> Language:
    """Get small model for NER (lightweight)"""
    global _NER_NLP_SINGLETON
    if _NER_NLP_SINGLETON is None:
        try:
            _NER_NLP_SINGLETON = spacy.load("en_core_web_sm")
        except OSError as exc:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' is not installed. "
                "Run: python -m spacy download en_core_web_sm"
            ) from exc
    return _NER_NLP_SINGLETON


def analyze_text(text: str) -> NLPAnalysisOut:
    """Analyze text using TRF model for POS and small model for NER"""
    pos_nlp = get_pos_nlp()
    ner_nlp = get_ner_nlp()
    
    # Use TRF model for POS tagging
    pos_doc = pos_nlp(text)
    
    # Use small model for NER
    ner_doc = ner_nlp(text)

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

    return NLPAnalysisOut(tokens=tokens, entities=entities)


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


def analyze_dependency(sentence: str) -> DependencyParseOut:
    """Analyze dependency parsing for a single sentence and generate visualization"""
    from spacy import displacy
    
    # Use TRF model for better dependency parsing accuracy
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


def analyze_constituency(sentence: str) -> ConstituencyParseOut:
    """Analyze constituency parsing for a single sentence and generate tree visualization"""
    from spacy import displacy
    
    # Use TRF model which includes constituency parser
    nlp = get_pos_nlp()
    doc = nlp(sentence)
    
    # Check if doc has constituency parse
    if not doc.has_annotation("SENT_START"):
        raise RuntimeError("Constituency parsing requires sentence boundaries")
    
    # Generate text representation of the tree
    text_tree = ""
    for sent in doc.sents:
        if hasattr(sent, 'constituents'):
            # Build a text representation of the constituency tree
            text_tree = _build_tree_text(sent._.constituents if hasattr(sent._, 'constituents') else None)
        else:
            # Fallback: use basic noun chunks if constituency not available
            text_tree = str(list(sent.noun_chunks))
    
    # Generate SVG visualization - use dependency style as fallback since 
    # constituency visualization requires benepar
    svg = displacy.render(doc, style="dep", jupyter=False, options={
        "compact": True,
        "bg": "#ffffff",
        "color": "#000000",
        "font": "Arial"
    })
    
    # Alternative: build a simple tree representation
    if not text_tree:
        text_tree = _build_simple_constituency_tree(doc)
    
    return ConstituencyParseOut(
        sentence=sentence,
        svg=svg,
        text_tree=text_tree
    )


def _build_simple_constituency_tree(doc) -> str:
    """Build a simple text-based constituency tree from spaCy doc"""
    tree_lines = []
    for sent in doc.sents:
        tree_lines.append(f"(S")
        # Group by noun chunks and verb phrases
        noun_chunks = list(sent.noun_chunks)
        
        for chunk in noun_chunks:
            tree_lines.append(f"  (NP {chunk.text})")
        
        # Add verb phrases
        for token in sent:
            if token.pos_ == "VERB" and token not in [t for chunk in noun_chunks for t in chunk]:
                tree_lines.append(f"  (VP {token.text})")
        
        tree_lines.append(")")
    
    return "\n".join(tree_lines)


def _build_tree_text(constituents) -> str:
    """Helper to build text tree from constituents"""
    if not constituents:
        return ""
    lines = []
    for const in constituents:
        lines.append(f"({const.label_} {const.text})")
    return "\n".join(lines)


def analyze_cfg(sentence: str) -> CFGParseOut:
    """Analyze sentence using Context-Free Grammar (CFG) parsing with NLTK"""
    try:
        import nltk
        from nltk import CFG
        from nltk.parse import ChartParser
    except ImportError:
        return CFGParseOut(
            sentence=sentence,
            trees=[],
            grammar_rules="",
            success=False,
            error_message="NLTK is not installed. Please run: pip install nltk"
        )
    
    # Define a comprehensive CFG for English
    grammar_rules = """
        S -> NP VP | VP
        NP -> Det N | Det Adj N | Pron | PropN | Det N PP | Adj N
        VP -> V NP | V | V PP | V NP PP | Aux VP | V Adj
        PP -> P NP
        Det -> 'the' | 'a' | 'an' | 'this' | 'that' | 'these' | 'those' | 'my' | 'your' | 'his' | 'her'
        N -> 'cat' | 'dog' | 'book' | 'student' | 'teacher' | 'fox' | 'mat' | 'table' | 'chair' | 'house' | 'car' | 'tree' | 'bird' | 'man' | 'woman' | 'child' | 'food' | 'water' | 'startup' | 'company'
        Pron -> 'I' | 'you' | 'he' | 'she' | 'it' | 'we' | 'they'
        PropN -> 'Apple' | 'John' | 'Mary' | 'London' | 'Paris' | 'UK' | 'U.K.'
        V -> 'is' | 'are' | 'was' | 'were' | 'sits' | 'sat' | 'reads' | 'read' | 'jumps' | 'jumped' | 'runs' | 'ran' | 'sleeps' | 'slept' | 'eats' | 'ate' | 'drinks' | 'buying' | 'buys'
        Adj -> 'quick' | 'brown' | 'lazy' | 'big' | 'small' | 'happy' | 'sad' | 'good' | 'bad' | 'red' | 'blue'
        P -> 'on' | 'in' | 'at' | 'over' | 'under' | 'near' | 'by' | 'with' | 'from' | 'to'
        Aux -> 'can' | 'will' | 'should' | 'would' | 'could' | 'may' | 'might' | 'must'
    """
    
    try:
        # Parse the grammar
        cfg = CFG. fromstring(grammar_rules)
        parser = ChartParser(cfg)
        
        # Tokenize the sentence (simple split by space and lowercase)
        # Remove punctuation for simpler parsing
        tokens = sentence.lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
        
        # Parse the sentence
        trees = list(parser.parse(tokens))
        
        if trees:
            tree_strings = [str(tree) for tree in trees]
            return CFGParseOut(
                sentence=sentence,
                trees=tree_strings,
                grammar_rules=grammar_rules.strip(),
                success=True
            )
        else:
            return CFGParseOut(
                sentence=sentence,
                trees=[],
                grammar_rules=grammar_rules.strip(),
                success=False,
                error_message=f"No valid parse found. The sentence may contain words not in the grammar lexicon or have an unrecognized structure. Tokens: {tokens}"
            )
    
    except Exception as e:
        return CFGParseOut(
            sentence=sentence,
            trees=[],
            grammar_rules=grammar_rules.strip(),
            success=False,
            error_message=f"Parsing error: {str(e)}"
        )


def analyze_cfg_using_gemini(sentence: str) -> GeminiCFGParseOut:
    """
    Use Gemini AI to generate a CFG parse tree in Mermaid diagram format.
    This provides a visual, AI-generated constituency parse.
    """
    try:
        # Create the prompt for Gemini
        prompt = f"""
        You are a linguistic expert specializing in Context-Free Grammar (CFG) parsing.

        Analyze the following sentence and create a CFG parse tree in Mermaid flowchart format:
        Sentence: "{sentence}"

        Requirements:
        1. Generate a Mermaid flowchart code that represents the CFG parse tree
        2. Use proper linguistic labels (S for Sentence, NP for Noun Phrase, VP for Verb Phrase, Det for Determiner, N for Noun, V for Verb, Adj for Adjective, P for Preposition, PP for Prepositional Phrase, etc.)
        3. Use the following Mermaid syntax:
        - Use graph TD for top-down tree
        - Use node IDs like S1, NP1, VP1, etc.
        - Format: nodeID["Label: word"]
        - Use --> for edges
        4. Also provide a brief explanation of the parse structure

        Example format:
        ```mermaid
        graph TD
            S1["S"]
            NP1["NP"]
            Det1["Det: the"]
            N1["N: cat"]
            VP1["VP"]
            V1["V: sat"]
            
            S1 --> NP1
            S1 --> VP1
            NP1 --> Det1
            NP1 --> N1
            VP1 --> V1
        ```

        Return ONLY valid Mermaid code in the mermaid_code field and a brief explanation in the explanation field.
        """

        # Use Gemini with structured output (Pydantic model)
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": GeminiCFGParseOut,
            }
        )
        
        # Parse the response
        if response.text:
            result = GeminiCFGParseOut.model_validate_json(response.text)
            return result
        else:
            raise ValueError("Empty response from Gemini")
        
    except Exception as e:
        # Return error with empty mermaid code
        return GeminiCFGParseOut(
            sentence=sentence,
            mermaid_code="",
            explanation=f"Error generating CFG parse with Gemini: {str(e)}"
        )


def analyze_semantic_roles(sentence: str) -> SemanticRoleOut:
    """
    Use Gemini AI to perform semantic role labeling (SRL) and generate a semantic role graph.
    Shows predicate-argument structures: who did what to whom, with what, where, when, etc.
    """
    try:
        # Create the prompt for Gemini
        prompt = f"""
You are a linguistic expert specializing in Semantic Role Labeling (SRL).

Analyze the following sentence and identify the semantic roles of each word/phrase:
Sentence: "{sentence}"

Semantic Role Labeling identifies the predicate-argument structure:
- **Predicate**: The main action/event (usually a verb)
- **Agent (ARG0)**: Who/what performs the action
- **Patient/Theme (ARG1)**: Who/what receives the action or is affected
- **Recipient (ARG2)**: To whom/for whom
- **Instrument (ARG-MNR)**: With what (tool/means)
- **Location (ARG-LOC)**: Where
- **Time (ARG-TMP)**: When
- **Source (ARG-DIR)**: From where/whom
- **Goal (ARG-GOL)**: To where
- **Cause (ARG-CAU)**: Why/because of what
- **Beneficiary (ARG-BNF)**: For whom/what

Requirements:
1. Generate a Mermaid graph code showing semantic roles as a directed graph
2. Format: Use graph LR (left-to-right)
3. Nodes should represent predicates and arguments
4. Edges should be labeled with semantic role names
5. Use clear node IDs and labels
6. Create a roles array listing each role with word, role type, and associated predicate

Example Mermaid format:
```mermaid
graph LR
    John["John"]
    bought["bought (Predicate)"]
    car["a car"]
    dealer["a dealer"]
    
    John -->|Agent| bought
    bought -->|Theme| car
    bought -->|Source| dealer
```

Example roles array:
[
  {{"word": "John", "role": "Agent", "predicate": "bought"}},
  {{"word": "a car", "role": "Theme", "predicate": "bought"}},
  {{"word": "a dealer", "role": "Source", "predicate": "bought"}}
]

Return:
- mermaid_code: Valid Mermaid graph code
- roles: Array of semantic roles with word, role, and predicate
- explanation: Brief explanation of the semantic structure
"""

        # Use Gemini with structured output (Pydantic model)
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": SemanticRoleOut,
            }
        )
        
        # Parse the response
        if response.text:
            result = SemanticRoleOut.model_validate_json(response.text)
            return result
        else:
            raise ValueError("Empty response from Gemini")
        
    except Exception as e:
        # Return error with empty data
        return SemanticRoleOut(
            sentence=sentence,
            mermaid_code="",
            roles=[],
            explanation=f"Error generating semantic role analysis with Gemini: {str(e)}"
        )


