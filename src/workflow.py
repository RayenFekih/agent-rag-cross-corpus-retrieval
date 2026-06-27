import logging

from google.adk import Context, Workflow
from google.adk.workflow import node

from src.agents import (
    evaluation_agent,
    llm_generator_agent,
    search_plan_agent,
)
from src.schemas import EvaluationInput, GeneratorInput, SearchPlanInput
from src.settings import settings

logger = logging.getLogger(__name__)

if settings.demo_scenario > 0:
    from src.mocks import mock_retrieval_node as _retrieval_node
else:
    from src.agents import retrieval_agent as _retrieval_node


@node(rerun_on_resume=True)
async def retrieval_loop(ctx: Context, node_input: str):
    """Iterative retrieval and evaluation loop.

    Runs plan → retrieve → evaluate, retrying with gap feedback until the
    Evaluation Agent is satisfied or settings.max_retries is reached.
    """
    user_query = node_input
    feedback = None

    search_plan = await ctx.run_node(
        search_plan_agent, SearchPlanInput(
            user_query=user_query, feedback=feedback)
    )
    contexts = await ctx.run_node(_retrieval_node, search_plan)
    evaluation = await ctx.run_node(
        evaluation_agent,
        EvaluationInput(user_query=user_query,
                        search_plan=search_plan, contexts=contexts),
    )

    retries = 0
    while not evaluation["sufficient"] and retries < settings.max_retries:
        logger.info(
            f"Retrieval insufficient — retry {retries + 1}/{settings.max_retries}")
        feedback = evaluation["feedback"]
        search_plan = await ctx.run_node(
            search_plan_agent, SearchPlanInput(
                user_query=user_query, feedback=feedback)
        )
        contexts = await ctx.run_node(_retrieval_node, search_plan)
        evaluation = await ctx.run_node(
            evaluation_agent,
            EvaluationInput(user_query=user_query,
                            search_plan=search_plan, contexts=contexts),
        )
        retries += 1

    return contexts


@node(rerun_on_resume=True)
async def rag_workflow(ctx: Context, node_input: str):
    """Top-level orchestrator node.

    ADK passes the user message as `node_input` when triggering this node
    from the Workflow START edge. Internally it is forwarded as `user_query`.

    Runs the retrieval loop to collect sufficient contexts, then passes them
    to the LLM Generator to produce the final grounded answer.
    """
    verified_contexts = await ctx.run_node(retrieval_loop, node_input)
    return await ctx.run_node(
        llm_generator_agent,
        GeneratorInput(user_query=node_input, contexts=verified_contexts),
    )


root_agent = Workflow(
    name="agentic_rag_workflow",
    edges=[("START", rag_workflow)],
)
