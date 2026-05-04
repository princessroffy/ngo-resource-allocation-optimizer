<img width="1470" height="756" alt="Screenshot 2026-05-02 at 13 28 06" src="https://github.com/user-attachments/assets/6698c350-f631-47d7-99ba-c52426fbb73d" />


#  Resource Allocation Optimization Model

##  Overview

This project is a data-driven decision support system designed to help NGOs allocate limited resources **fairly, efficiently, and transparently**.

It uses a scoring-based approach to prioritize beneficiaries based on vulnerability, urgency, and expected impact.

---

## ❗ Problem

NGOs often face difficult questions:

- Who should receive support first?
- How do we ensure fairness?
- How do we justify allocation decisions to donors?
- How do we balance impact vs coverage?

Most decisions are:
- Manual
- Subjective
- Difficult to explain

---

##  Solution

This system introduces a **priority scoring model** that:

- Quantifies beneficiary needs
- Ranks individuals based on urgency and impact
- Allocates resources based on available budget
- Provides explainable results for transparency

---

##  Features

- 📁 Upload beneficiary dataset (CSV)
- 💰 Input available budget
- 🧠 0–100 priority scoring system
- 🎯 Priority-first allocation strategy
- ⚖️ Balanced-by-program allocation strategy
- 📊 Interactive dashboard (charts & insights)
- 📥 Downloadable CSV reports
- 📌 Status classification:
  - Fully Supported
  - Partially Supported
  - Waitlisted

---

##  Tech Stack

- Python  
- Pandas  
- Streamlit  
- Matplotlib  

---

## Live Demo:
https://ngo-resource-allocation-optimizer-hbxklg6u7v9gp4uktxxwyt.streamlit.app/

---

## Scoring Logic

Each beneficiary is assigned a priority score (0–100) based on:

Vulnerability level
Urgency of need
Previous support received
Estimated cost of support
Expected impact

---

## Example Formula (Simplified):

Priority Score = 
(0.30 × Vulnerability) +
(0.25 × Urgency) +
(0.20 × Impact) -
(0.15 × Previous Support) +
(0.10 × Cost Efficiency)

👉 This ensures decisions are data-driven and explainable

---

## Allocation Strategies

1. Priority-First Allocation
Funds highest-priority beneficiaries first
Maximizes impact

3. Balanced Allocation
Distributes resources across programs
Ensures fairness across categories

---

## Real-World Impact

This system can be used by:

NGOs for fair resource distribution
Humanitarian organizations
Social welfare programs
Public health outreach initiatives

It helps improve:

Transparency
Accountability
Donor confidence
Impact efficiency

---

## Future Improvements

AI-based predictive allocation
Multi-cycle allocation tracking
Integration with NGO databases
Web-based multi-user system

---

##  Decision Intelligence Approach

This system applies rule-based and data-driven logic to simulate real-world NGO decision-making.

Instead of relying on intuition alone, it introduces:
- Structured prioritization
- Quantifiable fairness
- Explainable allocation logic

This bridges the gap between **data science and social impact strategy**.

---

## 👩🏽‍💻 Author

Rofiyat Aliyu
AI & Data for Social Impact

---

##  How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
