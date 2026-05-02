"""Scoring helpers for the Resource Allocation Optimization Model."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


REQUIRED_COLUMNS = [
    "beneficiary_id",
    "name",
    "age",
    "gender",
    "location",
    "program_type",
    "monthly_income",
    "household_size",
    "vulnerability_level",
    "urgency_level",
    "previous_support",
    "estimated_need",
    "expected_impact",
]

OPTIONAL_COLUMNS_DEFAULTS = {
    "disability_status": "No",
    "orphan_vulnerable_status": "No",
    "health_risk_level": "Low",
    "education_status": "Not specified",
    "employment_status": "Not specified",
}

LEVEL_SCORES = {
    "high": 30,
    "medium": 20,
    "low": 10,
}

IMPACT_SCORES = {
    "high": 25,
    "medium": 15,
    "low": 5,
}

MAX_RAW_SCORE = 135


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with predictable snake_case column names."""
    normalized = df.copy()
    normalized.columns = [
        str(column).strip().lower().replace(" ", "_").replace("-", "_")
        for column in normalized.columns
    ]
    return normalized


def validate_required_columns(columns: Iterable[str]) -> list[str]:
    """List required columns that are missing from a dataset."""
    available = {str(column).strip().lower() for column in columns}
    return [column for column in REQUIRED_COLUMNS if column not in available]


def _clean_text(value: object, fallback: str = "Low") -> str:
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _clean_level(value: object, fallback: str = "Low") -> str:
    text = _clean_text(value, fallback)
    title = text.title()
    return title if title in {"High", "Medium", "Low"} else fallback


def _is_yes(value: object) -> bool:
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"yes", "y", "true", "1", "received"}


def income_need_score(monthly_income: object) -> int:
    income = pd.to_numeric(monthly_income, errors="coerce")
    if pd.isna(income):
        return 0
    if income <= 15_000:
        return 10
    if income <= 30_000:
        return 6
    if income <= 50_000:
        return 3
    return 0


def household_need_score(household_size: object) -> int:
    size = pd.to_numeric(household_size, errors="coerce")
    if pd.isna(size):
        return 0
    if size >= 7:
        return 10
    if size >= 4:
        return 6
    return 2


def support_history_score(previous_support: object) -> int:
    return -10 if _is_yes(previous_support) else 15


def special_vulnerability_score(row: pd.Series) -> int:
    score = 0
    if _is_yes(row.get("disability_status", "No")):
        score += 5
    if _is_yes(row.get("orphan_vulnerable_status", "No")):
        score += 5

    health_risk = _clean_level(row.get("health_risk_level", "Low")).lower()
    if health_risk == "high":
        score += 5
    elif health_risk == "medium":
        score += 3
    return score


def classify_priority(score: float) -> str:
    if score >= 80:
        return "Very High Priority"
    if score >= 60:
        return "High Priority"
    if score >= 40:
        return "Medium Priority"
    return "Low Priority"


def prepare_beneficiary_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean input data and fill optional fields used by the model."""
    prepared = normalize_column_names(df)

    for column, default in OPTIONAL_COLUMNS_DEFAULTS.items():
        if column not in prepared.columns:
            prepared[column] = default

    prepared["age"] = pd.to_numeric(prepared["age"], errors="coerce").fillna(0).astype(int)
    prepared["monthly_income"] = (
        pd.to_numeric(prepared["monthly_income"], errors="coerce").fillna(0).clip(lower=0)
    )
    prepared["household_size"] = (
        pd.to_numeric(prepared["household_size"], errors="coerce").fillna(1).clip(lower=1)
    )
    prepared["estimated_need"] = (
        pd.to_numeric(prepared["estimated_need"], errors="coerce").fillna(0).clip(lower=0)
    )

    for column in ["vulnerability_level", "urgency_level", "expected_impact", "health_risk_level"]:
        prepared[column] = prepared[column].apply(_clean_level)

    for column in [
        "beneficiary_id",
        "name",
        "gender",
        "location",
        "program_type",
        "previous_support",
        "disability_status",
        "orphan_vulnerable_status",
        "education_status",
        "employment_status",
    ]:
        prepared[column] = prepared[column].apply(lambda value: _clean_text(value, "Not specified"))

    return prepared


def score_beneficiaries(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate explainable priority scores and categories."""
    scored = prepare_beneficiary_data(df)

    scored["vulnerability_score"] = scored["vulnerability_level"].str.lower().map(LEVEL_SCORES).fillna(10)
    scored["urgency_score"] = scored["urgency_level"].str.lower().map(LEVEL_SCORES).fillna(10)
    scored["impact_score"] = scored["expected_impact"].str.lower().map(IMPACT_SCORES).fillna(5)
    scored["support_history_score"] = scored["previous_support"].apply(support_history_score)
    scored["income_need_score"] = scored["monthly_income"].apply(income_need_score)
    scored["household_need_score"] = scored["household_size"].apply(household_need_score)
    scored["special_vulnerability_score"] = scored.apply(special_vulnerability_score, axis=1)

    component_columns = [
        "vulnerability_score",
        "urgency_score",
        "impact_score",
        "support_history_score",
        "income_need_score",
        "household_need_score",
        "special_vulnerability_score",
    ]
    scored["raw_priority_score"] = scored[component_columns].sum(axis=1)
    scored["priority_score"] = ((scored["raw_priority_score"] / MAX_RAW_SCORE) * 100).round(1).clip(upper=100)
    scored["priority_category"] = scored["priority_score"].apply(classify_priority)

    return scored.sort_values(
        by=["priority_score", "urgency_score", "estimated_need"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
