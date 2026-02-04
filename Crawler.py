import os
import time
import networkx as nx
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
TARGET_FOLDER = r"C:\Users\ajha1\Downloads\000_Organized_Workspace"  # Change to your folder
GRAPH_FILE = "my_personal_graph.graphml"

class LocalGraphBuilder:
    def __init__(self):
        # Initialize an empty Directed Graph
        self.G = nx.DiGraph()

    def add_file_node(self, file_data):
        """
        Adds a file node and connects it to its extension and folder.
        """
        file_path = file_data['path']
        filename = file_data['name']
        extension = file_data['extension']
        
        # 1. Add the File Node
        self.G.add_node(file_path, 
                        label=filename, 
                        type='File', 
                        size_mb=file_data['size_mb'],
                        created_at=file_data['created_at'])
        
        # 2. Add the Extension Node (and link it)
        # We use the extension string as the unique ID for the node
        ext_id = f"EXT_{extension}"
        self.G.add_node(ext_id, label=extension, type='Extension')
        
        # 3. Create the Edge: File -> Extension
        self.G.add_edge(file_path, ext_id, relation="HAS_EXTENSION")

        # 4. Link to Parent Folder (to show hierarchy)
        parent_folder = os.path.dirname(file_path)
        self.G.add_node(parent_folder, label=os.path.basename(parent_folder), type='Folder')
        self.G.add_edge(parent_folder, file_path, relation="CONTAINS")

        print(f"Indexed: {filename}")

    def scan_directory(self, root_path):
        print(f"Starting scan of: {root_path}")
        
        count = 0
        for root, dirs, files in os.walk(root_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                try:
                    # --- METADATA EXTRACTION ---
                    stats = os.stat(file_path)
                    size_mb = round(stats.st_size / (1024 * 1024), 2)
                    created_at = time.ctime(stats.st_ctime)
                    extension = os.path.splitext(filename)[1].lower().replace('.', '') or "unknown"

                    file_data = {
                        "path": file_path,
                        "name": filename,
                        "size_mb": size_mb,
                        "created_at": created_at,
                        "extension": extension
                    }

                    self.add_file_node(file_data)
                    count += 1
                    
                    # Safety Break: If testing, stop after 100 files so it doesn't freeze
                    # if count > 100: break 

                except PermissionError:
                    continue
                except Exception as e:
                    print(f"Error: {e}")

    def save_graph(self, filename):
        print(f"Saving graph to {filename}...")
        nx.write_graphml(self.G, filename)
        print("Graph saved successfully!")

    def visualize_sample(self):
        """
        Draws a tiny sample of the graph just to prove it works.
        """
        print("Generating preview...")
        plt.figure(figsize=(10, 8))
        
        # Draw only the first 50 nodes to avoid a mess
        subgraph = self.G.subgraph(list(self.G.nodes)[:50])
        
        pos = nx.spring_layout(subgraph)
        nx.draw(subgraph, pos, with_labels=False, node_size=50, node_color="skyblue")
        
        # Draw labels specifically for files/extensions
        labels = nx.get_node_attributes(subgraph, 'label')
        nx.draw_networkx_labels(subgraph, pos, labels, font_size=8)
        
        plt.show()

# --- EXECUTION ---
if __name__ == "__main__":
    builder = LocalGraphBuilder()
    
    # 1. Build the Graph
    builder.scan_directory(TARGET_FOLDER)
    
    # 2. Save it to disk (So you don't lose it!)
    builder.save_graph(GRAPH_FILE)
    
    # 3. Show a quick picture
    builder.visualize_sample()