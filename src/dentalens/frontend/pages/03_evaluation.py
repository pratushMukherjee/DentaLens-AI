"""Evaluation page -- model quality assessment with responsible AI metrics."""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[4]
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

import httpx
import streamlit as st
import pandas as pd

from dentalens.frontend.components.metrics_cards import render_eval_scorecard, render_metric_row
from dentalens.frontend.components.styles import BRAND, brand_header, footer, inject_styles, stat_card

inject_styles()

brand_header("Model Evaluation", "Assess RAG response quality with faithfulness, relevance, and responsible AI metrics")

api_url = st.session_state.get("api_base_url", "http://localhost:8000")

# ── Manual evaluation ──
st.markdown(
    f'<h3 style="color:{BRAND["primary_dark"]};">Evaluate a Response</h3>',
    unsafe_allow_html=True,
)
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
            st.markdown(
                f'<h3 style="color:{BRAND["primary_dark"]};">Results</h3>',
                unsafe_allow_html=True,
            )
            render_eval_scorecard(
                faithfulness=result["faithfulness_score"],
                relevance=result["relevance_score"],
                hallucination_rate=1.0 if result["hallucination_detected"] else 0.0,
            )

            detail_cols = st.columns(3, gap="medium")
            with detail_cols[0]:
                st.markdown(
                    stat_card(f"{result['latency_ms']:.0f} ms", "Latency"),
                    unsafe_allow_html=True,
                )
            with detail_cols[1]:
                hval = "Detected" if result["hallucination_detected"] else "Clean"
                st.markdown(stat_card(hval, "Hallucination"), unsafe_allow_html=True)
            with detail_cols[2]:
                st.markdown(
                    stat_card(str(len(result["responsible_ai_flags"])), "RAI Flags"),
                    unsafe_allow_html=True,
                )

            if result["responsible_ai_flags"]:
                st.warning("Responsible AI Flags:")
                for flag in result["responsible_ai_flags"]:
                    st.markdown(f"- {flag}")

        except httpx.ConnectError:
            st.error("Cannot connect to the API. Make sure the backend is running: `make api`")
        except Exception as e:
            st.error(f"Error: {e}")

# ── Batch evaluation ──
st.divider()
st.markdown(
    f'<h3 style="color:{BRAND["primary_dark"]};">Batch Evaluation</h3>',
    unsafe_allow_html=True,
)
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

                st.markdown(
                    f'<h4 style="color:{BRAND["primary"]};">Aggregate Report</h4>',
                    unsafe_allow_html=True,
                )
                render_eval_scorecard(
                    faithfulness=report["avg_faithfulness"],
                    relevance=report["avg_relevance"],
                    hallucination_rate=report["hallucination_rate"],
                )

                agg_cols = st.columns(2, gap="medium")
                with agg_cols[0]:
                    st.markdown(
                        stat_card(str(report["total_queries"]), "Total Queries"),
                        unsafe_allow_html=True,
                    )
                with agg_cols[1]:
                    st.markdown(
                        stat_card(f"{report['avg_latency_ms']:.0f} ms", "Avg Latency"),
                        unsafe_allow_html=True,
                    )

                # Per-query results table
                st.markdown(
                    f'<h4 style="color:{BRAND["primary"]};">Per-Query Results</h4>',
                    unsafe_allow_html=True,
                )
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

footer()
