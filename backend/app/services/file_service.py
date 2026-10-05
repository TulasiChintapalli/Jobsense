import io, os
ALLOWED = {".pdf", ".docx", ".txt"}

def extract_text(f):
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED: raise ValueError("Only PDF, DOCX and TXT files are supported.")
    data = f.read()
    if not data: raise ValueError("The uploaded file is empty.")
    try:
        if ext == ".txt": text = data.decode("utf-8", errors="ignore")
        elif ext == ".pdf":
            import fitz
            with fitz.open(stream=data, filetype="pdf") as doc: text = "\n".join(p.get_text() for p in doc)
        else:
            import docx
            text = "\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)
    except Exception:
        raise ValueError("Could not read this file. It may be corrupted.")
    if not text.strip(): raise ValueError("No readable text was found in the file.")
    return text
