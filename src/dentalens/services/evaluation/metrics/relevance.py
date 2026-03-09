"""Relevance metric — measures how well a response addresses the user's query."""

import json
import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from dentalens.infrastructure.llm.prompt_templates import RELEVANCE_CHECK_PROMPT

logger = logging.getLogger("dentalens.eval.relevance")


class RelevanceMetric:
    """Measures semantic relevance between user query and AI response.

    Uses LLM-as-judge to assess whether the response directly
    addresses the user's question.
    """

    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    async def evaluate(self, query: str, response: str) -> tuple[float, str]:
        """Evaluate relevance of a response to the query.

        Returns:
            Tuple of (relevance_score, reasoning)
        """
        prompt = RELEVANCE_CHECK_PROMPT.format(query=query, response=response)

        try:
            result = await self._llm.ainvoke([
                SystemMessage(content="You are a precise evaluation judge. Respond only with valid JSON."),
                HumanMessage(content=prompt),
            ])
            text = result.content if hasattr(result, "content") else str(result)
            parsed = json.loads(text)
            score = float(parsed.get("relevance_score", 0.0))
            reasoning = parsed.get("reasoning", "")
            return score, reasoning
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Relevance evaluation failed: %s", e)
            return 0.5, "Evaluation failed"
