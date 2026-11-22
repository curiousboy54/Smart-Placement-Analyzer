# Project Report Outline

## Title
SMART PLACEMENT: A Set Theory Based Interactive Student Placement Eligibility Analyzer

## Objective
To help placement staff analyze student eligibility using configurable criteria and visualize the overlap of exactly three selected criteria with a Venn Diagram.

## Discrete Mathematics
Let U be the set of students in the selected department filter. Let A, B and C be the sets of students satisfying the three selected eligibility criteria.
- A ∩ B ∩ C: students satisfying all three criteria.
- A ∪ B ∪ C: students satisfying at least one criterion.
- A − B: students satisfying A but not B.
- U − A: complement of A.
The eight Venn regions represent all possible membership combinations.

## Tools
Python, Pandas, Matplotlib, matplotlib-venn and Streamlit.

## Workflow
1. Upload CSV.
2. Turn available criteria ON/OFF.
3. Select exactly three enabled criteria.
4. Set thresholds.
5. Filter departments.
6. Explore Venn regions and student records.
7. Download eligible student records.

## Limitation
This is a demonstration and shortlisting aid. Actual placement decisions must follow official employer rules and be reviewed by authorized placement staff.
