import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from pathlib import Path

st.set_page_config(page_title="Smart Placement Analyzer", page_icon="🎓", layout="wide")
st.title("🎓 Smart Placement Eligibility Analyzer")
st.caption("A Set Theory based interactive placement shortlisting dashboard")

DEFAULT_FILE = Path(__file__).with_name("students.csv")

CRITERIA = {
    "CGPA": {"column": "cgpa", "kind": "min", "default": 7.5, "min": 0.0, "max": 10.0, "step": 0.1},
    "Maximum Active Backlogs": {"column": "backlogs", "kind": "max", "default": 0, "min": 0, "max": 10, "step": 1},
    "Minimum Technical Skills": {"column": "skills", "kind": "skills", "default": 2, "min": 1, "max": 20, "step": 1},
    "Attendance (%)": {"column": "attendance", "kind": "min", "default": 75, "min": 0, "max": 100, "step": 1},
    "Aptitude Score": {"column": "aptitude_score", "kind": "min", "default": 60, "min": 0, "max": 100, "step": 1},
    "Coding Score": {"column": "coding_score", "kind": "min", "default": 60, "min": 0, "max": 100, "step": 1},
    "Projects Completed": {"column": "projects_completed", "kind": "min", "default": 2, "min": 0, "max": 20, "step": 1},
    "Certifications": {"column": "certifications", "kind": "min", "default": 1, "min": 0, "max": 20, "step": 1},
    "Communication Score": {"column": "communication_score", "kind": "min", "default": 60, "min": 0, "max": 100, "step": 1},
}

st.sidebar.header("1. Student Data")
uploaded = st.sidebar.file_uploader("Upload student CSV", type=["csv"])
try:
    df = pd.read_csv(uploaded) if uploaded is not None else pd.read_csv(DEFAULT_FILE)
except Exception as e:
    st.error(f"CSV file read nahi ho paayi: {e}")
    st.stop()

