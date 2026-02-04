import networkx as nx
import spacy
from PyPDF2 import PdfReader
import os
import re
import json
import zipfile
import io
from collections import Counter

# --- CONFIGURATION ---
GRAPH_FILE = "my_personal_graph.graphml"

# Load Spacy for standard entities (People/Orgs)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- 1. THE UNIVERSAL READER (Cracks open complex formats) ---
def read_pbix(file_path):
    """
    HACK: PBIX files are just ZIP archives. We open them and read the 'Layout' file
    to find Page Names, Visual Titles, and Table references.
    """
    text_content = ""
    try:
        with zipfile.ZipFile(file_path, mode='r') as z:
            # 1. Try to read the Layout (Visuals & Pages)
            if 'Report/Layout' in z.namelist():
                # PBIX internals are often UTF-16
                layout_json = z.read('Report/Layout').decode('utf-16-le', errors='ignore')
                text_content += layout_json
            
            # 2. Try to read the DataModel (Table/Column names) - Limit size
            if 'DataModelSchema' in z.namelist():
                schema = z.read('DataModelSchema').decode('utf-16-le', errors='ignore')
                text_content += schema[:50000] # Limit to first 50k chars to save RAM
    except Exception as e:
        print(f"  [!] Could not parse PBIX {os.path.basename(file_path)}: {e}")
    return text_content

def read_notebook(file_path):
    """Parses Jupyter Notebooks (.ipynb) by extracting code and markdown cells."""
    text_content = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for cell in data.get('cells', []):
                # Join lines in the cell
                cell_text = " ".join(cell.get('source', []))
                text_content += cell_text + " "
    except:
        pass
    return text_content

def read_code_or_text(file_path):
    """Reads raw text from .py, .sql, .html, .md, .txt, .csv"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(10000) # Read first 10k chars
    except:
        return ""

def read_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages[:5]: # Read first 5 pages
            text += page.extract_text() or ""
    except:
        pass
    return text

def extract_content(file_path, ext):
    """Router to send file to the correct parser."""
    text = ""
    if ext == 'pbix':
        text = read_pbix(file_path)
    elif ext == 'ipynb':
        text = read_notebook(file_path)
    elif ext == 'pdf':
        text = read_pdf(file_path)
    elif ext in ['py', 'sql', 'html', 'css', 'js', 'json', 'md', 'txt', 'csv', 'xml', 'yaml', 'yml']:
        text = read_code_or_text(file_path)
    
    # Cleaning: Remove HTML tags if present
    if ext in ['html', 'pbix', 'ipynb']:
        text = re.sub(r'<[^<]+?>', ' ', text)
    
    return text.lower()

# --- 2. THE TECHNICAL TOKENIZER (Finds "IGDW", "Table_Sales", etc.) ---
def extract_technical_tokens(text):
    """
    Aggressive tokenizer. Ignores English sentences, looks for 'Variables', 'Codes', 'Project Names'.
    """
    # 1. Split by anything that isn't a letter or number
    # This turns "Project_IGDW-v2.0" into ["Project", "IGDW", "v2", "0"]
    raw_tokens = re.split(r'[^a-zA-Z0-9_]', text)
    
    # 2. Filter for "Interesting" words
    clean_tokens = []
    stopwords = {'the', 'and', 'for', 'with', 'from', 'that', 'this', 'return', 'import', 'def', 'class', 'self', 'print', 'true', 'false', 'none', 'null', 'data', 'file', 'code', 'text', 'string', 'value', 'name', 'type', 'list', 'dict', 'json', 'html', 'body', 'head', 'div', 'span', 'width', 'height', 'style', 'font'}
    
    for t in raw_tokens:
        t = t.strip()
        # Rule: Must be 3+ chars, not a number, not a stopword
        if len(t) > 3 and not t.isdigit() and t not in stopwords:
            clean_tokens.append(t)
            
    # 3. Frequency Analysis (The "Smart" Part)
    # Only keep words that appear multiple times (implies importance) OR look like code (has underscore)
    counts = Counter(clean_tokens)
    
    important_keywords = set()
    for word, count in counts.items():
        # If it has an underscore (e.g. 'sales_data'), it's definitely technical -> Keep it
        if '_' in word:
            important_keywords.add(word)
        # If it appears frequently in the file (e.g. 'IGDW' appears 5 times) -> Keep it
        elif count >= 3:
            important_keywords.add(word)
        # If it's all caps (acronym) -> Keep it
        elif word.isupper() and len(word) > 2:
            important_keywords.add(word)

    return list(important_keywords)[:15] # Return top 15 concepts per file

# --- 3. THE CONNECTOR ENGINE ---
def main():
    print(f"Loading {GRAPH_FILE}...")
    G = nx.read_graphml(GRAPH_FILE)
    
    print("🧠 Starting Universal Brain Scan...")
    print("   (This will parse PBIX, IPYNB, PDF, Code, and Text)")
    
    count = 0
    new_edges = 0
    
    nodes_list = list(G.nodes(data=True))
    for node, data in nodes_list:
        if data.get('type') == 'File':
            ext = data.get('extension', '')
            file_path = data.get('path', node)
            
            # 1. READ CONTENT
            # We now support almost ALL text-bearing files
            supported_exts = ['pbix', 'ipynb', 'pdf', 'py', 'sql', 'html', 'md', 'txt', 'csv', 'json', 'xml', 'js', 'css', 'yaml']
            
            if ext in supported_exts:
                text = extract_content(file_path, ext)
                if not text: continue
                
                # 2. EXTRACT TOKENS
                # Use "Technical Tokenizer" instead of just NLP
                tokens = extract_technical_tokens(text)
                
                # Also run standard NLP for People/Orgs (Optional, adds context)
                if len(text) < 100000: # Limit for spaCy speed
                    doc = nlp(text[:10000])
                    for ent in doc.ents:
                        if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                            clean = re.sub(r'[^a-zA-Z0-9]', '', ent.text).lower()
                            if len(clean) > 3: tokens.append(clean)

                # 3. CREATE CONNECTIONS
                # Dedup tokens
                unique_topics = list(set([t.upper() for t in tokens]))
                
                if unique_topics:
                    for topic in unique_topics:
                        topic_id = f"TOPIC_{topic}"
                        
                        # Add Topic Node (Yellow Bubble)
                        if not G.has_node(topic_id):
                            G.add_node(topic_id, label=topic, type='Topic', size=15)
                        
                        # Add Edge: File <-> Topic
                        if not G.has_edge(node, topic_id):
                            G.add_edge(node, topic_id, relation="MENTIONS")
                            new_edges += 1
                    
                    count += 1
                    print(f" [{ext.upper()}] Linked {os.path.basename(file_path)} -> {unique_topics[:3]}...")

    print(f"✅ DONE! Enriched {count} files with {new_edges} new connections.")
    nx.write_graphml(G, GRAPH_FILE)
    print("restart 'streamlit run app.py' to see the web of connections!")

if __name__ == "__main__":
    main()