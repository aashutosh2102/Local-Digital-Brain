import networkx as nx
import os
import re
import json
import zipfile
import string
from collections import Counter
from itertools import combinations

# --- CONFIGURATION ---
TARGET_FOLDER = r"C:\Users\ajha1\Downloads\000_Organized_Workspace"  # <--- UPDATE THIS
GRAPH_FILE = "my_personal_graph.graphml"

# Stopwords to ignore (Noise filter)
STOPWORDS = set(['the', 'and', 'for', 'with', 'from', 'that', 'this', 'return', 'import', 'def', 'class', 'self', 'print', 'true', 'false', 'none', 'null', 'data', 'file', 'code', 'text', 'string', 'value', 'name', 'type', 'list', 'dict', 'json', 'html', 'body', 'head', 'div', 'span', 'width', 'height', 'style', 'font', 'main', 'args', 'kwargs', 'path', 'test', 'error'])

class DeepMeshBuilder:
    def __init__(self):
        self.G = nx.Graph() # Undirected graph for a "Mesh" feel
        self.file_count = 0

    def clean_token(self, text):
        """Normalizes text to find 'concepts'."""
        # Remove punctuation but keep underscores (important for code)
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.upper().strip()

    def extract_tokens(self, text):
        """
        Extracts 'Technical DNA': Capitalized words, Snake_Case, CamelCase.
        """
        if not text: return []
        
        # 1. Regex for "Technical Terms" (e.g., DataFactory, sales_report, IGDW)
        # Matches words with underscores OR CamelCase OR AllCaps
        tech_pattern = r'\b[a-zA-Z0-9]+_[a-zA-Z0-9_]+\b|\b[A-Z]{2,}\b|\b[A-Z][a-z]+[A-Z][a-z]+\b'
        tech_tokens = re.findall(tech_pattern, text)
        
        # 2. Standard words (frequency based)
        words = self.clean_token(text).split()
        valid_words = [w for w in words if len(w) > 3 and w.lower() not in STOPWORDS and not w.isdigit()]
        
        # Combine and count
        all_tokens = tech_tokens + valid_words
        counts = Counter(all_tokens)
        
        # Return top 20 most frequent concepts in this file
        return [word for word, count in counts.most_common(20)]

    def parse_file(self, file_path, ext):
        text = ""
        try:
            # PBIX (Power BI)
            if ext == 'pbix':
                with zipfile.ZipFile(file_path, mode='r') as z:
                    if 'Report/Layout' in z.namelist():
                        text += z.read('Report/Layout').decode('utf-16-le', errors='ignore')
            
            # IPYNB (Jupyter)
            elif ext == 'ipynb':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for cell in data.get('cells', []):
                        text += " ".join(cell.get('source', []))
            
            # Code & Text
            elif ext in ['py', 'sql', 'json', 'html', 'md', 'txt', 'csv', 'xml', 'yaml', 'js', 'css']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read(20000) # Read 20k chars
            
            # PDF (Basic Text)
            elif ext == 'pdf':
                # (Skipping robust PDF lib import to keep it simple, assumes previous method or raw read)
                with open(file_path, 'rb') as f:
                     # Fallback: Extract strings from binary (works surprisingly well for keywords)
                     text = "".join([chr(b) for b in f.read(20000) if 32 <= b < 127])

        except Exception:
            pass
        
        return self.extract_tokens(text)

    def scan(self, root_path):
        print(f"🚀 Starting Deep Mesh Scan on: {root_path}")
        
        for root, dirs, files in os.walk(root_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                ext = filename.split('.')[-1].lower()
                
                # Filter for "Brain-Worthy" files
                if ext in ['pbix', 'ipynb', 'py', 'sql', 'md', 'txt', 'csv', 'json', 'pdf', 'html']:
                    
                    # 1. Create File Node
                    file_id = filename
                    self.G.add_node(file_id, type='File', path=file_path, size=15, color='#00c0f2')
                    
                    # 2. Extract Concepts
                    concepts = self.parse_file(file_path, ext)
                    
                    # 3. Link File -> Concepts
                    for concept in concepts:
                        # Add Concept Node (if new)
                        if not self.G.has_node(concept):
                            self.G.add_node(concept, type='Concept', size=25, color='#f9a825', title=concept)
                        
                        # Link File to Concept
                        self.G.add_edge(file_id, concept, weight=1)
                    
                    # 4. (NEW) The Mesh Effect: Link Co-occurring Concepts
                    # If "IGDW" and "SQL" appear in this file, link them together!
                    if len(concepts) > 1:
                        for c1, c2 in combinations(concepts, 2):
                            if self.G.has_edge(c1, c2):
                                self.G[c1][c2]['weight'] += 0.5
                            else:
                                self.G.add_edge(c1, c2, weight=0.5)

                    self.file_count += 1
                    if self.file_count % 50 == 0: print(f"  Indexed {self.file_count} files...")

    def save(self):
        print(f"💾 Saving {self.G.number_of_nodes()} nodes to {GRAPH_FILE}...")
        nx.write_graphml(self.G, GRAPH_FILE)
        print("✅ Done! This graph is now a dense neural network.")

if __name__ == "__main__":
    builder = DeepMeshBuilder()
    builder.scan(TARGET_FOLDER)
    builder.save()