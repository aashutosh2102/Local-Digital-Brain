import re
import config # Importing shared config

class Curator:
    """
    LAYER 2: CURATION & CLEANING
    Sole Responsibility: Normalize data, remove noise/HTML, structural formatting.
    """
    
    def cleanse(self, raw_text):
        if not raw_text: return ""

        # 1. Remove HTML/XML Tags (Crucial for .xlsx and .html)
        text = re.sub(r'<[^>]+>', ' ', raw_text)
        
        # 2. Remove URLs and Email Addresses (Privacy/Noise)
        text = re.sub(r'http\S+', ' ', text)
        text = re.sub(r'\S+@\S+', ' ', text)

        # 3. Remove Special Characters (Keep underscores for code variables)
        text = re.sub(r'[^\w\s]', ' ', text)

        # 4. Standardization
        text = text.upper()
        
        # 5. Stopword Removal (Using the list from config.py)
        tokens = text.split()
        clean_tokens = [
            t for t in tokens 
            if len(t) > 3 
            and t.lower() not in config.STOPWORDS 
            and not t.isdigit()
        ]

        return " ".join(clean_tokens)