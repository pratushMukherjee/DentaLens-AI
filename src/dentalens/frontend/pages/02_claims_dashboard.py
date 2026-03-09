"""Claims Dashboard page — interactive analytics on dental claims data."""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[4]
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

import httpx
import streamlit as st

from dentalens.frontend.components.charts import (
    render_anomalies_table,
    render_category_chart,
    render_status_chart,
)
from dentalens.frontend.components.metrics_cards import render_metric_row

st.title("📊 Claims Dashboard")
st.caption("Analytics and anomaly detection on dental claims data")

api_url = st.session_state.get("api_base_url", "http://localhost:8000")


@st.cache_data(ttl=60)
def fetch_summary(url: str) -> dict | None:
    try:
        resp = httpx.get(f"{url}/api/v1/claims/analysis/summary", timeout=10.0)
        return resp.json()
    except Exception:
        return None


@st.cache_data(ttl=60)
def fetch_anomalies(url: str) -> list | None:
    try:
        resp = httpx.get(f"{url}/api/v1/claims/analysis/anomalies", timeout=10.0)
        return resp.json()
    except Exception:
        return None


# Fetch data
summary = fetch_summary(api_url)
anomalies = fetch_anomalies(api_url)

if summary is None:
    st.error("Cannot connect to the API. Make sure the backend is running: `make api`")
    st.stop()

# Summary metrics
st.subheader("Overview")
render_metric_row([
    {"label": "Total Claims", "value": f"{summary['total_claims']:,}"},
    {"label": "Total Billed", "value": f"${summary['total_billed']:,.0f}"},
    {"label": "Total Paid", "value": f"${summary['total_paid']:,.0f}"},
    {"label": "Approval Rate", "value": f"{summary['approval_rate']:.1%}"},
])

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Claims by Status")
    render_status_chart(summary.get("status_counts", {}))

with col2:
    st.subheader("Claims by Procedure Category")
    render_category_chart(summary.get("category_counts", {}))

st.divider()

# Anomalies
st.subheader("⚠️ Billing Anomalies")
if anomalies:
    st.warning(f"{len(anomalies)} potential billing anomalies detected")
    render_anomalies_table(anomalies)
else:
    st.success("No billing anomalies detected")

# Additional metrics
st.divider()
st.subheader("Cost Analysis")
render_metric_row([
    {"label": "Avg Billed per Claim", "value": f"${summary['avg_billed']:,.2f}"},
    {"label": "Avg Paid per Claim", "value": f"${summary['avg_paid']:,.2f}"},
    {
        "label": "Avg Patient Responsibility",
        "value": f"${summary['avg_billed'] - summary['avg_paid']:,.2f}",
    },
    {
        "label": "Anomalies Detected",
        "value": f"{len(anomalies) if anomalies else 0}",
    },
])
