#virtual_universe_blessings.py
import tkinter as tk
from tkinter import ttk, VERTICAL, RIGHT, LEFT, Y, StringVar, messagebox

class VirtualUniverseBlessingsTab:
    def __init__(self, notebook, rogue_buffs_su, command_manager, localization):
        self.rogue_buffs_su = rogue_buffs_su
        self.command_manager = command_manager
        self.localization = localization

        self.vu_blessings_frame = ttk.Frame(notebook)
        notebook.add(self.vu_blessings_frame, text=localization.get("Virtual_Universe_Blessings", "Virtual Universe Blessings"))

        # Create main frame
        main_frame = tk.Frame(self.vu_blessings_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for search and filters
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Right frame for the list
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create the search and filters section
        self.create_search_filters_section(left_frame)

        # Create the blessings list section
        self.create_blessings_list_section(right_frame)

    def create_search_filters_section(self, parent_frame):
        # Search by name
        search_label = tk.Label(parent_frame, text=self.localization["Search"])
        search_label.pack(pady=5)
        self.search_var = StringVar()
        search_entry = tk.Entry(parent_frame, textvariable=self.search_var)
        search_entry.pack()
        search_entry.bind('<Return>', self.on_search)

        # Category filter
        category_label = tk.Label(parent_frame, text=self.localization["Category"])
        category_label.pack(pady=5)
        self.category_var = StringVar()
        categories = [
            '',  # Empty string for 'All' categories
            'basic su',
            'divergent su',
            'equations',
            'infinite blessings',
            'resonance deployments',
            'unknown'
        ]
        category_options = [self.localization.get(cat, cat) for cat in categories]
        self.category_dropdown = ttk.Combobox(parent_frame, textvariable=self.category_var, values=category_options, state='readonly')
        self.category_dropdown.current(0)  # Default to 'All'
        self.category_dropdown.pack()

        # Type filter
        type_label = tk.Label(parent_frame, text=self.localization["Type"])
        type_label.pack(pady=5)
        self.type_var = StringVar()
        types = [
            '',  # Empty string for 'All' types
            'Preservation',
            'Memory',
            'Nonexistence',
            'Abundance',
            'Hunting',
            'Destruction',
            'Joy',
            'Spreading',
            'Erudition',
            'Unknown'
        ]
        type_options = [self.localization.get(t, t) for t in types]
        self.type_dropdown = ttk.Combobox(parent_frame, textvariable=self.type_var, values=type_options, state='readonly')
        self.type_dropdown.current(0)  # Default to 'All'
        self.type_dropdown.pack()

        # Rarity filter
        rarity_label = tk.Label(parent_frame, text=self.localization["Rarity"])
        rarity_label.pack(pady=5)
        self.rarity_var = StringVar()
        rarities = [
            '',  # Empty string for 'All' rarities
            'Mythic',
            'Legendary',
            'Rare',
            'Common',
            'Unknown'
        ]
        rarity_options = [self.localization.get(r, r) for r in rarities]
        self.rarity_dropdown = ttk.Combobox(parent_frame, textvariable=self.rarity_var, values=rarity_options, state='readonly')
        self.rarity_dropdown.current(0)  # Default to 'All'
        self.rarity_dropdown.pack()

        # Search button
        search_button = tk.Button(parent_frame, text=self.localization["Search_Button"], command=self.on_search)
        search_button.pack(pady=10)

    def create_blessings_list_section(self, parent_frame):
        # Listbox with blessings
        blessings_frame = tk.Frame(parent_frame)
        blessings_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(blessings_frame, orient=VERTICAL)
        self.blessings_listbox = tk.Listbox(blessings_frame, width=80, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=self.blessings_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.blessings_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Bind selection event
        self.blessings_listbox.bind('<<ListboxSelect>>', self.on_blessing_select)

        # Initialize variables
        self.selected_blessing_id = None

        # Initialize the blessings list
        self.update_blessings_list()

        # Command buttons
        command_frame = tk.Frame(parent_frame)
        command_frame.pack(pady=10)

        get_button = tk.Button(command_frame, text=self.localization["Get_Blessing"], command=self.execute_get_blessing)
        get_button.grid(row=0, column=0, padx=5)

        enhance_selected_button = tk.Button(command_frame, text=self.localization["Enhance_Selected"], command=self.execute_enhance_selected)
        enhance_selected_button.grid(row=0, column=1, padx=5)

        enhance_all_button = tk.Button(command_frame, text=self.localization["Enhance_All"], command=self.execute_enhance_all)
        enhance_all_button.grid(row=0, column=2, padx=5)

    def update_blessings_list(self):
        # Clear the listbox
        self.blessings_listbox.delete(0, tk.END)

        # Get the search and filter criteria
        search_text = self.search_var.get().lower()
        selected_category = self.category_var.get()
        selected_type = self.type_var.get()
        selected_rarity = self.rarity_var.get()

        # Map localized category/type/rarity back to internal values
        category_map = {
            self.localization.get('basic su', 'basic su'): 'basic su',
            self.localization.get('divergent su', 'divergent su'): 'divergent su',
            self.localization.get('equations', 'equations'): 'equations',
            self.localization.get('infinite blessings', 'infinite blessings'): 'infinite blessings',
            self.localization.get('resonance deployments', 'resonance deployments'): 'resonance deployments',
            self.localization.get('unknown', 'unknown'): 'unknown'
        }
        type_map = {
            self.localization.get('Preservation', 'Preservation'): 'Preservation',
            self.localization.get('Memory', 'Memory'): 'Memory',
            self.localization.get('Nonexistence', 'Nonexistence'): 'Nonexistence',
            self.localization.get('Abundance', 'Abundance'): 'Abundance',
            self.localization.get('Hunting', 'Hunting'): 'Hunting',
            self.localization.get('Destruction', 'Destruction'): 'Destruction',
            self.localization.get('Joy', 'Joy'): 'Joy',
            self.localization.get('Spreading', 'Spreading'): 'Spreading',
            self.localization.get('Erudition', 'Erudition'): 'Erudition',
            self.localization.get('Unknown', 'Unknown'): 'Unknown'
        }
        rarity_map = {
            self.localization.get('Mythic', 'Mythic'): 'Mythic',
            self.localization.get('Legendary', 'Legendary'): 'Legendary',
            self.localization.get('Rare', 'Rare'): 'Rare',
            self.localization.get('Common', 'Common'): 'Common',
            self.localization.get('Unknown', 'Unknown'): 'Unknown'
        }

        # Convert localized values back to internal values
        selected_category_internal = category_map.get(selected_category, '')
        selected_type_internal = type_map.get(selected_type, '')
        selected_rarity_internal = rarity_map.get(selected_rarity, '')

        # Populate the listbox
        for buff in self.rogue_buffs_su:
            display_text = f"{buff.name} ({buff.id})"
            if search_text and search_text not in buff.name.lower():
                continue
            if selected_category_internal and buff.category != selected_category_internal:
                continue
            if selected_type_internal and buff.buff_type != selected_type_internal:
                continue
            if selected_rarity_internal and buff.rarity != selected_rarity_internal:
                continue
            self.blessings_listbox.insert(tk.END, display_text)

    def on_search(self, event=None):
        self.update_blessings_list()

    def on_blessing_select(self, event):
        selected_indices = self.blessings_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_blessing = self.blessings_listbox.get(index)
            if '(' in selected_blessing and ')' in selected_blessing:
                id_str = selected_blessing.split('(')[-1].split(')')[0]
                self.selected_blessing_id = id_str
            else:
                self.selected_blessing_id = None
        else:
            self.selected_blessing_id = None

    def execute_get_blessing(self):
        target_id = self.selected_blessing_id

        if not target_id:
            messagebox.showwarning(self.localization["Warning"], self.localization["No_blessing_selected"])
            return

        get_command = f"/rogue buff {target_id}"
        self.command_manager.update_command(get_command)

    def execute_enhance_selected(self):
        target_id = self.selected_blessing_id

        if not target_id:
            messagebox.showwarning(self.localization["Warning"], self.localization["No_blessing_selected"])
            return

        enhance_command = f"/rogue enhance {target_id}"
        self.command_manager.update_command(enhance_command)

    def execute_enhance_all(self):
        enhance_command = "/rogue enhance -1"
        self.command_manager.update_command(enhance_command)
