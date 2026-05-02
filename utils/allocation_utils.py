"""Allocation helpers for budget-constrained NGO support decisions."""

from __future__ import annotations

import pandas as pd


FULL_SUPPORT = "Full Support"
PARTIAL_SUPPORT = "Partial Support"
WAITLISTED = "Waitlisted"
OUTSIDE_FOCUS = "Outside Focus"


def _priority_order(df: pd.DataFrame) -> pd.Index:
    return df.sort_values(
        by=["priority_score", "urgency_score", "impact_score", "estimated_need"],
        ascending=[False, False, False, True],
    ).index


def _allocate_order(
    result: pd.DataFrame,
    order: pd.Index,
    budget: float,
    min_partial_ratio: float,
    allow_partial: bool = True,
) -> float:
    remaining = float(max(budget, 0))

    for idx in order:
        need = float(result.at[idx, "estimated_need"])
        already_allocated = float(result.at[idx, "recommended_support_amount"])
        outstanding_need = max(need - already_allocated, 0)

        if outstanding_need <= 0 or remaining <= 0:
            continue

        if remaining >= outstanding_need:
            result.at[idx, "recommended_support_amount"] = need
            result.at[idx, "allocation_status"] = FULL_SUPPORT
            remaining -= outstanding_need
            continue

        minimum_partial = need * min_partial_ratio
        if allow_partial and already_allocated == 0 and remaining >= minimum_partial:
            result.at[idx, "recommended_support_amount"] = remaining
            result.at[idx, "allocation_status"] = PARTIAL_SUPPORT
            remaining = 0
            break

    return remaining


def allocate_resources(
    scored_df: pd.DataFrame,
    available_budget: float,
    focus_programs: list[str] | None = None,
    method: str = "Priority first",
    min_partial_ratio: float = 0.5,
) -> pd.DataFrame:
    """Recommend support amounts under the available budget."""
    result = scored_df.copy()
    budget = float(max(available_budget, 0))
    min_partial_ratio = max(0.1, min(float(min_partial_ratio), 1.0))

    result["recommended_support_amount"] = 0.0
    result["allocation_status"] = WAITLISTED

    if focus_programs:
        focus_set = set(focus_programs)
        eligible_mask = result["program_type"].isin(focus_set)
        result.loc[~eligible_mask, "allocation_status"] = OUTSIDE_FOCUS
    else:
        eligible_mask = pd.Series(True, index=result.index)

    eligible = result.loc[eligible_mask]
    if eligible.empty or budget <= 0:
        result["funding_gap"] = (result["estimated_need"] - result["recommended_support_amount"]).clip(lower=0)
        return result

    if method == "Balanced by program":
        program_weights = (
            eligible.assign(weight=eligible["priority_score"] * eligible["estimated_need"])
            .groupby("program_type")["weight"]
            .sum()
        )
        total_weight = program_weights.sum()
        remaining_total = budget

        if total_weight > 0:
            for program, weight in program_weights.items():
                program_budget = budget * (weight / total_weight)
                program_order = _priority_order(result.loc[eligible_mask & (result["program_type"] == program)])
                leftover = _allocate_order(result, program_order, program_budget, min_partial_ratio)
                remaining_total -= program_budget - leftover

        waitlisted_order = _priority_order(
            result.loc[eligible_mask & (result["allocation_status"] == WAITLISTED)]
        )
        _allocate_order(result, waitlisted_order, remaining_total, min_partial_ratio)
    else:
        order = _priority_order(eligible)
        _allocate_order(result, order, budget, min_partial_ratio)

    result["funding_gap"] = (result["estimated_need"] - result["recommended_support_amount"]).clip(lower=0)
    return result.sort_values(
        by=["allocation_status", "priority_score", "estimated_need"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def summarize_allocation(allocated_df: pd.DataFrame, available_budget: float) -> dict[str, float]:
    total_requested = float(allocated_df["estimated_need"].sum())
    total_allocated = float(allocated_df["recommended_support_amount"].sum())
    supported_count = int(allocated_df["allocation_status"].isin([FULL_SUPPORT, PARTIAL_SUPPORT]).sum())
    waitlisted_count = int((allocated_df["allocation_status"] == WAITLISTED).sum())

    return {
        "total_beneficiaries": int(len(allocated_df)),
        "available_budget": float(available_budget),
        "total_requested": total_requested,
        "total_allocated": total_allocated,
        "remaining_balance": float(max(available_budget - total_allocated, 0)),
        "funding_gap": float(max(total_requested - total_allocated, 0)),
        "supported_beneficiaries": supported_count,
        "waitlisted_beneficiaries": waitlisted_count,
    }


def program_allocation_summary(allocated_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        allocated_df.groupby("program_type", as_index=False)
        .agg(
            beneficiaries=("beneficiary_id", "count"),
            selected_beneficiaries=(
                "allocation_status",
                lambda values: values.isin([FULL_SUPPORT, PARTIAL_SUPPORT]).sum(),
            ),
            total_requested=("estimated_need", "sum"),
            recommended_allocation=("recommended_support_amount", "sum"),
            funding_gap=("funding_gap", "sum"),
            average_priority_score=("priority_score", "mean"),
        )
        .sort_values("recommended_allocation", ascending=False)
    )
    summary["average_priority_score"] = summary["average_priority_score"].round(1)
    return summary
