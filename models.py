from typing import List

from pydantic import BaseModel


class TextInput(BaseModel):
    text: str


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


class NLPAnalysisOut(BaseModel):
    tokens: List[TokenOut]
    entities: List[EntityOut]


class POSAnalysisOut(BaseModel):
    tokens: List[TokenOut]


class NERAnalysisOut(BaseModel):
    entities: List[EntityOut]


class DependencyOut(BaseModel):
    token: str
    dep: str
    head: str
    pos: str
    children: List[str]


class DependencyParseOut(BaseModel):
    sentence: str
    svg: str
    dependencies: List[DependencyOut]


class ConstituencyParseOut(BaseModel):
    sentence: str
    svg: str
    text_tree: str


class CFGParseOut(BaseModel):
    sentence: str
    trees: List[str]
    grammar_rules: str
    success: bool
    error_message: str = ""


class GeminiCFGParseOut(BaseModel):
    sentence: str
    mermaid_code: str
    explanation: str


class SemanticRole(BaseModel):
    word: str
    role: str
    predicate: str


class SemanticRoleOut(BaseModel):
    sentence: str
    mermaid_code: str
    roles: List[SemanticRole]
    explanation: str


class TranslationInput(BaseModel):
    text: str
    target_language: str 


class TranslationOut(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float


