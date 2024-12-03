# tab_opencommand.py

import tkinter as tk
from tkinter import ttk

class OpenCommandTab:
    def __init__(self, notebook, localization):
        self.frame = ttk.Frame(notebook)
        self.localization = localization
        
        self.label = tk.Label(self.frame, text=self.localization["message"], justify="left")
        self.label.pack(fill="both", expand=True, padx=10, pady=10)
