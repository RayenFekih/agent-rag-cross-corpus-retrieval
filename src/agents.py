import logging
from abc import ABC, abstractmethod

from src.prompts import (
    EVALUATION_AGENT_SYSTEM_PROMPT,
    EVALUATION_AGENT_USER_PROMPT,
    QUERY_REWRITER_SYSTEM_PROMPT,
    QUERY_REWRITER_USER_PROMPT,
    SEARCH_PLAN_SYSTEM_PROMPT,
    SEARCH_PLAN_USER_PROMPT,
)
from src.settings import settings

logger = logging.getLogger(__name__)


class Agent(ABC):
    def __init__(self, name: str, llm: str, user_prompt: str, system_prompt: str):
        self.name = name
        self.llm = llm
        self.user_prompt = user_prompt
        self.system_prompt = system_prompt

    @abstractmethod
    def generate(self, input_text: str) -> str:
        ...


class QueryRewriterAgent(Agent):
    def __init__(self):
        super().__init__(name="QueryRewriter", llm=settings.llm,
                         user_prompt=QUERY_REWRITER_USER_PROMPT, system_prompt=QUERY_REWRITER_SYSTEM_PROMPT)

    def generate(self, input_text: str) -> str:
        ...


class SearchPlanAgent(Agent):
    def __init__(self):
        super().__init__(name="SearchPlanAgent", llm=settings.llm,
                         user_prompt=SEARCH_PLAN_USER_PROMPT, system_prompt=SEARCH_PLAN_SYSTEM_PROMPT)

    def generate(self, input_text: str) -> str:
        ...


class EvaluationAgent(Agent):
    def __init__(self):
        super().__init__(name="EvaluationAgent", llm=settings.llm,
                         user_prompt=EVALUATION_AGENT_USER_PROMPT, system_prompt=EVALUATION_AGENT_SYSTEM_PROMPT)

    def generate(self, input_text: str) -> str:
        ...
