from pydantic import BaseModel


class QueryTask(BaseModel):
    """A single retrieval task targeting one corpus."""

    improved_query: str
    looking_for: str


class CorpusTasks(BaseModel):
    corpus_id: str
    tasks: list[QueryTask]


class SearchPlan(BaseModel):
    """Structured search plan produced by the Search Planning Agent.

    Maps each corpus ID to one or more query tasks.
    """

    tasks: list[CorpusTasks]


class EvaluationResult(BaseModel):
    """Sufficiency verdict produced by the Evaluation Agent."""

    sufficient: bool
    feedback: str | None = None


class SearchPlanInput(BaseModel):
    """Input to the Search Planning Agent."""

    user_query: str
    feedback: str | None = None


class RetrievedContext(BaseModel):
    corpus_id: str
    source_id: str | None = None
    title: str | None = None
    content: str
    score: float | None = None


class EvaluationInput(BaseModel):
    user_query: str
    search_plan: SearchPlan
    contexts: list[RetrievedContext]


class GeneratorInput(BaseModel):
    user_query: str
    contexts: list[RetrievedContext]
