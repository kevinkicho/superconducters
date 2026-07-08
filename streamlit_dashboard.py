import streamlit as st
import requests
import pandas as pd
import time
from typing import Optional, Dict, Any

# Cloud Lab API configuration
API_BASE_URL = st.secrets.get("CLOUD_LAB_API_URL", "http://localhost:8000/api/v1")

def fetch_experiment_status() -> Optional[pd.DataFrame]:
    """Query the cloud lab API for current experiment status."""
    try:
        response = requests.get(f"{API_BASE_URL}/experiments/status", timeout=10)
        response.raise_for_status()
        data = response.json()
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

def fetch_pipeline_status() -> Optional[pd.DataFrame]:
    """Fetch pipeline run statistics (last run, candidates processed, etc.)."""
    try:
        response = requests.get(f"{API_BASE_URL}/pipeline/status", timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return pd.DataFrame([data])
        elif isinstance(data, list):
            return pd.DataFrame(data)
        else:
            st.error("Unexpected pipeline status format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch pipeline status: {e}")
        return None

def fetch_top_candidates() -> Optional[pd.DataFrame]:
    """Fetch top candidate metrics (material, predicted Tc, etc.)."""
    try:
        response = requests.get(f"{API_BASE_URL}/candidates/top", timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "candidates" in data:
            return pd.DataFrame(data["candidates"])
        else:
            st.error("Unexpected top candidates format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch top candidates: {e}")
        return None

def fetch_experimental_results() -> Optional[pd.DataFrame]:
    """Fetch recent experimental results (measured Tc, synthesis outcome)."""
    try:
        response = requests.get(f"{API_BASE_URL}/experiments/results", timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "results" in data:
            return pd.DataFrame(data["results"])
        else:
            st.error("Unexpected experimental results format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch experimental results: {e}")
        return None

def fetch_manufacturing_progress() -> Optional[pd.DataFrame]:
    """Fetch manufacturing progress (synthesis success rate, pilot plant status)."""
    try:
        response = requests.get(f"{API_BASE_URL}/manufacturing/progress", timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return pd.DataFrame([data])
        elif isinstance(data, list):
            return pd.DataFrame(data)
        else:
            st.error("Unexpected manufacturing progress format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch manufacturing progress: {e}")
        return None

def main():
    st.set_page_config(page_title="Superconductor Pipeline Dashboard", layout="wide")
    st.title("🔬 Superconductor Research Pipeline Dashboard")
    st.markdown("Real-time monitoring of pipeline status, candidate metrics, experimental results, and manufacturing progress.")

    # Sidebar configuration
    st.sidebar.header("Settings")
    refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds)", 10, 120, 30)
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh", value=True)

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Pipeline Status",
        "Top Candidates",
        "Experimental Results",
        "Manufacturing Progress",
        "Experiment Status"
    ])

    placeholder = st.empty()

    while True:
        with placeholder.container():
            with tab1:
                st.subheader("Pipeline Status")
                df = fetch_pipeline_status()
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No pipeline status data available.")

            with tab2:
                st.subheader("Top Candidate Metrics")
                df = fetch_top_candidates()
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No top candidate data available.")

            with tab3:
                st.subheader("Experimental Results")
                df = fetch_experimental_results()
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No experimental results data available.")

            with tab4:
                st.subheader("Manufacturing Progress")
                df = fetch_manufacturing_progress()
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No manufacturing progress data available.")

            with tab5:
                st.subheader("Experiment Status")
                df = fetch_experiment_status()
                if df is not None and not df.empty:
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
