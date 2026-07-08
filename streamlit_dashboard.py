import streamlit as st
import requests
import pandas as pd
import time
from typing import Optional

# Cloud Lab API configuration
API_BASE_URL = st.secrets.get("CLOUD_LAB_API_URL", "http://localhost:8000/api/v1")

def fetch_experiment_status() -> Optional[pd.DataFrame]:
    """Query the cloud lab API for current experiment status."""
    try:
        response = requests.get(f"{API_BASE_URL}/experiments/status", timeout=10)
        response.raise_for_status()
        data = response.json()
        # Expect data to be a list of dicts with keys: timestamp, current_step, errors
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "experiments" in data:
            return pd.DataFrame(data["experiments"])
        else:
            st.error("Unexpected API response format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch experiment status: {e}")
        return None

def main():
    st.set_page_config(page_title="Real-Time Experimental Monitoring", layout="wide")
    st.title("🔬 Real-Time Experimental Monitoring")
    st.markdown("Dashboard queries the cloud lab API for live experiment status.")

    # Auto-refresh every 30 seconds or manual refresh
    refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds)", 10, 120, 30)
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh", value=True)

    placeholder = st.empty()

    while True:
        with placeholder.container():
            st.subheader("Experiment Status")
            df = fetch_experiment_status()
            if df is not None and not df.empty:
                # Ensure columns exist
                required_cols = ["timestamp", "current_step", "errors"]
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = "N/A"
                st.dataframe(df[required_cols], use_container_width=True)
            else:
                st.info("No experiment data available.")

            if st.button("Refresh Now"):
                st.rerun()

        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
        else:
            break

if __name__ == "__main__":
    main()
