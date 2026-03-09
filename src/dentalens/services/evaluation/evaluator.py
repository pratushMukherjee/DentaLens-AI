"""Evaluation pipeline — orchestrates all metrics for RAG response quality assessment."""

import asyncio
import logging
import time

from langchain_core.language_models import BaseChatModel

from dentalens.domain.models.evaluation import EvalReport, EvaluationResult
from dentalens.services.evaluation.metrics.faithfulness import FaithfulnessMetric
from dentalens.services.evaluation.metrics.hallucination import HallucinationDetector
from dentalens.services.evaluation.metrics.relevance import RelevanceMetric
from dentalens.services.evaluation.metrics.responsible_ai import ResponsibleAIChecker

logger = logging.getLogger("dentalens.evaluation")


class EvaluationPipeline:
    """Orchestrates all evaluation metrics for comprehensive RAG assessment.

    Runs faithfulness, relevance, hallucination, and responsible AI checks
    in parallel for each query-response pair.
    """

    def __init__(self, llm: BaseChatModel):
        self._faithfulness = FaithfulnessMetric(llm)
        self._relevance = RelevanceMetric(llm)
        self._hallucination = HallucinationDetector(self._faithfulness)
        self._responsible_ai = ResponsibleAIChecker()

    async def evaluate(
        self, query: str, response: str, contexts: list[str]
    ) -> EvaluationResult:
        """Evaluate a single RAG response across all metrics.

        Runs faithfulness, relevance, and hallucination checks concurrently.
        """
        start = time.perf_counter()

        # Run LLM-based metrics in parallel
        faithfulness_task = self._faithfulness.evaluate(response, contexts)
        relevance_task = self._relevance.evaluate(query, response)
        hallucination_task = self._hallucination.detect(response, contexts)

        (faith_score, _), (rel_score, _), (hallucination_detected, _) = await asyncio.gather(
            faithfulness_task, relevance_task, hallucination_task
        )

        # Run rule-based checks synchronously (fast)
        rai_flags = self._responsible_ai.check(response)

        latency = (time.perf_counter() - start) * 1000

        result = EvaluationResult(
            query=query,
            response=response,
            retrieved_contexts=contexts,
            faithfulness_score=faith_score,
            relevance_score=rel_score,
            hallucination_detected=hallucination_detected,
            responsible_ai_flags=rai_flags,
            latency_ms=latency,
        )

        logger.info(
            "Evaluation: faithfulness=%.2f, relevance=%.2f, hallucination=%s, flags=%d",
            faith_score, rel_score, hallucination_detected, len(rai_flags),
        )
        return result

    async def evaluate_batch(
        self, samples: list[dict]
    ) -> list[EvaluationResult]:
        """Evaluate a batch of query-response pairs."""
        tasks = [
            self.evaluate(s["query"], s["response"], s["contexts"])
            for s in samples
        ]
        return await asyncio.gather(*tasks)

    @staticmethod
    def generate_report(results: list[EvaluationResult]) -> EvalReport:
        """Generate an aggregate evaluation report."""
        total = len(results)
        if total == 0:
            return EvalReport(
                total_queries=0, avg_faithfulness=0, avg_relevance=0,
                hallucination_rate=0, avg_latency_ms=0, results=[],
            )

        avg_faith = sum(r.faithfulness_score for r in results) / total
        avg_rel = sum(r.relevance_score for r in results) / total
        hall_rate = sum(1 for r in results if r.hallucination_detected) / total
        avg_latency = sum(r.latency_ms for r in results) / total

        flag_counts: dict[str, int] = {}
        for r in results:
            for flag in r.responsible_ai_flags:
                flag_type = flag.split(":")[0]
                flag_counts[flag_type] = flag_counts.get(flag_type, 0) + 1

        return EvalReport(
            total_queries=total,
            avg_faithfulness=round(avg_faith, 3),
            avg_relevance=round(avg_rel, 3),
            hallucination_rate=round(hall_rate, 3),
            responsible_ai_flag_counts=flag_counts,
            avg_latency_ms=round(avg_latency, 1),
            results=results,
        )
