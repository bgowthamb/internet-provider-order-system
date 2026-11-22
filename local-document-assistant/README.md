# Local Knowledge Assistant

A desktop, read-only document search assistant with optional local AI generation. Designed for personal records and general reference manuals. No API keys, account, or cloud upload required.

## Windows quick start

Install Python 3.12 from python.org (include Tcl/Tk). Open PowerShell in this folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe desktop.py
```

Select your private document folder outside the repository and outside cloud-synced locations. Ask a question. Results display excerpts with filenames and PDF page numbers.

### Optional AI mode

Install Ollama separately and download a local model suitable for your computer. Enter its exact installed model name in the desktop app. The app calls only the loopback Ollama endpoint; keep Ollama offline and avoid cloud models. Leave the model field blank for offline keyword retrieval without Ollama. Model installation requires internet access, but document retrieval does not.

## Privacy and limitations

- No documents, persistent index, prompts, or responses are written by this application. Documents are read in memory. Do not select a shared folder or add records to this public repository.
- Supported formats: text, Markdown, CSV, text-based PDF, DOCX (paragraphs and tables). Scanned PDFs require separate offline OCR.
- Keyword retrieval is not semantic search; use precise keywords. AI answers may be wrong; check source excerpts.
- This is a personal prototype, not a validated enterprise system or regulated manufacturing tool. Only use approved, non-confidential reference material in company settings. No autonomous actions or production system connections.
- For truly sensitive data use a trusted local offline system and full-disk encryption. Do not use cloud models or shared computers.

## Tests

`python -m unittest discover -v`
