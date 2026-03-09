"""Hallucination detection — flags response statements not grounded in context."""

import logging

from dentalens.services.evaluation.metrics.faithfulness import FaithfulnessMetric

logger = logging.getLogger("dentalens.eval.hallucination")

# Threshold below which we flag hallucination
_HALLUCINATION_THRESHOLD = 0.7


class HallucinationDetector:
    """Detects hallucinated content in RAG responses.

    A claim is considered hallucinated if it is not supported by
    the provided source context. This detector wraps the faithfulness
    metric and applies a threshold to flag responses.
    """

    def __init__(self, faithfulness_metric: FaithfulnessMetric):
        self._faithfulness = faithfulness_metric

    async def detect(self, response: str, contexts: list[str]) -> tuple[bool, list[str]]:
        """Check for hallucinations in a response.

        Returns:
            Tuple of (hallucination_detected, list of hallucinated claims)
        """
        score, claims = await self._faithfulness.evaluate(response, contexts)

        hallucinated_claims = [
            c["claim"]
            for c in claims
            if c.get("verdict") == "NOT_SUPPORTED"
        ]

        detected = score < _HALLUCINATION_THRESHOLD or len(hallucinated_claims) > 0
        if detected:
            logger.warning(
                "Hallucination detected (faithfulness=%.2f, %d unsupported claims)",
                score, len(hallucinated_claims),
            )

        return detected, hallucinated_claims
