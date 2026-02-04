import os
import networkx as nx
from itertools import combinations
from tqdm import tqdm
import gc
import json
import time
import config
from layer1_ingest import Ingestor
from layer2_curate import Curator
from layer3_neural import NeuralCore

# --- CONFIGURATION ---
ENABLE_DEEP_MESH = True 
MAX_CONCEPTS_PER_FILE = 20  # <--- THE SAFETY VALVE (Prevents RAM explosion)

# --- SMART PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Logic to find the right folder whether running from root or subfolder
if os.path.basename(BASE_DIR) == "digital_brain":
    ROOT_DIR = os.path.dirname(BASE_DIR)
else:
    ROOT_DIR = BASE_DIR
    BASE_DIR = os.path.join(ROOT_DIR, "digital_brain")

GRAPH_PATH = os.path.join(BASE_DIR, "my_personal_graph.graphml")
STATUS_PATH = os.path.join(BASE_DIR, "status.json")

def safe_save(G, filepath):
    """
    ATOMIC SAVE + RETRY LOGIC
    Prevents crashing if the App is reading the file at the same time.
    """
    temp_path = filepath + ".tmp"
    try:
        nx.write_graphml(G, temp_path)
        # Retry loop to handle Windows file locks
        for i in range(10):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                os.rename(temp_path, filepath)
                return
            except PermissionError:
                time.sleep(1) # Wait 1 sec and try again
    except Exception as e:
        print(f"⚠️ Save Warning: {e}")

def update_status(processed, total, start_time):
    """
    Updates the Timer for the Streamlit App.
    """
    elapsed = time.time() - start_time
    if processed == 0: return
    
    rate = processed / elapsed
    remaining = total - processed
    eta_seconds = remaining / rate if rate > 0 else 0
    
    if eta_seconds > 3600:
        eta_str = f"{int(eta_seconds // 3600)}h {int((eta_seconds % 3600) // 60)}m"
    else:
        eta_str = f"{int(eta_seconds // 60)} min {int(eta_seconds % 60)} sec"
        
    status_data = {
        "is_running": True,
        "progress": int((processed / total) * 100),
        "processed": processed,
        "total": total,
        "eta": eta_str
    }
    
    try:
        with open(STATUS_PATH, "w") as f:
            json.dump(status_data, f)
    except:
        pass

class Pipeline:
    def run(self):
        print(f"🚀 Starting AI Pipeline on: {config.TARGET_FOLDER}")
        print(f"🧠 Deep Mesh: ENABLED (Capped at top {MAX_CONCEPTS_PER_FILE} concepts/file)")
        
        l1 = Ingestor()
        l2 = Curator()
        l3 = NeuralCore()
        
        # Load Existing Brain
        if os.path.exists(GRAPH_PATH):
            print(f"📂 Found existing brain. Loading...")
            try:
                G = nx.read_graphml(GRAPH_PATH)
                print(f"   - Loaded {G.number_of_nodes()} nodes.")
            except:
                G = nx.Graph()
        else:
            G = nx.Graph()

        # Scan Files
        print("📊 Scanning files...")
        all_files = []
        for root, _, files in os.walk(config.TARGET_FOLDER):
            for filename in files:
                if filename.split('.')[-1].lower() in config.VALID_EXTENSIONS:
                    all_files.append(os.path.join(root, filename))
        
        total_files = len(all_files)
        print(f"✅ Found {total_files} files.")
        
        processed_count = 0
        start_time = time.time()
        
        try:
            pbar = tqdm(all_files, desc="🧠 Syncing", unit="file", ncols=100)
            
            for path in pbar:
                filename = os.path.basename(path)
                
                try:
                    # 1. DELTA CHECK (Skip unchanged)
                    current_mtime = str(os.path.getmtime(path))
                    if G.has_node(filename) and G.nodes[filename].get('mtime') == current_mtime:
                        processed_count += 1
                        if processed_count % 200 == 0:
                            update_status(processed_count, total_files, start_time)
                        continue 

                    # 2. PROCESS NEW FILE
                    raw = l1.read(path, filename.split('.')[-1].lower())
                    clean = l2.cleanse(raw)
                    concepts = l3.extract_concepts(clean)

                    if concepts:
                        # SAFETY VALVE: Only keep top 20 concepts to prevent RAM crash
                        concepts = concepts[:MAX_CONCEPTS_PER_FILE]

                        G.add_node(filename, type='File', path=path, mtime=current_mtime)
                        for c in concepts:
                            if not G.has_node(c): G.add_node(c, type='Concept')
                            G.add_edge(filename, c, weight=1)
                        
                        # 3. DEEP MESH LINKING (Safe)
                        if ENABLE_DEEP_MESH:
                            for c1, c2 in combinations(concepts, 2):
                                if G.has_edge(c1, c2): G[c1][c2]['weight'] += 0.5
                                else: G.add_edge(c1, c2, weight=0.5)

                    processed_count += 1

                    # 4. AUTOSAVE (Every 50 files)
                    if processed_count % 50 == 0:
                        safe_save(G, GRAPH_PATH)
                        update_status(processed_count, total_files, start_time)
                        gc.collect()

                except Exception:
                    pass

        except KeyboardInterrupt:
            print("\n🛑 PAUSED BY USER. Saving...")
        
        finally:
            safe_save(G, GRAPH_PATH)
            with open(STATUS_PATH, "w") as f:
                json.dump({"is_running": False, "progress": 100, "eta": "Done"}, f)
            print(f"✅ Saved. Total Processed: {processed_count}")

if __name__ == "__main__":
    Pipeline().run()