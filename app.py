import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Nurse Workforce AI Sentinel", page_icon="🏥", layout="wide"
)

st.title("🏥 Nurse Workforce AI Sentinel - Operational Dashboard")
st.markdown(
    "Phase 2 Prototype: Deterministic Signal Engine & Risk Calculation Layer"
)


@st.cache_data
def load_and_calculate_data():
  # Load clean dataset
  df = pd.read_csv("Data/nurses.csv", encoding="utf-8")

  # Standardize column names to lowercase with underscores
  df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

  # Drop blank rows
  if "name" in df.columns:
    df = df.dropna(subset=["name"])

  # Deterministic Signal & Risk Engine (Sprint 2 Requirement)
  def evaluate_risk(row):
    signals = []
    risk_score = 0

    # Hours worked / Overtime check
    hours = row.get("hours_worked", 40)
    if hours > 45:
      risk_score += 2
      signals.append(f"{hours} hours worked (high overtime)")
    elif hours > 40:
      risk_score += 1
      signals.append(f"{hours} hours worked")

    # Consecutive hours / shifts check
    consec = row.get("consecutive_hours", 8)
    if consec >= 12:
      risk_score += 2
      signals.append(f"{consec} consecutive hours")
    elif consec > 8:
      risk_score += 1

    # High acuity patient load check
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

    # Determine risk category based on score
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

# Unit Overview Table with Risk Filtering
st.subheader("📋 Unit Overview & Deterministic Warning List")

risk_filter = st.selectbox(
    "Filter by Risk Status:", ["All", "High", "Moderate", "Normal"]
)
if risk_filter != "All":
  filtered_df = df_nurses[df_nurses["risk_status"] == risk_filter]
else:
  filtered_df = df_nurses

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

# Nurse Detail Section
st.markdown("---")
st.subheader("🔍 Nurse Detail & Operational Evidence Panel")

selected_nurse_name = st.selectbox(
    "Select a nurse to review details:", df_nurses["name"]
)

selected_nurse_data = df_nurses[
    df_nurses["name"] == selected_nurse_name
].iloc[0]

# Display details side by side
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

with d_col2:
  st.markdown("### Operational Evidence & Signals")
  st.write(f"**Primary Signal:** {selected_nurse_data['primary_signal']}")
  st.write(f"**Hours Worked:** {selected_nurse_data['hours_worked']} hrs")
  st.write(
      f"**Consecutive Hours:** {selected_nurse_data['consecutive_hours']} hrs"
  )
  st.write(f"**Patients Assigned:** {selected_nurse_data['patient_count']}")
  st.write(
      f"**High Acuity Patients:** {selected_nurse_data['high_acuity_count']}"
  )