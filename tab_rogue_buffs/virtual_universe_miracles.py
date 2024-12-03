#virtual_universe_miracles.py
import tkinter as tk
from tkinter import ttk, VERTICAL, RIGHT, LEFT, Y, StringVar, messagebox

class VirtualUniverseMiraclesTab:
    def __init__(self, notebook, rogue_miracles, command_manager, localization):
        self.rogue_miracles = rogue_miracles
        self.command_manager = command_manager
        self.localization = localization

        self.vu_miracles_frame = ttk.Frame(notebook)
        notebook.add(self.vu_miracles_frame, text=localization.get("Virtual_Universe_Miracles", "Virtual Universe Miracles"))

        # Create main frame
        main_frame = tk.Frame(self.vu_miracles_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for search and filters
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Right frame for the list
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create the search and filters section
        self.create_miracles_search_filters_section(left_frame)

        # Create the miracles list section
        self.create_miracles_list_section(right_frame)

    def create_miracles_search_filters_section(self, parent_frame):
        # Search by name
        search_label = tk.Label(parent_frame, text=self.localization["Search"])
        search_label.pack(pady=5)
        self.miracle_search_var = StringVar()
        search_entry = tk.Entry(parent_frame, textvariable=self.miracle_search_var)
        search_entry.pack()
        search_entry.bind('<Return>', self.on_miracle_search)

        # Category filter
        category_label = tk.Label(parent_frame, text=self.localization["Category"])
        category_label.pack(pady=5)
        self.miracle_category_var = StringVar()
        categories = [
            '',  # Empty string for 'All' categories
            'basic su',
            'infinite',
            'divergent su',
            'unidentified area'
        ]
        category_options = [self.localization.get(cat, cat) for cat in categories]
        self.miracle_category_dropdown = ttk.Combobox(parent_frame, textvariable=self.miracle_category_var, values=category_options, state='readonly')
        self.miracle_category_dropdown.current(0)  # Default to 'All'
        self.miracle_category_dropdown.pack()

        # Search button
        search_button = tk.Button(parent_frame, text=self.localization["Search_Button"], command=self.on_miracle_search)
        search_button.pack(pady=10)

    def create_miracles_list_section(self, parent_frame):
        # Listbox with miracles
        miracles_frame = tk.Frame(parent_frame)
        miracles_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(miracles_frame, orient=VERTICAL)
        self.miracles_listbox = tk.Listbox(miracles_frame, width=80, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=self.miracles_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.miracles_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Bind selection event
        self.miracles_listbox.bind('<<ListboxSelect>>', self.on_miracle_select)

        # Initialize variables
        self.selected_miracle_id = None

        # Initialize the miracles list
        self.update_miracles_list()

    def update_miracles_list(self):
        # Clear the listbox
        self.miracles_listbox.delete(0, tk.END)

        # Get the search and filter criteria
        search_text = self.miracle_search_var.get().lower()
        selected_category = self.miracle_category_var.get()

        # Map localized category back to internal values
        category_map = {
            self.localization.get('basic su', 'basic su'): 'basic su',
            self.localization.get('infinite', 'infinite'): 'infinite',
            self.localization.get('divergent su', 'divergent su'): 'divergent su',
            self.localization.get('unidentified area', 'unidentified area'): 'unidentified area',
        }
        selected_category_internal = category_map.get(selected_category, '')

        # Categorize miracles based on ID ranges
        def categorize_miracle(miracle):
            miracle_id_int = int(miracle['id'])
            if 1 <= miracle_id_int <= 1900:
                return 'basic su'
            elif 2000 <= miracle_id_int <= 2200:
                return 'infinite'
            elif 3000 <= miracle_id_int <= 3999:
                return 'divergent su'
            elif 7000 <= miracle_id_int <= 7999:
                return 'unidentified area'
            else:
                return 'unknown'

        # Populate the listbox
        for miracle in self.rogue_miracles:
            category = categorize_miracle(miracle)
            display_text = f"{miracle['name']} ({miracle['id']})"
            if search_text and search_text not in miracle['name'].lower():
                continue
            if selected_category_internal and category != selected_category_internal:
                continue
            self.miracles_listbox.insert(tk.END, display_text)

    def on_miracle_search(self, event=None):
        self.update_miracles_list()

    def on_miracle_select(self, event):
        selected_indices = self.miracles_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_miracle = self.miracles_listbox.get(index)
            if '(' in selected_miracle and ')' in selected_miracle:
                id_str = selected_miracle.split('(')[-1].split(')')[0]
                self.selected_miracle_id = id_str
                self.execute_get_miracle()  # Automatically execute command when selected
            else:
                self.selected_miracle_id = None
        else:
            self.selected_miracle_id = None

    def execute_get_miracle(self):
        target_id = self.selected_miracle_id

        if not target_id:
            messagebox.showwarning(self.localization["Warning"], self.localization["No_miracle_selected"])
            return

        get_command = f"/rogue miracle {target_id}"
        self.command_manager.update_command(get_command)
