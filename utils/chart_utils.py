"""Plotly charts for the allocation dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.allocation_utils import FULL_SUPPORT, PARTIAL_SUPPORT


COLOR_SEQUENCE = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"]


def allocation_by_program(df: pd.DataFrame) -> go.Figure:
    grouped = (
        df.groupby("program_type", as_index=False)["recommended_support_amount"]
        .sum()
        .sort_values("recommended_support_amount", ascending=False)
    )
    fig = px.bar(
        grouped,
        x="program_type",
        y="recommended_support_amount",
        color="program_type",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={"program_type": "Program", "recommended_support_amount": "Recommended Allocation"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10), height=340)
    return fig


def priority_distribution(df: pd.DataFrame) -> go.Figure:
    order = ["Very High Priority", "High Priority", "Medium Priority", "Low Priority"]
    counts = df["priority_category"].value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["priority_category", "beneficiaries"]
    fig = px.bar(
        counts,
        x="priority_category",
        y="beneficiaries",
        color="priority_category",
        color_discrete_sequence=["#dc2626", "#f59e0b", "#2563eb", "#64748b"],
        labels={"priority_category": "Priority", "beneficiaries": "Beneficiaries"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10), height=340)
    return fig


def gender_distribution_selected(df: pd.DataFrame) -> go.Figure:
    selected = df[df["allocation_status"].isin([FULL_SUPPORT, PARTIAL_SUPPORT])]
    grouped = selected["gender"].value_counts().reset_index()
    grouped.columns = ["gender", "beneficiaries"]
    fig = px.pie(
        grouped,
        names="gender",
        values="beneficiaries",
        color_discrete_sequence=COLOR_SEQUENCE,
        hole=0.45,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=340)
    return fig


def support_status_distribution(df: pd.DataFrame) -> go.Figure:
    grouped = df["allocation_status"].value_counts().reset_index()
    grouped.columns = ["allocation_status", "beneficiaries"]
    fig = px.pie(
        grouped,
        names="allocation_status",
        values="beneficiaries",
        color_discrete_sequence=COLOR_SEQUENCE,
        hole=0.45,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=340)
    return fig


def funding_gap_by_location(df: pd.DataFrame) -> go.Figure:
    grouped = (
        df.groupby("location", as_index=False)["funding_gap"]
        .sum()
        .sort_values("funding_gap", ascending=False)
        .head(10)
    )
    fig = px.bar(
        grouped,
        x="funding_gap",
        y="location",
        orientation="h",
        color="funding_gap",
        color_continuous_scale="Reds",
        labels={"location": "Community", "funding_gap": "Funding Gap"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10), height=360)
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def requested_vs_budget(total_requested: float, available_budget: float, total_allocated: float) -> go.Figure:
    funding_gap = max(total_requested - total_allocated, 0)
    data = pd.DataFrame(
        {
            "metric": ["Requested", "Available Budget", "Allocated", "Funding Gap"],
            "amount": [total_requested, available_budget, total_allocated, funding_gap],
        }
    )
    fig = px.bar(
        data,
        x="metric",
        y="amount",
        color="metric",
        color_discrete_sequence=["#64748b", "#2563eb", "#16a34a", "#dc2626"],
        labels={"metric": "", "amount": "Amount"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10), height=340)
    return fig
