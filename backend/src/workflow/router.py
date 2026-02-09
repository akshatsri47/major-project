from pathlib import Path
from pydantic import BaseModel, Field

from langgraph.types import Send

from ..llm import get_model
from ..state import Classification, RouterState


class ClassificationResult(BaseModel):
    """Classify the user query into the proper sub-agent."""
    classifications: list[Classification] = Field(
        description="SELECT THE APPROPRIATE AGENT FOR THE TASK"
    )


model = get_model()


def classify_query(state: RouterState) -> dict:
    system_prompt = (
        Path(__file__).resolve().parent.parent
        / "prompt"
        / "triage.md"
    ).read_text(encoding="utf-8")

    model_router = model.with_structured_output(ClassificationResult)

    result = model_router.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["query"]}
    ])

    return {
        "classifications": result.classifications
    }


def route_to_agent(state: RouterState) -> list[Send]:
    return [
        Send(cls["source"], {"query": cls["query"]})
        for cls in state["classifications"]
    ]
