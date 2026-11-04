import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Nurse Workforce AI Sentinel", page_icon="🏥", layout="wide"
)

st.title("🏥 Nurse Workforce AI Sentinel - Operational Dashboard")
st.markdown("Phase 3 Prototype: Deterministic Signals & GenAI Orchestration Layer")


@st.cache_data
def load_and_calculate_data():
  # Load clean dataset
  df = pd.read_csv("Data/nurses.csv", encoding="utf-8")

  # Standardize column names
  df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

  if "name" in df.columns:
    df = df.dropna(subset=["name"])

  # Deterministic Signal & Risk Engine (Sprint 2)
  def evaluate_risk(row):
    signals = []
    risk_score = 0

    hours = row.get("hours_worked", 40)
    if hours > 45:
      risk_score += 2
      signals.append(f"{hours} hours worked (high overtime)")
    elif hours > 40:
      risk_score += 1
      signals.append(f"{hours} hours worked")

    consec = row.get("consecutive_hours", 8)
    if consec >= 12:
      risk_score += 2
      signals.append(f"{consec} consecutive hours")
    elif consec > 8:
      risk_score += 1

    high_acuity = row.get("high_acuity_count", 0)
    patients = row.get("patient_count", 4)
    if high_acuity >= 2:
      risk_score += 2
      signals.append(
          f"{patients} patients including {high_acuity} high-acuity"
      )
    elif patients > 5:
      risk_score += 1
      signals.append(f"{patients} patient load")

    if risk_score >= 3:
      status = "High"
    elif risk_score >= 1:
      status = "Moderate"
    else:
      status = "Normal"

    primary_signal = (
        ", ".join(signals)
        if signals
        else "Within normal operational parameters"
    )
    return pd.Series([status, primary_signal])

  df[["risk_status", "primary_signal"]] = df.apply(evaluate_risk, axis=1)
  return df


df_nurses = load_and_calculate_data()

# Top-Level Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Nurses Monitored", len(df_nurses))
col2.metric(
    "High Risk Warnings",
    len(df_nurses[df_nurses["risk_status"] == "High"]),
    delta_color="inverse",
)
col3.metric(
    "Moderate Risk", len(df_nurses[df_nurses["risk_status"] == "Moderate"])
)
col4.metric("Active Units", "ICU, Emergency, Pediatrics, General")

st.markdown("---")

# Unit Overview Table
st.subheader("📋 Unit Overview & Deterministic Warning List")
risk_filter = st.selectbox(
    "Filter by Risk Status:", ["All", "High", "Moderate", "Normal"]
)
filtered_df = (
    df_nurses
    if risk_filter == "All"
    else df_nurses[df_nurses["risk_status"] == risk_filter]
)

st.dataframe(
    filtered_df[
        [
            "name",
            "role",
            "unit",
            "hours_worked",
            "consecutive_hours",
            "patient_count",
            "high_acuity_count",
            "risk_status",
            "primary_signal",
        ]
    ],
    use_container_width=True,
)

# Nurse Detail & GenAI Insight Panel (Sprint 3)
st.markdown("---")
st.subheader("🔍 Nurse Detail & GenAI Insight Panel")

selected_nurse_name = st.selectbox(
    "Select a nurse to review details & AI synthesis:", df_nurses["name"]
)
selected_nurse_data = df_nurses[
    df_nurses["name"] == selected_nurse_name
].iloc[0]

d_col1, d_col2 = st.columns(2)

with d_col1:
  st.markdown(f"### Profile: {selected_nurse_data['name']}")
  st.write(f"**Role:** {selected_nurse_data['role']}")
  st.write(f"**Unit:** {selected_nurse_data['unit']}")
  st.write(
      f"**Experience:** {selected_nurse_data.get('experience_years', 'N/A')}"
      " years"
  )
  st.write(f"**Calculated Risk Status:** {selected_nurse_data['risk_status']}")
  st.write(f"**Hours Worked:** {selected_nurse_data['hours_worked']} hrs")
  st.write(
      f"**Consecutive Hours:** {selected_nurse_data['consecutive_hours']} hrs"
  )
  st.write(f"**Patients Assigned:** {selected_nurse_data['patient_count']}")
  st.write(
      f"**High Acuity Patients:** {selected_nurse_data['high_acuity_count']}"
  )

with d_col2:
  st.markdown("### 🧠 GenAI Operational Synthesis")

  status = selected_nurse_data["risk_status"]
  name = selected_nurse_data["name"]
  signal = selected_nurse_data["primary_signal"]

  if status == "High":
    st.error(f"**ATTENTION - {name}**\n\nPotential workload/fatigue signal detected.")
    st.markdown(f"**Why (Evidence):** {signal}.")
    st.markdown(
        "**Fact / Hypothesis Separation:** These data indicate an operational"
        " workload signal; they do not establish that the nurse is fatigued or"
        " that patient safety has been compromised."
    )
    st.markdown(
        "**Suggested Manager Corrective Measures:**\n"
        "1. Review current patient allocation and verify if one high-acuity"
        " patient can be reassigned.\n"
        "2. Confirm applicable overtime and consecutive shift limits.\n"
        "3. Check relief staffing availability for upcoming shifts."
    )
  elif status == "Moderate":
    st.warning(
        f"**NOTICE - {name}**\n\nElevated operational load detected."
    )
    st.markdown(f"**Why (Evidence):** {signal}.")
    st.markdown(
        "**Fact / Hypothesis Separation:** Moderate threshold reached; monitor"
        " trajectory over next shift."
    )
    st.markdown(
        "**Suggested Manager Corrective Measures:**\n"
        "1. Monitor shift progression.\n"
        "2. Ensure scheduled breaks are strictly observed."
    )
  else:
    st.success(
        f"**STABLE - {name}**\n\nWithin normal operational parameters."
    )
    st.markdown(f"**Evidence:** {signal}.")
    st.markdown(
        "**Suggested Manager Action:** No immediate intervention required."
    )