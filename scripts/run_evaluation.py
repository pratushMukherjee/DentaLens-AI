"""CLI script to run the DentaLens AI evaluation suite."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dentalens.config.settings import Settings
from dentalens.config.logging_config import setup_logging
from dentalens.config.constants import FAITHFULNESS_THRESHOLD, RELEVANCE_THRESHOLD, HALLUCINATION_RATE_THRESHOLD
from dentalens.infrastructure.llm.llm_provider import LLMProviderFactory
from dentalens.services.evaluation.evaluator import EvaluationPipeline
from dentalens.services.evaluation.eval_dataset import EvalDataset


async def main() -> None:
    settings = Settings()
    setup_logging(settings.log_level)

    print("DentaLens AI — Evaluation Suite")
    print("=" * 40)

    # Load evaluation dataset
    eval_path = Path("tests/evaluation/golden_qa_pairs.json")
    dataset = EvalDataset.load(eval_path)
    print(f"Loaded {len(dataset)} evaluation samples")

    # Create LLM for evaluation
    llm = LLMProviderFactory.create(
        model=settings.openai_model,
        api_key=settings.openai_api_key.get_secret_value(),
        temperature=0.0,
        streaming=False,
    )

    pipeline = EvaluationPipeline(llm)

    # Run evaluation on each sample
    samples = [
        {
            "query": s.query,
            "response": s.expected_answer,
            "contexts": [s.relevant_context],
        }
        for s in dataset.samples
    ]

    print(f"\nRunning evaluation on {len(samples)} samples...")
    results = await pipeline.evaluate_batch(samples)
    report = pipeline.generate_report(results)

    # Print results
    print(f"\n{'=' * 50}")
    print("EVALUATION REPORT")
    print(f"{'=' * 50}")
    print(f"Total queries evaluated:  {report.total_queries}")
    print(f"Avg faithfulness:         {report.avg_faithfulness:.3f}  (threshold: {FAITHFULNESS_THRESHOLD})")
    print(f"Avg relevance:            {report.avg_relevance:.3f}  (threshold: {RELEVANCE_THRESHOLD})")
    print(f"Hallucination rate:       {report.hallucination_rate:.3f}  (threshold: {HALLUCINATION_RATE_THRESHOLD})")
    print(f"Avg latency:              {report.avg_latency_ms:.1f} ms")

    if report.responsible_ai_flag_counts:
        print(f"\nResponsible AI flags:")
        for flag, count in report.responsible_ai_flag_counts.items():
            print(f"  {flag}: {count}")

    # Check thresholds
    print(f"\n{'=' * 50}")
    passed = True
    if report.avg_faithfulness < FAITHFULNESS_THRESHOLD:
        print(f"FAIL: Faithfulness {report.avg_faithfulness:.3f} < {FAITHFULNESS_THRESHOLD}")
        passed = False
    if report.avg_relevance < RELEVANCE_THRESHOLD:
        print(f"FAIL: Relevance {report.avg_relevance:.3f} < {RELEVANCE_THRESHOLD}")
        passed = False
    if report.hallucination_rate > HALLUCINATION_RATE_THRESHOLD:
        print(f"FAIL: Hallucination rate {report.hallucination_rate:.3f} > {HALLUCINATION_RATE_THRESHOLD}")
        passed = False

    if passed:
        print("ALL THRESHOLDS PASSED")
    print(f"{'=' * 50}")

    # Save report
    report_path = Path("data/evaluation_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report.model_dump(mode="json"), f, indent=2, default=str)
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
