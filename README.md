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



---

## 📂 Codebase Structure

The project is organized into two main zones: the **Core Brain Logic** (inside `digital_brain/`) and the **Root Utilities** (helper scripts).

### 🧠 Zone 1: The Digital Brain (`digital_brain/`)
This folder contains the **Medallion Architecture** pipeline. It is the "Engine" of the project.

| File | Layer | Description |
| :--- | :--- | :--- |
| **`layer1_ingest.py`** | 🥉 **Bronze** | **The Raw Reader.** Handles messy binary files. It knows how to open PDFs, extract text from Excel cells, and unzip archives to find code. |
| **`layer2_curate.py`** | 🥈 **Silver** | **The Cleaner.** Removes whitespace, normalizes Unicode, strips HTML tags, and filters out "stop words" (junk data). |
| **`layer3_neural.py`** | 🥇 **Gold** | **The Thinker.** Uses `spaCy` (NLP) to extract named entities (Organizations, Dates, Code Libraries) and identify "Concepts" from the text. |
| **`main_pipeline.py`** | ⚙️ **Orchestrator** | **The Boss.** Runs the loop. It manages the "Safety Valve" (memory limits), handles the Atomic Saves, and updates `status.json` for the frontend. |
| **`config.py`** | 🔧 **Settings** | **The Control Panel.** Defines which file extensions to scan (`.py`, `.md`, `.pbix`) and sets folder paths. |

### 🛠️ Zone 2: Root Utilities
These are standalone scripts that support the main application or provide experimental features.

| File | Purpose |
| :--- | :--- |
| **`app.py`** | **The Frontend.** A Streamlit application that reads the `.graphml` database and visualizes it using `PyVis`. It includes the Live Timer and Physics Engine. |
| **`Crawler.py`** | **Data Scout.** A standalone script used to spider through directories and list files without processing them (useful for debugging file permissions). |
| **`nlp_processor.py`** | **NLP Lab.** A testing ground for the spaCy model. Used to tweak entity recognition rules before moving them into `layer3_neural.py`. |
| **`render_all.py`** | **Static Renderer.** Generates a static HTML file of the entire graph (without the Streamlit UI) for quick sharing. |
| **`deep_mesh_builder.py`** | **Experimental.** A playground for testing new "Deep Mesh" algorithms before they are merged into the main pipeline. |

---