from __future__ import annotations

from typing import Any, List

import spacy
from spacy.language import Language

from models import NLPAnalysisOut, TokenOut, EntityOut


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