required = ["student_id", "name", "department"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("CSV mein required columns missing hain: " + ", ".join(missing))
    st.stop()

for spec in CRITERIA.values():
    col = spec["column"]
    if col in df.columns and spec["kind"] != "skills":
        df[col] = pd.to_numeric(df[col], errors="coerce")
if "skills" in df.columns:
    df["skills"] = df["skills"].fillna("").astype(str)

available = [name for name, spec in CRITERIA.items() if spec["column"] in df.columns]
st.sidebar.header("2. Turn criteria ON / OFF")
st.sidebar.caption("Criteria ON/OFF karo. Venn Diagram mein exactly 3 selected criteria hi dikhaye jayenge.")
enabled = []
defaults_on = {"CGPA", "Maximum Active Backlogs", "Minimum Technical Skills"}
for name in available:
    if st.sidebar.checkbox(name, value=name in defaults_on, key=f"enable_{name}"):
        enabled.append(name)

if len(enabled) < 3:
    st.warning("Venn Diagram ke liye kam-se-kam 3 criteria ON karein.")
    st.stop()

st.sidebar.header("3. Choose exactly 3 criteria")
default_three = [x for x in ["CGPA", "Maximum Active Backlogs", "Minimum Technical Skills"] if x in enabled]
if len(default_three) < 3:
    default_three = enabled[:3]
selected = st.sidebar.multiselect(
    "Venn Diagram ke 3 criteria",
    options=enabled,
    default=default_three[:3],
    max_selections=3
)
if len(selected) != 3:
    st.info("Venn Diagram dekhne ke liye exactly 3 criteria select karein.")
    st.stop()

st.sidebar.header("4. Set thresholds")
thresholds = {}
for name in selected:
    spec = CRITERIA[name]
    if spec["kind"] == "skills":
        thresholds[name] = st.sidebar.number_input(
            f"{name} (minimum)", min_value=int(spec["min"]),
            max_value=int(spec["max"]), value=int(spec["default"]), step=1
        )
    else:
        thresholds[name] = st.sidebar.number_input(
            name, min_value=float(spec["min"]), max_value=float(spec["max"]),
            value=float(spec["default"]), step=float(spec["step"])
        )

departments = sorted(df["department"].dropna().astype(str).unique().tolist())
chosen_departments = st.sidebar.multiselect("Department filter", departments, default=departments)
filtered = df[df["department"].astype(str).isin(chosen_departments)].copy()

def criterion_mask(frame, name):
    spec = CRITERIA[name]
    col = spec["column"]
    threshold = thresholds[name]
    if spec["kind"] == "skills":
        counts = frame[col].fillna("").astype(str).apply(
            lambda value: len([x for x in value.split(";") if x.strip()])
        )
        return counts >= threshold
    values = pd.to_numeric(frame[col], errors="coerce")
    if spec["kind"] == "max":
        return values.notna() & (values <= threshold)
    return values.notna() & (values >= threshold)

masks = {name: criterion_mask(filtered, name) for name in selected}
sets = {name: set(filtered.loc[masks[name], "student_id"].astype(str)) for name in selected}
A_name, B_name, C_name = selected
A, B, C = sets[A_name], sets[B_name], sets[C_name]
eligible_ids = A & B & C
eligible_mask = filtered["student_id"].astype(str).isin(eligible_ids)
eligible = filtered[eligible_mask]

st.subheader("Placement Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Students in filter", len(filtered))
c2.metric("Meet all 3 criteria", len(eligible))
c3.metric("Do not meet all 3", len(filtered) - len(eligible))
c4.metric("Departments", filtered["department"].nunique())

st.subheader("Venn Diagram — exactly 3 selected criteria")
fig, ax = plt.subplots(figsize=(9, 6))
venn3([A, B, C], set_labels=(A_name, B_name, C_name), ax=ax)
ax.set_title("Student overlap by placement criteria")
st.pyplot(fig, use_container_width=True)
plt.close(fig)

st.subheader("Venn Region Explorer")
region_masks = {
    f"Only {A_name}": masks[A_name] & ~masks[B_name] & ~masks[C_name],
    f"Only {B_name}": ~masks[A_name] & masks[B_name] & ~masks[C_name],
    f"Only {C_name}": ~masks[A_name] & ~masks[B_name] & masks[C_name],
    f"{A_name} + {B_name} only": masks[A_name] & masks[B_name] & ~masks[C_name],
    f"{A_name} + {C_name} only": masks[A_name] & ~masks[B_name] & masks[C_name],
    f"{B_name} + {C_name} only": ~masks[A_name] & masks[B_name] & masks[C_name],
    "All 3 criteria": masks[A_name] & masks[B_name] & masks[C_name],
    "None of the 3": ~masks[A_name] & ~masks[B_name] & ~masks[C_name],
}
region_choice = st.selectbox("Select a Venn region to view students", list(region_masks.keys()))
region_students = filtered[region_masks[region_choice]]
st.caption(f"{len(region_students)} student(s) in this region")
st.dataframe(region_students, use_container_width=True, hide_index=True)

st.subheader("Eligible Students (intersection of all 3 sets)")
st.dataframe(eligible, use_container_width=True, hide_index=True)
st.download_button(
    "⬇️ Download eligible students CSV",
    data=eligible.to_csv(index=False).encode("utf-8-sig"),
    file_name="eligible_students.csv",
    mime="text/csv"
)

st.subheader("Department-wise eligible students")
if not filtered.empty:
    dept_counts = eligible.groupby("department").size().reindex(departments, fill_value=0)
    st.bar_chart(dept_counts)
else:
    st.info("Selected departments mein data nahi hai.")

with st.expander("CSV format / required columns"):
    st.write("Required identity columns: student_id, name, department.")
    st.write("Optional criterion columns: cgpa, backlogs, skills, attendance, aptitude_score, coding_score, projects_completed, certifications, communication_score.")
    st.write("A criterion checkbox tabhi dikhega jab uska matching column CSV mein ho.")
    st.write("Skills ko semicolon se separate karein, jaise Python;Java;SQL.")
