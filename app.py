import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Nurse Workforce AI Sentinel", page_icon="🏥", layout="wide"
)

st.title("🏥 Nurse Workforce AI Sentinel - Operational Dashboard")
st.markdown(
    "Phase 1 Prototype: Monitoring nurse workload, fatigue indicators, and AI"
    " warning signals."
)


@st.cache_data
def load_data():
  # Clean CSV loading now works perfectly
  df = pd.read_csv("Data/nurses.csv", encoding="utf-8")

  # Standardize column names to lowercase with underscores
  df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

  # Drop blank rows
  if "name" in df.columns:
    df = df.dropna(subset=["name"])

  # Safety fallback defaults
  defaults = {
      "risk_status": "Normal",
      "role": "Nurse",
      "unit": "General",
      "hours_worked": 0,
      "consecutive_hours": 0,
      "patient_count": 0,
      "high_acuity_count": 0,
  }
  for col, val in defaults.items():
    if col not in df.columns:
      df[col] = val

  return df


df_nurses = load_data()

# Top-Level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Nurses Monitored", len(df_nurses))
col2.metric(
    "High Risk Warnings", len(df_nurses[df_nurses["risk_status"] == "High"])
)
col3.metric("Active Units", "ICU, Emergency, Pediatrics, General")

st.markdown("---")

# Unit Overview Table
st.subheader("📋 Unit Overview & Nurse Warning List")
st.dataframe(df_nurses, use_container_width=True)

# Nurse Detail Section
st.markdown("---")
st.subheader("🔍 Nurse Detail & AI Insight Panel")

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
  st.write(f"**Risk Status:** {selected_nurse_data['risk_status']}")

with d_col2:
  st.markdown("### Operational Metrics")
  st.write(f"**Hours Worked:** {selected_nurse_data['hours_worked']} hrs")
  st.write(
      f"**Consecutive Hours:** {selected_nurse_data['consecutive_hours']} hrs"
  )
  st.write(f"**Patients Assigned:** {selected_nurse_data['patient_count']}")
  st.write(
      f"**High Acuity Patients:** {selected_nurse_data['high_acuity_count']}"
  )