"""Claims Dashboard page -- interactive analytics on dental claims data."""

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
from dentalens.frontend.components.styles import BRAND, brand_header, footer, inject_styles, stat_card

inject_styles()

brand_header("Claims Dashboard", "Analytics and anomaly detection on dental claims data")

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

# ── Overview stats ──
st.markdown(
    f'<h3 style="color:{BRAND["primary_dark"]};">Overview</h3>',
    unsafe_allow_html=True,
)
stat_cols = st.columns(4, gap="medium")
stats = [
    (f"{summary['total_claims']:,}", "Total Claims"),
    (f"${summary['total_billed']:,.0f}", "Total Billed"),
    (f"${summary['total_paid']:,.0f}", "Total Paid"),
    (f"{summary['approval_rate']:.1%}", "Approval Rate"),
]
for col, (value, label) in zip(stat_cols, stats):
    with col:
        st.markdown(stat_card(value, label), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ──
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        f'<h4 style="color:{BRAND["primary"]};">Claims by Status</h4>',
        unsafe_allow_html=True,
    )
    render_status_chart(summary.get("status_counts", {}))

with col2:
    st.markdown(
        f'<h4 style="color:{BRAND["primary"]};">Claims by Procedure Category</h4>',
        unsafe_allow_html=True,
    )
    render_category_chart(summary.get("category_counts", {}))

st.divider()

# ── Anomalies ──
anomaly_count = len(anomalies) if anomalies else 0
st.markdown(
    f'<h3 style="color:{BRAND["primary_dark"]};">Billing Anomalies</h3>',
    unsafe_allow_html=True,
)
if anomalies:
    st.warning(f"{anomaly_count} potential billing anomalies detected")
    render_anomalies_table(anomalies)
else:
    st.success("No billing anomalies detected")

st.divider()

# ── Cost Analysis ──
st.markdown(
    f'<h3 style="color:{BRAND["primary_dark"]};">Cost Analysis</h3>',
    unsafe_allow_html=True,
)
cost_cols = st.columns(4, gap="medium")
cost_stats = [
    (f"${summary['avg_billed']:,.2f}", "Avg Billed / Claim"),
    (f"${summary['avg_paid']:,.2f}", "Avg Paid / Claim"),
    (f"${summary['avg_billed'] - summary['avg_paid']:,.2f}", "Avg Patient Responsibility"),
    (str(anomaly_count), "Anomalies Detected"),
]
for col, (value, label) in zip(cost_cols, cost_stats):
    with col:
        st.markdown(stat_card(value, label), unsafe_allow_html=True)

footer()
