import streamlit as st
import requests
import pandas as pd
import time
import asyncio
import websockets
import threading
import json
import plotly.graph_objects as go
from typing import Optional, Dict, Any
from run_pipeline import live_external_validation, what_if_analysis

class WebSocketServer:
    """Simple WebSocket server for real-time collaboration."""
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.state = {}  # shared state (plot selections, annotations)

    async def handler(self, websocket, path):
        self.clients.add(websocket)
        try:
            # Send current state to new client
            await websocket.send(json.dumps({'type': 'init', 'state': self.state}))
            async for message in websocket:
                data = json.loads(message)
                # Update state and broadcast
                if data['type'] == 'update':
                    self.state.update(data['payload'])
                    # Broadcast to all other clients
                    for client in self.clients:
                        if client != websocket:
                            try:
                                await client.send(json.dumps({'type': 'update', 'payload': data['payload']}))
                            except:
                                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)

    def start(self):
        asyncio.run(self._run())

    async def _run(self):
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # run forever

def start_websocket_server():
    ws_server = WebSocketServer()
    ws_server.start()


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

def fetch_research_literature():
    """Return a DataFrame of recent room-temperature superconductor research findings."""
    data = [
        {"Material": "H3S (Sulfur Hydride)", "Tc (K)": 203, "Pressure (GPa)": 150, "Reference": "Drozdov et al., Nature 2015", "URL": "https://doi.org/10.1038/nature14964"},
        {"Material": "LaH10 (Lanthanum Decahydride)", "Tc (K)": 250, "Pressure (GPa)": 170, "Reference": "Somayazulu et al., PRL 2019", "URL": "https://doi.org/10.1103/PhysRevLett.122.027001"},
        {"Material": "CSH (Carbonaceous Sulfur Hydride)", "Tc (K)": 287, "Pressure (GPa)": 267, "Reference": "Snider et al., Nature 2020", "URL": "https://doi.org/10.1038/s41586-020-2801-z"},
        {"Material": "LK-99 (Pb10-xCux(PO4)6O)", "Tc (K)": "Room temp (claimed)", "Pressure (GPa)": "Ambient", "Reference": "Lee et al., arXiv 2023", "URL": "https://arxiv.org/abs/2307.12008"},
    ]
    return pd.DataFrame(data)


def main():
    st.set_page_config(page_title="Superconductor Pipeline Dashboard", layout="wide")
    st.title("🔬 Superconductor Research Pipeline Dashboard")
    st.markdown("Real-time monitoring of pipeline status, candidate metrics, experimental results, and manufacturing progress.")

    # Sidebar configuration
    st.sidebar.header("Settings")
    refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds)", 10, 120, 30)
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh", value=True)

    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Pipeline Status",
        "Top Candidates",
        "Experimental Results",
        "Manufacturing Progress",
        "Experiment Status",
        "Live Monitoring",
        "What-If Analysis",
        "Research Literature"
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

            with tab6:
                st.subheader("Live Monitoring")
                validation_data = live_external_validation()
                if validation_data is not None:
                    if isinstance(validation_data, pd.DataFrame):
                        st.dataframe(validation_data, use_container_width=True)
                    else:
                        st.json(validation_data)
                else:
                    st.info("No live validation data available.")

            with tab7:
                st.subheader("What-If Analysis")
                temperature = st.slider("Temperature (K)", min_value=0, max_value=500, value=300, step=1)
                pressure = st.slider("Pressure (GPa)", min_value=0.0, max_value=100.0, value=1.0, step=0.1)
                doping = st.slider("Doping Level (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
                if st.button("Run What-If"):
                    result = what_if_analysis(temperature=temperature, pressure=pressure, doping=doping)
                    if result is not None:
                        if isinstance(result, pd.DataFrame):
                            st.dataframe(result, use_container_width=True)
                        else:
                            st.json(result)
                    else:
                        st.error("What-if analysis failed.")
            with tab8:
                st.subheader("Research Literature")
                df = fetch_research_literature()
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True)
                    st.markdown("**Sources:**")
                    for _, row in df.iterrows():
                        st.markdown(f"- [{row['Reference']}]({row['URL']})")
                else:
                    st.info("No research literature data available.")

            with tab9:
                st.subheader("Pareto Front: Tc vs. Synthesis Pressure/Cost")
                df = fetch_pareto_front()
                if df is not None and not df.empty:
                    st.scatter_chart(df, x="pressure", y="tc", color="cost", use_container_width=True)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No Pareto front data available.")

            with tab10:
                st.subheader("Uncertainty Intervals for Predicted Tc")
                df = fetch_uncertainty_intervals()
                if df is not None and not df.empty:
                    st.line_chart(df, x="material", y=["predicted_tc", "lower_bound", "upper_bound"], use_container_width=True)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No uncertainty interval data available.")

            with tab11:
                st.subheader("Status Panel")

            with st.expander("Synthesis Planner", expanded=False):
                st.subheader("Synthesis Planner")
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    candidate_material = st.text_input("Candidate Material", "LaH10")
                with col_b:
                    pressure = st.number_input("Pressure (GPa)", min_value=0.0, max_value=500.0, value=150.0, step=1.0)
                with col_c:
                    temperature = st.number_input("Temperature (K)", min_value=0.0, max_value=500.0, value=200.0, step=1.0)
                with col_d:
                    composition = st.text_input("Composition", "LaH10")
                if st.button("Predict Tc"):
                    # Placeholder for prediction logic
                    predicted_tc = 250.0  # Example value
                    uncertainty = 15.0
                    st.metric("Predicted Tc (K)", f"{predicted_tc} ± {uncertainty}")
                    st.info("Recommended next steps: Synthesize at 150 GPa and 200 K using diamond anvil cell. Measure resistivity and magnetic susceptibility.")
                else:
                    st.info("Enter parameters and click 'Predict Tc' to see results.")
                status = fetch_status_panel()
                if status is not None:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Last Arxiv Scrape", status.get("last_arxiv_scrape", "N/A"))
                    with col2:
                        st.metric("Validation Metrics", status.get("validation_metrics", "N/A"))
                    with col3:
                        st.metric("Active Learning Iteration", status.get("active_learning_iteration", "N/A"))
                    st.json(status)
                else:
                    st.info("No status panel data available.")

            if st.button("Refresh Now"):
                st.rerun()

        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
        else:
            break

