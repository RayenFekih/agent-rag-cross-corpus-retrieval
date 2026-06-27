import logging

from google.adk import Context
from google.adk.agents import LlmAgent
from google.adk.workflow import node

from src.prompts import (
    EVALUATION_AGENT_SYSTEM_PROMPT,
    LLM_GENERATOR_SYSTEM_PROMPT,
    SEARCH_PLAN_SYSTEM_PROMPT,
)
from src.schemas import (
    EvaluationInput,
    EvaluationResult,
    GeneratorInput,
    SearchPlan,
    SearchPlanInput,
)
from src.settings import settings

logger = logging.getLogger(__name__)


search_plan_agent = LlmAgent(
    name="search_plan_agent",
    model=settings.llm,
    instruction=SEARCH_PLAN_SYSTEM_PROMPT,
    input_schema=SearchPlanInput,
    output_schema=SearchPlan,
    description=(
        "Rewrites the user query and produces a structured search plan "
        "mapping each corpus to one or more retrieval tasks."
    ),
)

evaluation_agent = LlmAgent(
    name="evaluation_agent",
    model=settings.llm,
    instruction=EVALUATION_AGENT_SYSTEM_PROMPT,
    input_schema=EvaluationInput,
    output_schema=EvaluationResult,
    description=(
        "Evaluates whether the retrieved contexts are sufficient to answer "
        "the user query. Returns a gap analysis when they are not."
    ),
)

llm_generator_agent = LlmAgent(
    name="llm_generator",
    model=settings.llm,
    instruction=LLM_GENERATOR_SYSTEM_PROMPT,
    input_schema=GeneratorInput,
    output_schema=str,
    description=(
        "Synthesizes a grounded final answer from the verified retrieved contexts."
    ),
)


@node(name="retrieval_agent")
async def retrieval_agent(ctx: Context, node_input: SearchPlan) -> list:
    """Execute every query task in the search plan against Agent Search.

    Calls search_agent_search() from src/retrieval.py for each corpus and
    query task in search_plan.tasks, and returns a flat list of retrieved
    document dicts with rank signals.
    """
    ...
