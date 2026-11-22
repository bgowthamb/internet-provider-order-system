"""Windows-friendly desktop interface; no web server or uploads."""
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
from assistant import index_folder, answer


def main():
    root = tk.Tk()
    root.title('Local Knowledge Assistant')
    root.geometry('980x700')
    root.configure(bg='#e8eef5')
    style = ttk.Style(root)
    style.configure('Title.TLabel', font=('Segoe UI', 23, 'bold'))
    panel = ttk.Frame(root, padding=24)
    panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='Local Knowledge Assistant', style='Title.TLabel').pack(anchor='w')
    ttk.Label(panel, text='Private, read-only search • Select one folder at a time').pack(anchor='w', pady=(0, 16))
    folder = tk.StringVar()
    status = tk.StringVar(value='Choose a folder outside GitHub and cloud-synced directories.')
    model = tk.StringVar()
    query = tk.StringVar()
    row = ttk.Frame(panel)
    row.pack(fill='x')
    ttk.Entry(row, textvariable=folder).pack(side='left', fill='x', expand=True)
    def pick():
        chosen = filedialog.askdirectory()
        if chosen:
            folder.set(chosen)
    ttk.Button(row, text='Browse', command=pick).pack(side='left', padx=8)
    ttk.Label(panel, text='Optional downloaded Ollama model (blank = source search only)').pack(anchor='w', pady=(12, 0))
    ttk.Entry(panel, textvariable=model).pack(fill='x')
    ttk.Label(panel, text='Ask a question').pack(anchor='w', pady=(12, 0))
    ttk.Entry(panel, textvariable=query).pack(fill='x')
    results = ScrolledText(panel, wrap='word', font=('Segoe UI', 11))
    def show(text, message):
        results.delete('1.0', 'end')
        results.insert('1.0', text)
        status.set(message)
        button.configure(state='normal')
    def ask():
        path, question, selected_model = folder.get(), query.get().strip(), model.get().strip()
        if not path or not question:
            status.set('Choose a folder and enter a question.')
            return
        button.configure(state='disabled')
        status.set('Reading local files…')
        def work():
            try:
                passages, warnings = index_folder(path)
                output = answer(question, passages, selected_model or None)
                if warnings:
                    output += '\n\nReading notes:\n' + '\n'.join(warnings)
                root.after(0, show, output, f'Searched {len(passages)} passages')
            except Exception as exc:
                root.after(0, show, f'Unable to complete: {exc}', 'Check the folder or local model and retry.')
        threading.Thread(target=work, daemon=True).start()
    button = ttk.Button(panel, text='Search documents', command=ask)
    button.pack(anchor='w', pady=12)
    results.pack(fill='both', expand=True)
    ttk.Label(panel, textvariable=status, wraplength=850).pack(anchor='w', pady=8)
    root.mainloop()


if __name__ == '__main__':
    main()
