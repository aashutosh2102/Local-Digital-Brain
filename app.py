import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os
import json
import time

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Handles both root and subfolder execution context
GRAPH_FILE = os.path.join(BASE_DIR, "digital_brain", "my_personal_graph.graphml")
STATUS_FILE = os.path.join(BASE_DIR, "digital_brain", "status.json")

# Fallback if running directly from root
if not os.path.exists(os.path.dirname(GRAPH_FILE)):
    GRAPH_FILE = "digital_brain/my_personal_graph.graphml"
    STATUS_FILE = "digital_brain/status.json"

st.set_page_config(page_title="My Digital Brain", layout="wide", page_icon="🧠")
st.title("🧠 My Digital Brain")

# --- 1. LIVE STATUS DASHBOARD ---
pipeline_running = False
if os.path.exists(STATUS_FILE):
    try:
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)
        
        if status.get("is_running", False):
            pipeline_running = True
            st.info("🚀 **Brain Indexing in Progress...**")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Progress", f"{status.get('progress')}%")
            c2.metric("Files", f"{status.get('processed')} / {status.get('total')}")
            c3.metric("⏱️ ETA", status.get('eta'))
            
            st.progress(status.get('progress') / 100)
            if st.button("Refresh Status"): st.rerun()
            st.divider()
    except:
        pass

# --- 2. ROBUST LOADER ---
@st.cache_data(ttl=60)
def load_graph(file_path):
    if not os.path.exists(file_path): return None
    try: return nx.read_graphml(file_path)
    except: return None # Returns None if file is locked/writing

G = load_graph(GRAPH_FILE)

# --- 3. WAITING ROOM ---
if not G:
    if pipeline_running:
        st.warning("⏳ **Waiting for the next data batch...**")
        st.caption("The backend is writing data. Please wait a moment.")
        time.sleep(2) # Auto-wait
        st.rerun()
    else:
        st.error("📉 No Brain Database Found.")
        st.info("Run the pipeline script first!")
    st.stop()

# --- 4. APP INTERFACE ---
st.sidebar.header("🕹️ Command Center")
st.sidebar.caption(f"Brain Nodes: {len(G.nodes())}")

search_query = st.sidebar.text_input("🔍 Search", placeholder="Project, Code, Invoice...")
min_weight = st.sidebar.slider("Connection Strength", 1.0, 5.0, 1.0)
enable_physics = st.sidebar.checkbox("Enable Physics", value=True)

final_G = nx.Graph()
found_files = []

if search_query:
    matches = [n for n in G.nodes() if search_query.lower() in str(n).lower()]
    if matches:
        st.sidebar.success(f"Found {len(matches)}")
        nodes = set(matches)
        for n in matches:
            if G.nodes[n].get('type') == 'File': found_files.append(n)
            for neighbor in G.neighbors(n):
                if G[n][neighbor].get('weight', 1) >= min_weight:
                    nodes.add(neighbor)
        final_G = G.subgraph(list(nodes))
else:
    concepts = [n for n, d in G.nodes(data=True) if d.get('type') == 'Concept']
    hubs = sorted(concepts, key=lambda n: G.degree(n), reverse=True)[:40]
    final_G = G.subgraph(hubs)

# Quick Launch
if found_files:
    st.sidebar.markdown("---")
    file_to_open = st.sidebar.selectbox("Open File:", ["Select..."] + sorted(found_files))
    if file_to_open != "Select..." and st.sidebar.button("Open"):
        try:
            os.startfile(G.nodes[file_to_open].get('path', file_to_open))
        except: st.error("Could not open file.")

# Visualize
if final_G.number_of_nodes() > 0:
    net = Network(height="750px", width="100%", bgcolor="#222", font_color="white")
    net.from_nx(final_G)
    
    if enable_physics:
        net.force_atlas_2based(gravity=-100, spring_length=200)
    else:
        net.toggle_physics(False)

    for node in net.nodes:
        node['label'] = str(node['id'])[:20]
        node['color'] = '#00c0f2' if node.get('type') == 'File' else '#f9a825'
        node['size'] = 15 if node.get('type') == 'File' else 25

    try:
        path = tempfile.gettempdir()
        tmpfile = f"{path}/graph.html"
        net.save_graph(tmpfile)
        with open(tmpfile, 'r', encoding='utf-8') as f:
            components.html(f.read(), height=800)
    except: pass