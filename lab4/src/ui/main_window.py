import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel, Label, Entry, Button, X
from utils.validator import Validator

class MainWindow(tk.Tk):
    def __init__(self, app, record_size, index_record_size):
        super().__init__()
        self.app = app
        self.current_block = 0
        self.validator = Validator(record_size, index_record_size)
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

        nav_frame = tk.Frame(self, pady=10)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_prev = tk.Button(nav_frame, text="◀", command=self._prev_block)
        self.btn_prev.pack(side=tk.LEFT, padx=20)

        self.btn_next = tk.Button(nav_frame, text="▶", command=self._next_block)
        self.btn_next.pack(side=tk.RIGHT, padx=20)

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        records, total_blocks = self.app.get_block(self.current_block)

        for rec in records:
            self.tree.insert("", tk.END, values=(
                rec['key'], 
                rec['value'], 
                rec['area'].upper()
            ))

        self.btn_prev.config(state=tk.NORMAL if self.current_block > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_block < total_blocks - 1 else tk.DISABLED)

    def _next_block(self):
        self.current_block += 1
        self.refresh_table()

    def _prev_block(self):
        self.current_block -= 1
        self.refresh_table()

    def _on_add_click(self):
        add_window = Toplevel(self)
        add_window.title("Add New Record")
        add_window.geometry("250x200")
        add_window.transient(self)
        add_window.grab_set()

        Label(add_window, text="Key (leave -1 for auto):").pack(pady=(10, 0))
        key_entry = Entry(add_window)
        key_entry.insert(0, "-1")
        key_entry.pack(padx=20, fill=X)

        Label(add_window, text="Data Value:").pack(pady=(10, 0))
        value_entry = Entry(add_window)
        value_entry.pack(padx=20, fill=X)

        def submit():
            key_val = key_entry.get()
            data_val = value_entry.get()

            key_validation, msg = self.validator.validate_key(key_val)

            if not key_validation:
                messagebox.showwarning(msg[0], msg[1])
                return

            data_validation, msg = self.validator.validate_data(data_val)

            if not data_validation and key_validation:
                messagebox.showwarning(msg[0], msg[1])
                return

            new_id = self.app.add(data_val, int(key_val))
            
            if new_id != -1:
                messagebox.showinfo("Success", f"Record added successfully with ID: {new_id}")
                add_window.destroy()
                self.refresh_table()
            else:
                messagebox.showerror("Error", "Failed to add record. ID might already exist.")

        Button(add_window, text="Add Record", command=submit).pack(pady=20)

    def _on_find_click(self):
        key_to_find = simpledialog.askinteger("Find Record", "Enter Key to search:")
        
        if key_to_find is None:
            return

        result = self.app.search(key_to_find)

        if result != -1:
            msg = (f"Key: {result['key']}\n"
                    f"Value: {result['value']}\n"
                    f"Area: {result['area']}")
            messagebox.showinfo("Record Found", msg)

            self._highlight_row_by_key(result['key'])
        else:
            messagebox.showwarning("Not Found", f"Record with key {key_to_find} not found!")

    def _highlight_row_by_key(self, key):
        for item_id in self.tree.get_children():
            row_key = self.tree.item(item_id)['values'][0]
            
            if str(row_key) == str(key):
                self.tree.selection_set(item_id)
                self.tree.see(item_id)
                return

    def _on_update_click(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return

        item_id = selected[0]
        row_values = self.tree.item(item_id)['values']
        current_key = row_values[0]
        current_val = row_values[1]

        update_win = Toplevel(self)
        update_win.title(f"Update Record #{current_key}")
        update_win.geometry("400x200")
        update_win.transient(self)
        update_win.grab_set()

        Label(update_win, text=f"Key: {current_key}", font=('Arial', 10, 'bold')).pack(pady=10)
        
        Label(update_win, text="Enter New Data Value").pack()
        val_entry = Entry(update_win)
        val_entry.insert(0, current_val)
        val_entry.pack(padx=20, fill=X)

        def do_save():
            new_data = val_entry.get()

            data_validation, msg = self.validator.validate_data(new_data)

            if not data_validation:
                messagebox.showwarning(msg[0], msg[1])
                return

            try:
                result = self.app.update(int(current_key), new_data)
                
                if result != -1:
                    messagebox.showinfo("Success", "Record updated successfully!")
                    update_win.destroy()
                    self.refresh_table()
                else:
                    messagebox.showerror("Error", "Failed to update record in storage.")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")

        Button(update_win, text="Save Changes", command=do_save).pack(pady=20)

    def _on_delete_click(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
        
        item_data = self.tree.item(selected[0])
        key_to_delete = item_data['values'][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete this record? (key: {key_to_delete})"):
            self.app.remove(key_to_delete)
            self.refresh_table()