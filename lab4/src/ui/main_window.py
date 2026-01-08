import tkinter as tk
from tkinter import ttk, messagebox

class MainWindow(tk.Tk):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.title("Lab 4 - Oleksandr Cherepov")
        self.geometry("800x500")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

        self._setup_ui()
        self.refresh_table()

    def _setup_ui(self):
        button_frame = tk.Frame(self, pady=15, bg="#f0f0f0")
        button_frame.pack(side=tk.TOP, fill=tk.X)

        btn_params = {"padx": 10, "pady": 5, "expand": True, "fill": tk.X}
        
        tk.Button(button_frame, text="Add Record", command=self._on_add_click).pack(side=tk.LEFT, **btn_params)
    
        tk.Button(button_frame, text="Find Record", command=self._on_find_click).pack(side=tk.LEFT, **btn_params)
        
        tk.Button(button_frame, text="Update Record", command=self._on_update_click).pack(side=tk.LEFT, **btn_params)
        
        tk.Button(button_frame, text="Delete Record", command=self._on_delete_click).pack(side=tk.LEFT, **btn_params)

        table_container = tk.Frame(self)
        table_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_container, 
            columns=("Key", "Value", "Area"), 
            show='headings', 
            yscrollcommand=scrollbar.set
        )
        
        self.tree.heading("Key", text="Key")
        self.tree.heading("Value", text="Data Content")
        self.tree.heading("Area", text="Storage Area")
        
        self.tree.column("Key", width=80, anchor=tk.CENTER)
        self.tree.column("Value", width=450, anchor=tk.W)
        self.tree.column("Area", width=120, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        records = self.app.get_all()

        for rec in records:
            self.tree.insert("", tk.END, values=(
                rec['key'], 
                rec['value'], 
                rec['area'].upper()
            ))

    # PLACEHOLDERS
    def _on_add_click(self):
        pass

    def _on_find_click(self):
        pass

    def _on_update_click(self):
        pass

    def _on_delete_click(self):
        pass