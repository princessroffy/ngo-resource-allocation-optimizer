<img width="1470" height="756" alt="Screenshot 2026-05-02 at 13 28 06" src="https://github.com/user-attachments/assets/6698c350-f631-47d7-99ba-c52426fbb73d" />
# REI Resource Allocation Optimizer

Resource Allocation Optimization Model is a data-driven NGO decision support system designed to help nonprofit organizations allocate limited resources fairly and effectively. The system analyzes beneficiary vulnerability, urgency, previous support, estimated need, and expected impact to calculate priority scores and recommend resource distribution.

This project demonstrates how data science and AI-inspired decision logic can support transparent, accountable, and impact-driven humanitarian resource allocation.

## Features

- Upload a beneficiary CSV or use included sample data.
- Enter an available budget for the allocation cycle.
- Calculate an explainable 0-100 priority score for each beneficiary.
- Recommend full support, partial support, or waitlist status.
- Compare priority-first allocation against a balanced-by-program allocation method.
- View dashboard charts for program allocation, priority levels, gender mix, status distribution, location gaps, and budget gap.
- Download selected beneficiaries, waitlisted beneficiaries, program summaries, and full allocation results as CSV files.

## Scoring Logic

The model calculates component scores for:

- Vulnerability level
- Urgency level
- Expected impact
- Previous support history
- Monthly income pressure
- Household size pressure
- Disability status, orphan or vulnerable status, and health risk

The raw score is normalized to a 0-100 priority score:

| Score Range | Priority Category |
| --- | --- |
| 80 and above | Very High Priority |
| 60 to 79 | High Priority |
| 40 to 59 | Medium Priority |
| Below 40 | Low Priority |

## Allocation Logic

The app supports two allocation methods:

- **Priority first:** Sorts all eligible beneficiaries by priority score and allocates support until the budget is exhausted.
- **Balanced by program:** Reserves a share of the budget for each program based on weighted demand, then allocates within each program by priority.

If the remaining budget cannot fully cover the next beneficiary but can meet the minimum partial-support threshold, the app recommends partial support.

## Required CSV Columns

```csv
beneficiary_id,name,age,gender,location,program_type,monthly_income,household_size,vulnerability_level,urgency_level,previous_support,estimated_need,expected_impact
```

Optional columns are also supported:

```csv
disability_status,orphan_vulnerable_status,health_risk_level,education_status,employment_status
```

## Project Structure

```text
resource-allocation-optimization-model/
├── app.py
├── requirements.txt
├── README.md
├── sample_data.csv
├── data/
│   └── sample_beneficiaries.csv
├── utils/
│   ├── allocation_utils.py
│   ├── chart_utils.py
│   ├── report_utils.py
│   └── scoring_utils.py
├── reports/
└── assets/
```

## Run Locally

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Deployment

This app is ready for Streamlit Cloud:

1. Push the project to GitHub.
2. Create a new Streamlit Cloud app from the repository.
3. Set `app.py` as the entry file.
4. Deploy.

## Future Improvements

- PDF allocation report generation.
- Donor-specific allocation rules.
- Linear programming optimization with SciPy.
- Fairness constraints by gender, community, or program type.
- Impact forecasting and post-support outcome tracking.
