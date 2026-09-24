from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Document(BaseModel):
    doc_id: str
    source: str
    lang: str
    title_native: str
    abstract_native: str
    title_en: Optional[str] = None
    abstract_en: Optional[str] = None
    has_en_abstract: bool
    year: int
    venue: str
    url: Optional[str] = None
    license: Optional[str] = None
    body_path: Optional[str] = None

class IdeaValidity(BaseModel):
    judge_model: str
    label: str
    confidence: float
    second_judge_label: Optional[str] = None
    agree: bool
    human_label: Optional[str] = None

class Idea(BaseModel):
    idea_id: str
    source_doc_id: str
    generator: str
    operators: List[Dict[str, Any]]
    text_en: str
    facets: Dict[str, str]
    preemption_label: str
    validity: IdeaValidity
    shortcut: Dict[str, Any]
    split: str
    seed: int

class Hit(BaseModel):
    doc_id: str
    score: float
    view: str
    lang: str
    rank: int

class RunCost(BaseModel):
    n_search: int
    tokens_in: int
    tokens_out: int
    usd: float

class RunRecord(BaseModel):
    run_id: str
    system: str
    condition: str
    budget: float
    idea_id: str
    ranked_doc_ids: List[str]
    cost: RunCost
    trajectory_path: Optional[str] = None
    verdict: Optional[str] = None
    confidence: Optional[float] = None
