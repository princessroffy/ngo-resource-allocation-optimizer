from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.allocation_utils import allocate_resources, program_allocation_summary, summarize_allocation
from utils.chart_utils import (
    allocation_by_program,
    funding_gap_by_location,
    gender_distribution_selected,
    priority_distribution,
    requested_vs_budget,
    support_status_distribution,
)
from utils.report_utils import (
    allocation_summary_csv,
    recommendation_text,
    selected_beneficiaries,
    to_csv_bytes,
    waitlisted_beneficiaries,
)
from utils.scoring_utils import normalize_column_names, score_beneficiaries, validate_required_columns


BASE_DIR = Path(__file__).parent
SAMPLE_DATA_PATH = BASE_DIR / "data" / "sample_beneficiaries.csv"


st.set_page_config(
    page_title="REI Resource Allocation Optimizer",
    page_icon="R",
    layout="wide",
)


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_DATA_PATH)


def money(value: float) -> str:
    return f"NGN {value:,.0f}"


def render_metric(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label=label, value=value, help=help_text)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stMetricLabel"] {
        color: #475569;
    }
    .recommendation-box {
        border-left: 4px solid #2563eb;
        background: #f8fafc;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        white-space: pre-line;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.title("REI Optimizer")
ngo_name = st.sidebar.text_input(
    "NGO name", value="Rofiyat Empowerment Initiative")
uploaded_file = st.sidebar.file_uploader(
    "Upload beneficiary CSV", type=["csv"])
available_budget = st.sidebar.number_input(
    "Available budget",
    min_value=0,
    value=500_000,
    step=25_000,
    help="Budget available for this allocation cycle.",
)
allocation_method = st.sidebar.selectbox(
    "Allocation method",
    options=["Priority first", "Balanced by program"],
    help="Priority first ranks all beneficiaries together. Balanced by program reserves budget by program demand and priority.",
)
min_partial_ratio = (
    st.sidebar.slider(
        "Minimum partial support",
        min_value=10,
        max_value=100,
        value=50,
        step=5,
        help="A partial allocation is only recommended if the remaining budget can cover at least this share of the person's estimated need.",
    )
    / 100
)


if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    data_source_label = uploaded_file.name
else:
    raw_df = load_sample_data()
    data_source_label = "sample_beneficiaries.csv"

normalized_df = normalize_column_names(raw_df)
missing_columns = validate_required_columns(normalized_df.columns)

if missing_columns:
    st.error(
        "The uploaded CSV is missing required columns: "
        + ", ".join(f"`{column}`" for column in missing_columns)
    )
    st.info("Use the included sample data as a template for the expected format.")
    st.stop()

scored_df = score_beneficiaries(normalized_df)
programs = sorted(scored_df["program_type"].dropna().unique())
focus_programs = st.sidebar.multiselect(
    "Program focus",
    options=programs,
    default=programs,
    help="Select one or more programs to include in this allocation run.",
)
focus_arg = None if not focus_programs or set(
    focus_programs) == set(programs) else focus_programs

allocated_df = allocate_resources(
    scored_df=scored_df,
    available_budget=float(available_budget),
    focus_programs=focus_arg,
    method=allocation_method,
    min_partial_ratio=min_partial_ratio,
)
metrics = summarize_allocation(allocated_df, float(available_budget))
program_summary = program_allocation_summary(allocated_df)


st.title("REI Resource Allocation Optimizer")
st.markdown("**NGO decision support tool**")
st.caption(
    "A data-driven decision support tool for fair and transparent NGO resource distribution.")

top_bar_left, top_bar_right = st.columns([0.68, 0.32])
with top_bar_left:
    st.write(f"**Organization:** {ngo_name}")
    st.write(f"**Dataset:** {data_source_label}")
with top_bar_right:
    with st.expander("Scoring model"):
        st.write(
            "Priority score uses vulnerability, urgency, expected impact, previous support, "
            "income pressure, household size, disability or orphan status, and health risk."
        )
        st.write(
            "Scores are normalized to 0-100, then classified into low, medium, high, and very high priority.")


metric_cols = st.columns(6)
with metric_cols[0]:
    render_metric("Beneficiaries", f"{metrics['total_beneficiaries']:,.0f}")
with metric_cols[1]:
    render_metric("Budget", money(metrics["available_budget"]))
with metric_cols[2]:
    render_metric("Requested", money(metrics["total_requested"]))
with metric_cols[3]:
    render_metric("Supported", f"{metrics['supported_beneficiaries']:,.0f}")
with metric_cols[4]:
    render_metric("Waitlisted", f"{metrics['waitlisted_beneficiaries']:,.0f}")
with metric_cols[5]:
    render_metric(
        "Funding gap",
        money(metrics["funding_gap"]),
        "This funding gap represents the difference between the total requested support and the available allocation budget",
    )
    st.caption(
        "This funding gap represents the difference between the total requested support and the available allocation budget"
    )


st.subheader("Beneficiary priority and allocation")
display_columns = [
    "beneficiary_id",
    "name",
    "gender",
    "location",
    "program_type",
    "vulnerability_level",
    "urgency_level",
    "expected_impact",
    "priority_score",
    "priority_category",
    "estimated_need",
    "recommended_support_amount",
    "funding_gap",
    "allocation_status",
]
st.dataframe(
    allocated_df[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "priority_score": st.column_config.ProgressColumn(
            "Priority Score",
            help="Normalized priority score from 0 to 100.",
            min_value=0,
            max_value=100,
            format="%.1f",
        ),
        "estimated_need": st.column_config.NumberColumn("Estimated Need", format="NGN %.0f"),
        "recommended_support_amount": st.column_config.NumberColumn(
            "Recommended Support", format="NGN %.0f"
        ),
        "funding_gap": st.column_config.NumberColumn("Funding Gap", format="NGN %.0f"),
    },
)


st.subheader("Recommended allocation dashboard")
chart_tab, equity_tab, gap_tab = st.tabs(
    ["Program allocation", "Beneficiary mix", "Funding gap"])

with chart_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(allocation_by_program(
            allocated_df), use_container_width=True)
    with c2:
        st.plotly_chart(priority_distribution(
            allocated_df), use_container_width=True)

with equity_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(gender_distribution_selected(
            allocated_df), use_container_width=True)
    with c2:
        st.plotly_chart(support_status_distribution(
            allocated_df), use_container_width=True)

with gap_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(funding_gap_by_location(
            allocated_df), use_container_width=True)
    with c2:
        st.plotly_chart(
            requested_vs_budget(
                metrics["total_requested"],
                metrics["available_budget"],
                metrics["total_allocated"],
            ),
            use_container_width=True,
        )


st.subheader("Program-level allocation")
st.dataframe(
    program_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "total_requested": st.column_config.NumberColumn("Total Requested", format="NGN %.0f"),
        "recommended_allocation": st.column_config.NumberColumn(
            "Recommended Allocation", format="NGN %.0f"
        ),
        "funding_gap": st.column_config.NumberColumn("Funding Gap", format="NGN %.0f"),
        "average_priority_score": st.column_config.NumberColumn("Average Priority", format="%.1f"),
    },
)


