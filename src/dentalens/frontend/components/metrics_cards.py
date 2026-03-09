"""Reusable metric display cards for Streamlit dashboards."""

import streamlit as st


def render_metric_row(metrics: list[dict]) -> None:
    """Render a row of metric cards.

    Each metric dict should have: label, value, and optionally delta, help.
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            col.metric(
                label=metric["label"],
                value=metric["value"],
                delta=metric.get("delta"),
                help=metric.get("help"),
            )


def render_eval_scorecard(faithfulness: float, relevance: float, hallucination_rate: float) -> None:
    """Render evaluation scores as a colored scorecard."""
    cols = st.columns(3)

    with cols[0]:
        color = "green" if faithfulness >= 0.8 else "orange" if faithfulness >= 0.6 else "red"
        st.markdown(f"### :{color}[Faithfulness: {faithfulness:.1%}]")

    with cols[1]:
        color = "green" if relevance >= 0.7 else "orange" if relevance >= 0.5 else "red"
        st.markdown(f"### :{color}[Relevance: {relevance:.1%}]")

    with cols[2]:
        color = "green" if hallucination_rate <= 0.1 else "orange" if hallucination_rate <= 0.2 else "red"
        st.markdown(f"### :{color}[Hallucination: {hallucination_rate:.1%}]")