def fetch_pareto_front() -> Optional[pd.DataFrame]:
    """Fetch Pareto front data (Tc vs. synthesis pressure/cost) from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/optimization/pareto", timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "points" in data:
            return pd.DataFrame(data["points"])
        else:
            st.error("Unexpected Pareto front format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch Pareto front: {e}")
        return None


def fetch_uncertainty_intervals() -> Optional[pd.DataFrame]:
    """Fetch uncertainty intervals for predicted Tc from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/predictions/uncertainty", timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "intervals" in data:
            return pd.DataFrame(data["intervals"])
        else:
            st.error("Unexpected uncertainty intervals format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch uncertainty intervals: {e}")
        return None


def fetch_status_panel() -> Optional[Dict[str, Any]]:
    """Fetch status panel data (last arxiv scrape time, validation metrics, active learning iteration)."""
    try:
        response = requests.get(f"{API_BASE_URL}/pipeline/status", timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return data
        else:
            st.error("Unexpected status panel format.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch status panel: {e}")
        return None


if __name__ == "__main__":
    # Start WebSocket server in background thread
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()
    main()

# --- Collaboration Hub Tab ---
def collaboration_hub_tab():
    st.header("Collaboration Hub")
    
    # Role-based access control
    if "user_role" not in st.session_state:
        st.session_state.user_role = "viewer"
    
    role = st.session_state.user_role
    
    # Role selector (for demo purposes)
    st.sidebar.selectbox("Select Role", ["viewer", "contributor", "admin"], key="user_role")
    
    # WebSocket connection status
    if "ws_connected" not in st.session_state:
        st.session_state.ws_connected = False
    
    # Try to connect to WebSocket server
    if not st.session_state.ws_connected:
        try:
            async def connect():
                async with websockets.connect("ws://localhost:8765") as websocket:
                    st.session_state.ws_connected = True
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    if data['type'] == 'init':
                        st.session_state.shared_state = data['state']
                    async for message in websocket:
                        data = json.loads(message)
                        if data['type'] == 'update':
                            st.session_state.shared_state.update(data['payload'])
                            st.experimental_rerun()
            threading.Thread(target=lambda: asyncio.run(connect()), daemon=True).start()
        except Exception as e:
            st.warning(f"WebSocket connection failed: {e}")
    
    # Shared plot area
    st.subheader("Shared Plot")
    candidates = fetch_top_candidates()
    if candidates is not None and not candidates.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=candidates.index,
            y=candidates.get('predicted_tc', candidates.get('Tc', [0])),
            mode='markers+text',
            text=candidates.get('formula', candidates.index),
            marker=dict(size=10, color='blue'),
            name='Candidates'
        ))
        fig.update_layout(title='Candidate Materials (Shared)', xaxis_title='Index', yaxis_title='Predicted Tc (K)')
        st.plotly_chart(fig, use_container_width=True, key="shared_plot")
    else:
        st.info("No candidate materials available.")
    
    # Annotation input (only for contributors and admins)
    if role in ["contributor", "admin"]:
        st.subheader("Add Annotation")
        annotation_text = st.text_input("Annotation text")
        if st.button("Send Annotation"):
            if st.session_state.ws_connected:
                st.success("Annotation sent (WebSocket broadcast).")
            else:
                st.error("WebSocket not connected.")
    
    # Display annotations from shared state
    st.subheader("Annotations")
    if "shared_state" in st.session_state and "annotations" in st.session_state.shared_state:
        for ann in st.session_state.shared_state["annotations"]:
            st.write(f"- {ann}")
    else:
        st.info("No annotations yet.")
    
    # Sample request form (only for contributors and admins)
    if role in ["contributor", "admin"]:
        st.subheader("Sample Request Form")
        with st.form("sample_request"):
            material = st.text_input("Material Name")
            composition = st.text_input("Composition")
            quantity = st.number_input("Quantity (g)", min_value=0.1, step=0.1)
            submitted = st.form_submit_button("Submit Request")
            if submitted:
                st.success(f"Sample request for {material} submitted.")
    else:
        st.info("You need contributor or admin role to submit sample requests.")
    
    # Feedback submission form (all roles)
    st.subheader("Feedback")
    with st.form("feedback_form"):
        feedback_text = st.text_area("Your feedback")
        feedback_submitted = st.form_submit_button("Submit Feedback")
        if feedback_submitted:
            st.success("Feedback submitted. Thank you!")
    
    # Data Export section
    st.subheader("Data Export")
    data_export_tab()



def data_export_tab():
    st.header("Data Export")
    data_type = st.selectbox("Select data to export", ["Candidate Materials", "Experimental Results"])
    if data_type == "Candidate Materials":
        df = fetch_top_candidates()
    else:
        df = fetch_experimental_results()
    if df is not None:
        st.dataframe(df)
        csv = df.to_csv(index=False)
        json_str = df.to_json(orient="records", indent=2)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download CSV", csv, file_name=f"{data_type.lower().replace(' ', '_')}.csv", mime="text/csv")
        with col2:
            st.download_button("Download JSON", json_str, file_name=f"{data_type.lower().replace(' ', '_')}.json", mime="application/json")
    else:
        st.info("No data available.")
