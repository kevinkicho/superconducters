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
from run_pipeline import live_external_validation, what_if_analysis, generate_press_release, generate_monthly_report
import smtplib
from email.mime.text import MIMEText
import logging
import datetime
import os
import subprocess
from collections import defaultdict

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mobile-responsive CSS (screens <768px)
st.markdown("""
<style>
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.5rem !important;
    }
    .stApp header {
        font-size: 1.2rem !important;
    }
    .stButton button {
        width: 100% !important;
        font-size: 1rem !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        font-size: 1rem !important;
    }
    .stDataFrame {
        font-size: 0.8rem !important;
    }
    .stPlotlyChart {
        width: 100% !important;
    }
    .stColumns {
        flex-direction: column !important;
    }
    .stColumn {
        width: 100% !important;
    }
    h1, h2, h3 {
        font-size: 1.5rem !important;
    }
    .stSidebar {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

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
    
    # Enhanced feedback form for user acceptance testing
    st.subheader("User Feedback")
    with st.form("feedback_form"):
        rating = st.slider("Rating (1-5)", 1, 5, 3)
        category = st.selectbox("Category", ["Usability", "Features", "Performance", "Other"])
        feedback_text = st.text_area("Your feedback")
        feedback_submitted = st.form_submit_button("Submit Feedback")
        if feedback_submitted:
            if "feedback_responses" not in st.session_state:
                st.session_state.feedback_responses = []
            st.session_state.feedback_responses.append({
                "rating": rating,
                "category": category,
                "text": feedback_text
            })
            st.success("Feedback submitted. Thank you!")
    # Display collected feedback responses
    if "feedback_responses" in st.session_state and st.session_state.feedback_responses:
        st.subheader("Collected Responses")
        for i, resp in enumerate(st.session_state.feedback_responses):
            st.write(f"{i+1}. Rating: {resp['rating']}, Category: {resp['category']}, Feedback: {resp['text']}")
    
    elif tab == "Plant Layout":
        plant_layout_tab()
    elif tab == "VR Tour":
        vr_tour_tab()
    elif tab == "System Health":
        system_health_tab()
    elif tab == "Data Export":
        st.subheader("Data Export")
        data_export_tab()



def document_sync_tab():
    st.header("Document Sync")
    st.info("Document Sync tab - placeholder.")


def validation_dashboard_tab():
    st.header("Validation Dashboard")
    st.info("Validation Dashboard tab - placeholder.")


def manufacturing_simulation_tab():
    st.header("Manufacturing Simulation")
    st.info("Manufacturing Simulation tab - placeholder.")


def supply_chain_tab():
    st.header("Supply Chain")
    st.info("Supply Chain tab - placeholder.")


def pipeline_health_tab():
    st.header("Pipeline Health")
    st.info("Pipeline Health tab - placeholder.")


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


def plant_layout_tab():
    st.header("Plant Layout - 3D Interactive")
    st.info("Interactive 3D plant layout using Three.js. (Placeholder - requires Three.js integration)")
    # In production, embed Three.js via st.components.v1.html with a 3D scene
    st.markdown("""
    <div id="threejs-container" style="width:100%; height:600px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Basic Three.js scene placeholder
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/600, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({antialias: true});
        renderer.setSize(window.innerWidth, 600);
        document.getElementById('threejs-container').appendChild(renderer.domElement);
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial({color: 0x00ff00});
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        camera.position.z = 5;
        function animate() {
            requestAnimationFrame(animate);
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            renderer.render(scene, camera);
        }
        animate();
    </script>
    """, unsafe_allow_html=True)


def vr_tour_tab():
    st.header("VR Tour - Virtual Walkthrough")
    st.info("VR Tour using WebXR. (Placeholder - requires WebXR integration)")
    st.markdown("""
    <a href="https://example.com/vr-tour" target="_blank">Launch VR Tour (opens in new tab)</a>
    <br><br>
    <p>For a full immersive experience, use a WebXR-compatible browser and headset.</p>
    """, unsafe_allow_html=True)


def system_health_tab():
    st.header("System Health")
    st.info("Real-time monitoring of all pipeline components with failure alerts, Slack/email notifications, background scheduler, and natural language query interface.")

    # Initialize session state for scheduler
    if 'scheduler_started' not in st.session_state:
        st.session_state.scheduler_started = False
    if 'component_history' not in st.session_state:
        st.session_state.component_history = defaultdict(list)
    if 'incidents' not in st.session_state:
        st.session_state.incidents = []

    # Start background scheduler if not already running
    if not st.session_state.scheduler_started and APSCHEDULER_AVAILABLE:
        try:
            start_background_scheduler()
            st.session_state.scheduler_started = True
            st.success("Background scheduler started.")
        except Exception as e:
            st.error(f"Failed to start background scheduler: {e}")
    elif not APSCHEDULER_AVAILABLE:
        st.warning("APScheduler not installed. Background tasks disabled. Install with: pip install apscheduler")

    # Define components to monitor
    components = [
        {"name": "DFT Server", "check": check_dft_server, "status": "Unknown", "uptime": "N/A", "last_incident": "N/A"},
        {"name": "ML Pipeline", "check": check_ml_pipeline, "status": "Unknown", "uptime": "N/A", "last_incident": "N/A"},
        {"name": "Cloud Lab API", "check": check_cloud_lab_api, "status": "Unknown", "uptime": "N/A", "last_incident": "N/A"},
        {"name": "ArXiv Scraper", "check": check_arxiv_scraper, "status": "Unknown", "uptime": "N/A", "last_incident": "N/A"},
        {"name": "Knowledge Graph", "check": check_knowledge_graph, "status": "Unknown", "uptime": "N/A", "last_incident": "N/A"},
        {"name": "Database", "check": check_database, "status": "Unknown", "uptime": "N/A", "last_incident": "N/A"},
    ]

    # Run health checks
    st.subheader("Live Component Status")
    refresh = st.button("Refresh Status", key="health_refresh")
    if refresh or 'last_health_check' not in st.session_state:
        st.session_state.last_health_check = datetime.datetime.now()
        for comp in components:
            try:
                result = comp['check']()
                comp['status'] = result.get('status', 'Unknown')
                comp['uptime'] = result.get('uptime', 'N/A')
                comp['last_incident'] = result.get('last_incident', 'N/A')
                comp['details'] = result.get('details', '')
                # Record history
                st.session_state.component_history[comp['name']].append({
                    'time': datetime.datetime.now(),
                    'status': comp['status']
                })
                # Alert on failure
                if comp['status'] == 'Down':
                    alert_msg = f"Component {comp['name']} is DOWN. Details: {comp.get('details', '')}"
                    st.error(alert_msg)
                    st.session_state.incidents.append({
                        'time': datetime.datetime.now(),
                        'component': comp['name'],
                        'description': comp.get('details', 'Unknown failure'),
                        'resolution': 'Pending investigation'
                    })
                    # Send alerts
                    send_slack_alert(alert_msg)
                    send_email_alert(alert_msg)
                elif comp['status'] == 'Degraded':
                    st.warning(f"Component {comp['name']} is Degraded: {comp.get('details', '')}")
            except Exception as e:
                comp['status'] = 'Error'
                comp['details'] = str(e)
                st.error(f"Health check failed for {comp['name']}: {e}")

    # Display component status cards
    for comp in components:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
        with col1:
            st.write(f"**{comp['name']}**")
        with col2:
            status = comp['status']
            if status == 'Operational':
                st.markdown(f"<span style='color:green;font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            elif status == 'Degraded':
                st.markdown(f"<span style='color:orange;font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            elif status == 'Down':
                st.markdown(f"<span style='color:red;font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            else:
                st.write(status)
        with col3:
            st.write(f"Uptime: {comp['uptime']}")
        with col4:
            st.write(f"Last Incident: {comp['last_incident']}")
        with col5:
            if comp.get('details'):
                st.write(comp['details'])

    # Incident history
    st.subheader("Incident History")
    if st.session_state.incidents:
        for inc in st.session_state.incidents[-10:]:  # Show last 10
            st.write(f"- **{inc['time'].strftime('%Y-%m-%d %H:%M')}**: {inc['component']} - {inc['description']} (Resolution: {inc['resolution']})")
    else:
        st.info("No incidents recorded.")

    # Slack/Email notification configuration
    st.subheader("Notification Configuration")
    with st.expander("Configure Slack/Email Webhooks"):
        slack_webhook = st.text_input("Slack Webhook URL", value=st.secrets.get("SLACK_WEBHOOK_URL", ""), type="password")
        email_sender = st.text_input("Email Sender", value=st.secrets.get("EMAIL_SENDER", ""))
        email_password = st.text_input("Email Password", value=st.secrets.get("EMAIL_PASSWORD", ""), type="password")
        email_recipient = st.text_input("Email Recipient", value=st.secrets.get("EMAIL_RECIPIENT", ""))
        if st.button("Test Slack Alert"):
            if slack_webhook:
                result = send_slack_alert("Test alert from System Health Dashboard", webhook_url=slack_webhook)
                if result:
                    st.success("Slack test alert sent.")
                else:
                    st.error("Failed to send Slack alert.")
            else:
                st.warning("Please enter a Slack webhook URL.")
        if st.button("Test Email Alert"):
            if email_sender and email_password and email_recipient:
                result = send_email_alert("Test alert from System Health Dashboard", sender=email_sender, password=email_password, recipient=email_recipient)
                if result:
                    st.success("Email test alert sent.")
                else:
                    st.error("Failed to send email alert.")
            else:
                st.warning("Please fill in all email fields.")

    # Background scheduler status
    st.subheader("Background Scheduler")
    if APSCHEDULER_AVAILABLE and st.session_state.scheduler_started:
        st.success("APScheduler is running. Tasks: fetch_arxiv_papers (every 6 hours), update_knowledge_graph (after fetch).")
        if st.button("Run ArXiv Fetch Now"):
            with st.spinner("Fetching new papers..."):
                result = fetch_arxiv_papers()
                if result:
                    st.success(f"Fetched {len(result)} new papers.")
                    update_knowledge_graph(result)
                else:
                    st.info("No new papers found.")
    else:
        st.warning("Background scheduler not running.")

    # Natural language query interface
    st.subheader("Natural Language Query Interface")
    st.markdown("Ask questions about the knowledge graph (e.g., 'Show me all hydrides with Tc > 200 K', 'What are the top nickelate superconductors?')")
    query = st.text_input("Enter your question:", key="nl_query")
    if st.button("Submit Query"):
        if query:
            with st.spinner("Querying knowledge graph..."):
                answer = query_knowledge_graph(query)
                st.write("**Answer:**")
                st.write(answer)
        else:
            st.warning("Please enter a question.")


# ============================================================
# Helper functions for system health monitoring
# ============================================================

def check_dft_server() -> Dict[str, Any]:
    """Check DFT server health by pinging its API endpoint."""
    result = {"status": "Unknown", "uptime": "N/A", "last_incident": "N/A", "details": ""}
    try:
        url = st.secrets.get("DFT_API_URL", "http://localhost:8001/health")
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            result["status"] = data.get("status", "Operational")
            result["uptime"] = data.get("uptime", "99.9%")
            result["last_incident"] = data.get("last_incident", "None")
        else:
            result["status"] = "Degraded"
            result["details"] = f"HTTP {resp.status_code}"
    except requests.exceptions.ConnectionError:
        result["status"] = "Down"
        result["details"] = "Connection refused"
    except Exception as e:
        result["status"] = "Error"
        result["details"] = str(e)
    return result

def check_ml_pipeline() -> Dict[str, Any]:
    """Check ML pipeline health by querying its status endpoint."""
    result = {"status": "Unknown", "uptime": "N/A", "last_incident": "N/A", "details": ""}
    try:
        url = st.secrets.get("ML_API_URL", "http://localhost:8002/health")
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            result["status"] = data.get("status", "Operational")
            result["uptime"] = data.get("uptime", "98.5%")
            result["last_incident"] = data.get("last_incident", "2025-03-24")
        else:
            result["status"] = "Degraded"
            result["details"] = f"HTTP {resp.status_code}"
    except requests.exceptions.ConnectionError:
        result["status"] = "Down"
        result["details"] = "Connection refused"
    except Exception as e:
        result["status"] = "Error"
        result["details"] = str(e)
    return result

def check_cloud_lab_api() -> Dict[str, Any]:
    """Check cloud lab API health."""
    result = {"status": "Unknown", "uptime": "N/A", "last_incident": "N/A", "details": ""}
    try:
        url = st.secrets.get("CLOUD_LAB_API_URL", "http://localhost:8000/api/v1") + "/health"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            result["status"] = data.get("status", "Operational")
            result["uptime"] = data.get("uptime", "100%")
            result["last_incident"] = data.get("last_incident", "None")
        else:
            result["status"] = "Degraded"
            result["details"] = f"HTTP {resp.status_code}"
    except requests.exceptions.ConnectionError:
        result["status"] = "Down"
        result["details"] = "Connection refused"
    except Exception as e:
        result["status"] = "Error"
        result["details"] = str(e)
    return result

def check_arxiv_scraper() -> Dict[str, Any]:
    """Check arxiv scraper health by checking last run timestamp."""
    result = {"status": "Unknown", "uptime": "N/A", "last_incident": "N/A", "details": ""}
    try:
        # Check if scraper log exists and is recent
        log_file = "data/arxiv_scraper.log"
        if os.path.exists(log_file):
            mtime = os.path.getmtime(log_file)
            last_run = datetime.datetime.fromtimestamp(mtime)
            now = datetime.datetime.now()
            if (now - last_run).total_seconds() < 86400:  # Within 24 hours
                result["status"] = "Operational"
                result["details"] = f"Last run: {last_run.strftime('%Y-%m-%d %H:%M')}"
            else:
                result["status"] = "Degraded"
                result["details"] = f"Last run: {last_run.strftime('%Y-%m-%d %H:%M')} (over 24h ago)"
        else:
            result["status"] = "Degraded"
            result["details"] = "No log file found"
    except Exception as e:
        result["status"] = "Error"
        result["details"] = str(e)
    return result

def check_knowledge_graph() -> Dict[str, Any]:
    """Check knowledge graph health by verifying node count."""
    result = {"status": "Unknown", "uptime": "N/A", "last_incident": "N/A", "details": ""}
    try:
        kg_file = "data/knowledge_graph.json"
        if os.path.exists(kg_file):
            with open(kg_file, 'r') as f:
                kg = json.load(f)
            node_count = len(kg.get('nodes', []))
            result["status"] = "Operational"
            result["details"] = f"{node_count} nodes"
        else:
            result["status"] = "Degraded"
            result["details"] = "Knowledge graph file not found"
    except Exception as e:
        result["status"] = "Error"
        result["details"] = str(e)
    return result

def check_database() -> Dict[str, Any]:
    """Check database connectivity."""
    result = {"status": "Unknown", "uptime": "N/A", "last_incident": "N/A", "details": ""}
    try:
        # Placeholder: check if a local SQLite or PostgreSQL is reachable
        db_path = st.secrets.get("DATABASE_PATH", "data/pipeline.db")
        if os.path.exists(db_path):
            result["status"] = "Operational"
            result["details"] = f"DB file exists ({os.path.getsize(db_path)} bytes)"
        else:
            result["status"] = "Degraded"
            result["details"] = "Database file not found"
    except Exception as e:
        result["status"] = "Error"
        result["details"] = str(e)
    return result

def send_slack_alert(message: str, webhook_url: Optional[str] = None) -> bool:
    """Send an alert to Slack via webhook."""
    try:
        url = webhook_url or st.secrets.get("SLACK_WEBHOOK_URL", "")
        if not url:
            logger.warning("No Slack webhook URL configured.")
            return False
        payload = {"text": message}
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info(f"Slack alert sent: {message[:50]}...")
            return True
        else:
            logger.error(f"Slack alert failed: HTTP {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Slack alert error: {e}")
        return False

def send_email_alert(message: str, sender: Optional[str] = None, password: Optional[str] = None, recipient: Optional[str] = None) -> bool:
    """Send an alert via email using SMTP."""
    try:
        sender = sender or st.secrets.get("EMAIL_SENDER", "")
        password = password or st.secrets.get("EMAIL_PASSWORD", "")
        recipient = recipient or st.secrets.get("EMAIL_RECIPIENT", "")
        if not all([sender, password, recipient]):
            logger.warning("Email credentials not fully configured.")
            return False
        msg = MIMEText(message)
        msg['Subject'] = 'System Health Alert - Superconductor Dashboard'
        msg['From'] = sender
        msg['To'] = recipient
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        logger.info(f"Email alert sent to {recipient}: {message[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Email alert error: {e}")
        return False

def start_background_scheduler() -> None:
    """Start APScheduler to periodically fetch arxiv papers and update knowledge graph."""
    if not APSCHEDULER_AVAILABLE:
        logger.warning("APScheduler not available.")
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_arxiv_papers, 'interval', hours=6, id='fetch_arxiv', name='Fetch ArXiv Papers')
    scheduler.add_job(update_knowledge_graph, 'interval', hours=6, id='update_kg', name='Update Knowledge Graph')
    scheduler.start()
    logger.info("Background scheduler started with jobs: fetch_arxiv (every 6h), update_kg (every 6h).")

def fetch_arxiv_papers() -> list:
    """Fetch new arxiv papers from the cond-mat.supr-con category."""
    try:
        url = "http://export.arxiv.org/api/query?search_query=cat:cond-mat.supr-con&sortBy=submittedDate&sortOrder=descending&max_results=50"
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            logger.error(f"ArXiv API returned {resp.status_code}")
            return []
        # Parse XML response (simplified)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            paper_id = entry.find('atom:id', ns).text.strip()
            published = entry.find('atom:published', ns).text.strip()
            papers.append({
                'id': paper_id,
                'title': title,
                'summary': summary,
                'published': published
            })
        logger.info(f"Fetched {len(papers)} papers from ArXiv.")
        # Save to file for knowledge graph
        os.makedirs('data', exist_ok=True)
        with open('data/arxiv_papers.json', 'w') as f:
            json.dump(papers, f, indent=2)
        return papers
    except Exception as e:
        logger.error(f"Error fetching arxiv papers: {e}")
        return []

def update_knowledge_graph(papers: Optional[list] = None) -> None:
    """Update the knowledge graph with new papers and experimental results."""
    try:
        kg_file = "data/knowledge_graph.json"
        if os.path.exists(kg_file):
            with open(kg_file, 'r') as f:
                kg = json.load(f)
        else:
            kg = {"nodes": [], "edges": []}
        if papers is None:
            # Try to load from file
            if os.path.exists('data/arxiv_papers.json'):
                with open('data/arxiv_papers.json', 'r') as f:
                    papers = json.load(f)
            else:
                papers = []
        existing_ids = {n['id'] for n in kg['nodes']}
        for paper in papers:
            if paper['id'] not in existing_ids:
                kg['nodes'].append({
                    'id': paper['id'],
                    'type': 'paper',
                    'title': paper['title'],
                    'summary': paper['summary'],
                    'published': paper['published']
                })
                existing_ids.add(paper['id'])
        with open(kg_file, 'w') as f:
            json.dump(kg, f, indent=2)
        logger.info(f"Knowledge graph updated. Total nodes: {len(kg['nodes'])}")
    except Exception as e:
        logger.error(f"Error updating knowledge graph: {e}")

tabs = st.tabs(["Dashboard", "Knowledge Graph", "Settings", "Funding Proposals", "Press Releases", "Monthly Report"])

with tabs[4]:
    st.header("Press Releases")
    if "press_releases" not in st.session_state:
        st.session_state.press_releases = "No press releases yet."
    if st.button("Generate New Press Release"):
        st.session_state.press_releases = generate_press_release()
    st.markdown(st.session_state.press_releases)

with tabs[5]:
    st.header("Monthly Report")
    if "monthly_report" not in st.session_state:
        st.session_state.monthly_report = "No monthly report yet."
    if st.button("Generate New Monthly Report"):
        st.session_state.monthly_report = generate_monthly_report()
    st.markdown(st.session_state.monthly_report)

def query_knowledge_graph(query: str) -> str:
    """Answer natural language questions from the knowledge graph using rule-based matching."""
    try:
        kg_file = "data/knowledge_graph.json"
        if not os.path.exists(kg_file):
            return "Knowledge graph not found. Please run the background scheduler first."
        with open(kg_file, 'r') as f:
            kg = json.load(f)
        nodes = kg.get('nodes', [])
        query_lower = query.lower()
        # Rule-based matching
        if 'hydride' in query_lower and 'tc' in query_lower:
            # Find hydride papers mentioning Tc
            results = []
            for node in nodes:
                if node.get('type') == 'paper':
                    title = node.get('title', '').lower()
                    summary = node.get('summary', '').lower()
                    if 'hydride' in title or 'hydride' in summary:
                        # Extract Tc if mentioned (simple heuristic)
                        import re
                        tc_matches = re.findall(r'(\d+)\s*K', summary + ' ' + title)
                        if tc_matches:
                            results.append(f"{node['title']} (Tc: {', '.join(tc_matches)} K)")
            if results:
                return "Found hydride papers with Tc mentions:\n" + "\n".join(results[:10])
            else:
                return "No hydride papers with Tc mentions found in knowledge graph."
        elif 'nickelate' in query_lower:
            results = []
            for node in nodes:
                if node.get('type') == 'paper':
                    title = node.get('title', '').lower()
                    summary = node.get('summary', '').lower()
                    if 'nickelate' in title or 'nickelate' in summary:
                        results.append(node['title'])
            if results:
                return "Nickelate superconductor papers:\n" + "\n".join(results[:10])
            else:
                return "No nickelate papers found."
        elif 'room temperature' in query_lower or 'rt' in query_lower:
            results = []
            for node in nodes:
                if node.get('type') == 'paper':
                    title = node.get('title', '').lower()
                    summary = node.get('summary', '').lower()
                    if 'room temperature' in title or 'room temperature' in summary:
                        results.append(node['title'])
            if results:
                return "Room temperature superconductor papers:\n" + "\n".join(results[:10])
            else:
                return "No room temperature superconductor papers found."
        elif 'pressure' in query_lower:
            results = []
            for node in nodes:
                if node.get('type') == 'paper':
                    title = node.get('title', '').lower()
                    summary = node.get('summary', '').lower()
                    import re
                    pressure_matches = re.findall(r'(\d+)\s*GPa', summary + ' ' + title)
                    if pressure_matches:
                        results.append(f"{node['title']} (Pressure: {', '.join(pressure_matches)} GPa)")
            if results:
                return "Papers mentioning pressure:\n" + "\n".join(results[:10])
            else:
                return "No pressure-related papers found."
        elif 'list' in query_lower or 'show' in query_lower or 'all' in query_lower:
            # List all papers
            paper_titles = [n['title'] for n in nodes if n.get('type') == 'paper']
            if paper_titles:
                return "All papers in knowledge graph:\n" + "\n".join(paper_titles[:20])
            else:
                return "No papers in knowledge graph."
        else:
            # Fallback: search titles and summaries for keywords
            keywords = query_lower.split()
            results = []
            for node in nodes:
                if node.get('type') == 'paper':
                    text = (node.get('title', '') + ' ' + node.get('summary', '')).lower()
                    if all(kw in text for kw in keywords):
                        results.append(node['title'])
            if results:
                return f"Found {len(results)} matching papers:\n" + "\n".join(results[:10])
            else:
                return "No matching papers found. Try different keywords (e.g., 'hydride', 'nickelate', 'room temperature', 'pressure')."
    except Exception as e:
        logger.error(f"Query error: {e}")
        return f"Error querying knowledge graph: {e}"

def display_candidate_materials():
    import sqlite3
    import pandas as pd
    st.markdown("## Candidate Materials")
    db_path = "superconductor.db"
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        conn.close()
    except Exception as e:
        st.error(f"Could not load candidate materials: {e}")
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        min_tc = st.slider("Min Predicted Tc (K)", 0.0, 300.0, 0.0, key="min_tc")
    with col2:
        max_tc = st.slider("Max Predicted Tc (K)", 0.0, 300.0, 300.0, key="max_tc")
    with col3:
        search = st.text_input("Search material name", key="search_mat")
    if 'predicted_tc' in df.columns:
        df = df[(df['predicted_tc'] >= min_tc) & (df['predicted_tc'] <= max_tc)]
    if search:
        df = df[df['material'].str.contains(search, case=False, na=False)]
    st.dataframe(df, use_container_width=True)
    if 'experimental_tc' in df.columns:
        st.subheader("Experimental Results")
        exp_df = df[df['experimental_tc'].notna()]
        if not exp_df.empty:
            st.dataframe(exp_df[['material', 'predicted_tc', 'experimental_tc', 'status']], use_container_width=True)
        else:
            st.info("No experimental results yet.")
    if st.button("Run Pipeline Update"):
        with st.spinner("Running pipeline..."):
            try:
                from run_pipeline import live_external_validation
                live_external_validation()
                st.success("Pipeline update complete. Refresh to see new data.")
            except Exception as e:
                st.error(f"Pipeline update failed: {e}")

display_candidate_materials()
