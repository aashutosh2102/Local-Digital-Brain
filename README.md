# 🧠 Local Digital Brain

A privacy-first, local Knowledge Graph that transforms raw files into an intelligent "Neural Mesh" using Python, spaCy, and NetworkX. 

> **Status:** v1.0 (Production Stable)
> **Key Tech:** Medallion Architecture, Neural Mesh, Atomic Persistence.

---

## 🏗️ Architecture Flow

This system runs in two decoupled phases: **The Builder** (Backend) and **The Viewer** (Frontend).

```mermaid
graph TD
    subgraph "Phase 1: The Builder (main_pipeline.py)"
        A[📂 Raw Files] -->|Ingest Layer| B(📄 Text Extraction)
        B -->|Curate Layer| C{🧹 Cleaning & Normalization}
        C -->|Neural Layer| D[🧠 Entity & Concept Extraction]
        D -->|Mesh Logic| E{🕸️ Deep Mesh Linking}
        
        E -- "Safety Valve (Top 20)" --> F[Nodes & Edges]
        F -->|Atomic Write| G[(my_personal_graph.graphml)]
        F -->|Live Status| H[status.json]
    end

    subgraph "Phase 2: The Viewer (app.py)"
        G -.->|Read-Only| I[Streamlit Dashboard]
        H -.->|Poll Status| J[⏱️ Live Timer & ETA]
        I --> K[🚀 Interactive Graph Physics]
    end
    
    style G fill:#f9f,stroke:#333,stroke-width:4px
    style E fill:#bbf,stroke:#333,stroke-width:2px