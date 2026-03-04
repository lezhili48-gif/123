import json
from openai import OpenAI
from app.core.config import get_settings
from app.schemas.schemas import EvidenceItem


def extract_evidence_from_abstract(doi: str | None, abstract: str | None) -> list[dict]:
    if not abstract:
        return []
    settings = get_settings()
    pointer = doi or "NO_DOI"
    if not settings.openai_api_key:
        sentence = abstract.split(".")[0].strip() or abstract[:120]
        return [EvidenceItem(claim=sentence, source_pointer=pointer, confidence="low").model_dump()]

    client = OpenAI(api_key=settings.openai_api_key)
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim": {"type": "string"},
                        "context": {"type": "string"},
                        "outcome": {"type": "string"},
                        "magnitude": {"type": "string"},
                        "mechanism": {"type": "string"},
                        "source_pointer": {"type": "string"},
                        "confidence": {"type": "string"},
                    },
                    "required": ["claim", "source_pointer"],
                },
            }
        },
        "required": ["items"],
    }
    resp = client.responses.create(
        model=settings.model_text,
        input=[
            {"role": "system", "content": "Extract evidence as strict JSON."},
            {"role": "user", "content": f"DOI:{pointer}\nAbstract:{abstract}\nOutput JSON with key items."},
        ],
        text={"format": {"type": "json_schema", "name": "evidence", "schema": schema}},
    )
    data = json.loads(resp.output_text)
    out = []
    for item in data.get("items", []):
        item.setdefault("source_pointer", pointer)
        out.append(EvidenceItem(**item).model_dump())
    return out
