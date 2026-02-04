import spacy
import re
import os
from collections import Counter

class NeuralCore:
    """
    LAYER 3: INTELLIGENCE
    Sole Responsibility: Extract Concepts using Logic (Regex) and ML (SpaCy).
    """
    def __init__(self):
        print("🧠 Loading AI Models...")
        try: 
            self.nlp = spacy.load("en_core_web_sm")
        except: 
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def extract_concepts(self, clean_text):
        if not clean_text: return []
        concepts = set()
        
        # 1. Technical Patterns (Always safe, low memory)
        tech_tokens = re.findall(r'\b[A-Z0-9]+_[A-Z0-9_]+\b|\b[A-Z]{2,}\b', clean_text)
        concepts.update([t for t in tech_tokens if len(t) > 3])

        # 2. ML Entities (The Memory Hog)
        try:
            # REDUCED LIMIT: 50,000 -> 15,000 chars to save RAM
            # If text is too long, we only read the beginning
            doc = self.nlp(clean_text[:15000])
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                    concepts.add(ent.text.strip().replace(" ", "_"))
        except Exception:
            # If AI fails (Out of Memory), we just skip this part and return what we have
            pass

        # 3. Frequency (Top 10 most common words)
        try:
            for word, count in Counter(clean_text.split()).most_common(10):
                if len(word) > 3: concepts.add(word)
        except Exception:
            pass
            
        return list(concepts)