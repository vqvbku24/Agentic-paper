import json
from dseek.schemas import Document, Idea, RunRecord

def test_document_round_trip():
    data = {
        "doc_id": "123",
        "source": "acl_anthology",
        "lang": "fr",
        "title_native": "Titre",
        "abstract_native": "Résumé",
        "title_en": "Title",
        "abstract_en": "Abstract",
        "has_en_abstract": True,
        "year": 2024,
        "venue": "jeptalnrecital",
        "url": "https://example.com",
        "license": "CC-BY-4.0",
        "body_path": None
    }

    doc = Document(**data)
    dumped = json.loads(doc.model_dump_json())

    assert dumped["doc_id"] == "123"
    assert dumped["lang"] == "fr"

    # round-trip
    doc_reloaded = Document(**dumped)
    assert doc_reloaded.doc_id == doc.doc_id

def test_idea_round_trip():
    data = {
        "idea_id": "idea_001",
        "source_doc_id": "123",
        "generator": "llm",
        "operators": [{"name": "D1", "level": 2}],
        "text_en": "Some text",
        "facets": {"purpose": "purpose here"},
        "preemption_label": "full",
        "validity": {
            "judge_model": "judge_a",
            "label": "full",
            "confidence": 0.9,
            "second_judge_label": "full",
            "agree": True,
            "human_label": None
        },
        "shortcut": {"bm25_top1_hit": False},
        "split": "pilot",
        "seed": 1234
    }

    idea = Idea(**data)
    dumped = json.loads(idea.model_dump_json())
    assert dumped["idea_id"] == "idea_001"
    assert dumped["validity"]["judge_model"] == "judge_a"

    idea_reloaded = Idea(**dumped)
    assert idea_reloaded.idea_id == idea.idea_id

def test_run_record_round_trip():
    data = {
        "run_id": "run_01",
        "system": "hybrid",
        "condition": "en_only",
        "budget": 10.0,
        "idea_id": "idea_001",
        "ranked_doc_ids": ["123", "456"],
        "cost": {
            "n_search": 3,
            "tokens_in": 100,
            "tokens_out": 50,
            "usd": 0.05
        },
        "trajectory_path": None,
        "verdict": None,
        "confidence": None
    }

    record = RunRecord(**data)
    dumped = json.loads(record.model_dump_json())
    assert dumped["run_id"] == "run_01"
    assert dumped["cost"]["n_search"] == 3

    record_reloaded = RunRecord(**dumped)
    assert record_reloaded.run_id == record.run_id
