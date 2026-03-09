"""Chart helper functions for Streamlit dashboards."""

import streamlit as st
import pandas as pd


def render_status_chart(status_counts: dict[str, int]) -> None:
    """Render a bar chart of claims by status."""
    df = pd.DataFrame(
        list(status_counts.items()),
        columns=["Status", "Count"],
    ).set_index("Status")
    st.bar_chart(df)


def render_category_chart(category_counts: dict[str, int]) -> None:
    """Render a bar chart of claims by procedure category."""
    df = pd.DataFrame(
        list(category_counts.items()),
        columns=["Category", "Count"],
    ).set_index("Category")
    st.bar_chart(df)


def render_anomalies_table(anomalies: list[dict]) -> None:
    """Render a table of detected billing anomalies."""
    if not anomalies:
        st.info("No billing anomalies detected.")
        return

    df = pd.DataFrame(anomalies)
    display_cols = ["claim_id", "procedure_code", "billed_amount", "typical_mean", "deviation", "reason"]
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True)
