"""Faithfulness metric — checks if response claims are grounded in source context."""

import json
import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from dentalens.infrastructure.llm.prompt_templates import HALLUCINATION_CHECK_PROMPT

logger = logging.getLogger("dentalens.eval.faithfulness")


class FaithfulnessMetric:
    """Measures how faithfully a response reflects the source context.

    Uses LLM-as-judge to extract claims from the response and verify
    each one against the provided context. Returns a score from 0.0
    (no claims supported) to 1.0 (all claims supported).
    """

    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    async def evaluate(self, response: str, contexts: list[str]) -> tuple[float, list[dict]]:
        """Evaluate faithfulness of a response against source contexts.

        Returns:
            Tuple of (faithfulness_score, list of claim evaluations)
        """
        context_text = "\n\n---\n\n".join(contexts)
        prompt = HALLUCINATION_CHECK_PROMPT.format(
            context=context_text,
            response=response,
        )

        try:
            result = await self._llm.ainvoke([
                SystemMessage(content="You are a precise evaluation judge. Respond only with valid JSON."),
                HumanMessage(content=prompt),
            ])
            text = result.content if hasattr(result, "content") else str(result)
            parsed = json.loads(text)
            score = float(parsed.get("overall_faithfulness", 0.0))
            claims = parsed.get("claims", [])
            return score, claims
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Faithfulness evaluation failed: %s", e)
            return 0.5, []  # Neutral score on failure
