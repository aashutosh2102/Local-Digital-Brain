import networkx as nx
import matplotlib.pyplot as plt

GRAPH_FILE = "my_personal_graph.graphml"

print("Loading full graph... (this might take 10 seconds)")
G = nx.read_graphml(GRAPH_FILE)
print(f"Loaded {G.number_of_nodes()} nodes.")

# Use a layout that spreads things out efficiently (Kamada-Kawai is good but slow, Spring is faster)
print("Calculating layout positions... (this handles the physics)")
# k=0.15 controls the spacing (smaller = tighter)
pos = nx.spring_layout(G, k=0.15, iterations=20, seed=42) 

plt.figure(figsize=(50, 50)) # Massive canvas size (5000x5000 pixels)

print("Drawing nodes...")
# Draw Files (Blue, Small)
files = [n for n, d in G.nodes(data=True) if d.get('type')=='File']
nx.draw_networkx_nodes(G, pos, nodelist=files, node_size=10, node_color='skyblue', alpha=0.6)

# Draw Folders (Red, Larger)
folders = [n for n, d in G.nodes(data=True) if d.get('type')=='Folder']
nx.draw_networkx_nodes(G, pos, nodelist=folders, node_size=100, node_color='salmon')

# Draw Edges (Very thin)
nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.5, edge_color='gray')

print("Saving 'full_system_map.png'... this will be huge!")
plt.savefig("full_system_map.png", dpi=100, bbox_inches='tight')
print("Done! Open 'full_system_map.png' to see everything.")