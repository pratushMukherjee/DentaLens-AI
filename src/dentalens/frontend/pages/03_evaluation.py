"""Evaluation page — model quality assessment with responsible AI metrics."""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[4]
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

import httpx
import streamlit as st
import pandas as pd

from dentalens.frontend.components.metrics_cards import render_eval_scorecard, render_metric_row

st.title("🔍 Model Evaluation")
st.caption("Assess RAG response quality with faithfulness, relevance, and responsible AI metrics")

api_url = st.session_state.get("api_base_url", "http://localhost:8000")

# Manual evaluation
st.subheader("Evaluate a Response")
with st.form("eval_form"):
    query = st.text_input("Query", placeholder="Does the PPO Gold plan cover root canals?")
    response = st.text_area(
        "Response to Evaluate",
        placeholder="Yes, the PPO Gold plan covers root canal therapy under Basic Services at 80% after deductible.",
    )
    contexts = st.text_area(
        "Source Context (one per line)",
        placeholder="Basic Services (80% after deductible): D3310 Root canal therapy...",
    )
    submitted = st.form_submit_button("Run Evaluation")

if submitted and query and response:
    context_list = [c.strip() for c in contexts.split("\n") if c.strip()]
    if not context_list:
        context_list = ["No context provided"]

    with st.spinner("Evaluating..."):
        try:
            resp = httpx.post(
                f"{api_url}/api/v1/evaluate",
                json={"query": query, "response": response, "contexts": context_list},
                timeout=60.0,
            )
            result = resp.json()

            st.divider()
            st.subheader("Results")
            render_eval_scorecard(
                faithfulness=result["faithfulness_score"],
                relevance=result["relevance_score"],
                hallucination_rate=1.0 if result["hallucination_detected"] else 0.0,
            )

            render_metric_row([
                {"label": "Latency", "value": f"{result['latency_ms']:.0f} ms"},
                {"label": "Hallucination", "value": "Detected" if result["hallucination_detected"] else "Clean"},
                {"label": "RAI Flags", "value": str(len(result["responsible_ai_flags"]))},
            ])

            if result["responsible_ai_flags"]:
                st.warning("Responsible AI Flags:")
                for flag in result["responsible_ai_flags"]:
                    st.markdown(f"- {flag}")

        except httpx.ConnectError:
            st.error("Cannot connect to the API. Make sure the backend is running: `make api`")
        except Exception as e:
            st.error(f"Error: {e}")

# Batch evaluation section
st.divider()
st.subheader("Batch Evaluation (Golden Q&A Pairs)")
st.markdown("Load the golden Q&A dataset and evaluate all samples against the RAG pipeline.")

if st.button("Run Batch Evaluation"):
    import json
    from pathlib import Path

    eval_path = Path("tests/evaluation/golden_qa_pairs.json")
    if not eval_path.exists():
        st.error("Golden Q&A file not found. Run from the project root directory.")
    else:
        with open(eval_path) as f:
            data = json.load(f)

        samples = [
            {
                "query": s["query"],
                "response": s["expected_answer"],
                "contexts": [s["relevant_context"]],
            }
            for s in data["samples"]
        ]

        with st.spinner(f"Evaluating {len(samples)} samples..."):
            try:
                resp = httpx.post(
                    f"{api_url}/api/v1/evaluate/batch",
                    json={"samples": samples},
                    timeout=300.0,
                )
                report = resp.json()

                st.subheader("Aggregate Report")
                render_eval_scorecard(
                    faithfulness=report["avg_faithfulness"],
                    relevance=report["avg_relevance"],
                    hallucination_rate=report["hallucination_rate"],
                )

                render_metric_row([
                    {"label": "Total Queries", "value": str(report["total_queries"])},
                    {"label": "Avg Latency", "value": f"{report['avg_latency_ms']:.0f} ms"},
                ])

                # Per-query results table
                st.subheader("Per-Query Results")
                results_df = pd.DataFrame(report["results"])
                st.dataframe(
                    results_df[["query", "faithfulness_score", "relevance_score",
                                "hallucination_detected", "latency_ms"]],
                    use_container_width=True,
                )

            except httpx.ConnectError:
                st.error("Cannot connect to the API.")
            except Exception as e:
                st.error(f"Error: {e}")