st.subheader("Final recommendation")
st.markdown(
    f"<div class='recommendation-box'>{recommendation_text(allocated_df, metrics)}</div>",
    unsafe_allow_html=True,
)


st.subheader("Download CSV reports")
download_cols = st.columns(4)

selected_df = selected_beneficiaries(allocated_df)
waitlisted_df = waitlisted_beneficiaries(allocated_df)
summary_df = allocation_summary_csv(allocated_df)

with download_cols[0]:
    st.download_button(
        "Selected beneficiaries",
        data=to_csv_bytes(selected_df),
        file_name="selected_beneficiaries.csv",
        mime="text/csv",
        use_container_width=True,
    )
with download_cols[1]:
    st.download_button(
        "Waitlisted beneficiaries",
        data=to_csv_bytes(waitlisted_df),
        file_name="waitlisted_beneficiaries.csv",
        mime="text/csv",
        use_container_width=True,
    )
with download_cols[2]:
    st.download_button(
        "Allocation summary",
        data=to_csv_bytes(summary_df),
        file_name="allocation_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )
with download_cols[3]:
    st.download_button(
        "Full allocation table",
        data=to_csv_bytes(allocated_df),
        file_name="full_allocation_results.csv",
        mime="text/csv",
        use_container_width=True,
    )
