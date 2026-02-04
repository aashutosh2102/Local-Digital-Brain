import os
import json
import zipfile
import email
from email import policy

class Ingestor:
    """
    LAYER 1: RAW INGESTION
    Sole Responsibility: Extract raw string data from complex binary formats.
    """
    
    def read(self, file_path, ext):
        raw_text = ""
        try:
            # 1. EMAILS (.eml)
            if ext == 'eml':
                with open(file_path, 'rb') as f:
                    msg = email.message_from_binary_file(f, policy=policy.default)
                    subject = str(msg['subject'])
                    sender = str(msg['from'])
                    body = msg.get_body(preferencelist=('plain'))
                    body_text = body.get_content() if body else ""
                    raw_text = f"{subject}\n{sender}\n{body_text}"

            # 2. EXCEL (.xlsx) - The XML Hack (Fast)
            elif ext == 'xlsx':
                with zipfile.ZipFile(file_path, 'r') as z:
                    if 'xl/sharedStrings.xml' in z.namelist():
                        raw_text = z.read('xl/sharedStrings.xml').decode('utf-8')

            # 3. POWER BI (.pbix) - The Layout Hack
            elif ext == 'pbix':
                with zipfile.ZipFile(file_path, mode='r') as z:
                    if 'Report/Layout' in z.namelist():
                        raw_text = z.read('Report/Layout').decode('utf-16-le', errors='ignore')

            # 4. JUPYTER (.ipynb)
            elif ext == 'ipynb':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for cell in data.get('cells', []):
                        if cell.get('cell_type') == 'code':
                            raw_text += " ".join(cell.get('source', [])) + "\n"

            # 5. PDFs (Binary Fallback)
            elif ext == 'pdf':
                with open(file_path, 'rb') as f:
                    # Robust binary extraction (ignores formatting)
                    raw_text = "".join([chr(b) for b in f.read(50000) if 32 <= b < 127])

            # 6. TEXT / CODE (.py, .sql, .json, .csv, etc.)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read(50000)

        except Exception:
            # Fail silently on corrupt files (Standard ETL practice)
            pass
            
        return raw_text