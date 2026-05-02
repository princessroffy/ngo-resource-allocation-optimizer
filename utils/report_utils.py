"""Report and download helpers for the Streamlit app."""

from __future__ import annotations

import pandas as pd

from utils.allocation_utils import FULL_SUPPORT, PARTIAL_SUPPORT, program_allocation_summary


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def selected_beneficiaries(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["allocation_status"].isin([FULL_SUPPORT, PARTIAL_SUPPORT])].copy()


def waitlisted_beneficiaries(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["allocation_status"].isin(["Waitlisted", "Outside Focus"])].copy()


def allocation_summary_csv(df: pd.DataFrame) -> pd.DataFrame:
    return program_allocation_summary(df)


def recommendation_text(df: pd.DataFrame, metrics: dict[str, float]) -> str:
    supported = int(metrics["supported_beneficiaries"])
    total = int(metrics["total_beneficiaries"])
    budget = metrics["available_budget"]
    gap = metrics["funding_gap"]

    program_summary = program_allocation_summary(df)
    top_programs = program_summary.sort_values(
        ["funding_gap", "average_priority_score"],
        ascending=[False, False],
    ).head(3)
    program_lines = [
        f"{idx + 1}. {row.program_type}"
        for idx, row in enumerate(top_programs.itertuples())
    ]
    program_block = "\n".join(program_lines) if program_lines else "No eligible programs found."

    return (
        f"Based on the available budget of NGN {budget:,.0f}, the system recommends "
        f"supporting {supported} of {total} beneficiaries first.\n"
        "The highest need areas are:\n"
        f"{program_block}\n"
        f"Additional funding of NGN {gap:,.0f} is required to support all eligible applicants.\n"
        "This funding gap represents the difference between the total requested support and the available allocation budget."
    )
