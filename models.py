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


