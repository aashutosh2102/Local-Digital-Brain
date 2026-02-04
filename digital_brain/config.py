import os

# --- PATHS ---
# Auto-detects Downloads. Change this string if you want to scan elsewhere.
TARGET_FOLDER = r"C:\Users\ajha1\Downloads\000_Organized_Workspace"  # Change to your folder
GRAPH_OUTPUT = "my_personal_graph.graphml"

# --- THE GOLDEN LIST (Allowed File Types) ---
# We ONLY process these. Everything else is ignored.
VALID_EXTENSIONS = {
    # Documentation & Data
    'pdf', 'txt', 'md', 'csv', 'json', 'xml', 'xlsx', 'html',
    # Code & Scripts
    'py', 'sql', 'js', 'css', 'ipynb',
    # Business Intelligence & Comms
    'pbix', 'eml'
}

# --- NOISE FILTERS ---
STOPWORDS = {
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'return', 'import', 
    'def', 'class', 'self', 'print', 'true', 'false', 'none', 'null', 'data', 
    'file', 'code', 'text', 'value', 'name', 'type', 'list', 'dict', 'json', 
    'html', 'body', 'width', 'height', 'style', 'font', 'main', 'args', 
    'kwargs', 'path', 'test', 'error', 'div', 'span', 'class', 'id'
}