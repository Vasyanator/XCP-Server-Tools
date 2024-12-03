# tab_items.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, VERTICAL, RIGHT, LEFT, Y, END

class ItemsTab:
    def __init__(self, notebook, base_materials, lightcones, materials, other_items, unknown_items, command_manager, localization, server_type):
        self.notebook = notebook
        self.base_materials = base_materials
        self.lightcones = lightcones
        self.materials = materials
        self.other_items = other_items
        self.unknown_items = unknown_items
        self.command_manager = command_manager
        self.localization = localization
        self.server_type = server_type

        self.frame = ttk.Frame(notebook)
        self.init_tab()

    def init_tab(self):
        # Create sub-tabs
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for each item type, passing the respective lists
        self.create_item_tab(self.localization['Base Materials'], self.base_materials)
        self.create_item_tab(self.localization['Lightcones'], self.lightcones, additional_options={'level': (1, 80), 'rank': (1, 5)})
        self.create_item_tab(self.localization['Materials'], self.materials)
        self.create_item_tab(self.localization['Other'], self.other_items)
        self.create_item_tab(self.localization['Unknown'], self.unknown_items)

    def create_item_tab(self, tab_name, item_list, additional_options=None):
        tab_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab_frame, text=tab_name)

        selected_item_id = None
        quantity_var = tk.StringVar(value='1')
        search_var = tk.StringVar()

        # For Lightcones, we have additional variables
        if additional_options:
            level_var = tk.StringVar(value='80')
            rank_var = tk.StringVar(value='5')

        # Create main frame
        main_frame = tk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for item selection
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right frame for options
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Search functionality
        search_label = tk.Label(left_frame, text=self.localization["Search"])
        search_label.pack()

        search_entry = tk.Entry(left_frame, textvariable=search_var)
        search_entry.pack()
        search_var.trace('w', lambda *args: update_item_list())

        # Item selection with scrollbar
        item_frame = tk.Frame(left_frame)
        item_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(item_frame, orient=VERTICAL)
        item_listbox = tk.Listbox(item_frame, width=50, height=20, yscrollcommand=scrollbar.set)
        scrollbar.config(command=item_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        item_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Bind item selection event
        def on_item_select(event):
            nonlocal selected_item_id
            selected_indices = item_listbox.curselection()
            if selected_indices:
                index = selected_indices[0]
                selected_item = item_listbox.get(index)
                if '(' in selected_item and ')' in selected_item:
                    id_str = selected_item.split('(')[-1].split(')')[0]
                    selected_item_id = id_str
                    # Update the command
                    update_command()
                else:
                    self.command_manager.update_command('')
            else:
                self.command_manager.update_command('')

        item_listbox.bind('<<ListboxSelect>>', on_item_select)

        # Quantity selection
        quantity_label = tk.Label(right_frame, text=self.localization["Quantity"])
        quantity_label.pack()

        quantity_entry = tk.Entry(right_frame, textvariable=quantity_var)
        quantity_entry.pack()

        # Update command when quantity changes
        quantity_var.trace('w', lambda *args: update_command())

        # For Lightcones, add level and rank options
        if additional_options:
            # Level selection
            level_label = tk.Label(right_frame, text=f"{self.localization['Level']} ({additional_options['level'][0]}-{additional_options['level'][1]}):")
            level_label.pack()

            level_spinbox = tk.Spinbox(
                right_frame,
                from_=additional_options['level'][0],
                to=additional_options['level'][1],
                textvariable=level_var,
                width=5,
                command=lambda: update_command()
            )
            level_spinbox.pack()

            # Rank selection
            rank_label = tk.Label(right_frame, text=f"{self.localization['Rank']} ({additional_options['rank'][0]}-{additional_options['rank'][1]}):")
            rank_label.pack()

            rank_spinbox = tk.Spinbox(
                right_frame,
                from_=additional_options['rank'][0],
                to=additional_options['rank'][1],
                textvariable=rank_var,
                width=5,
                command=lambda: update_command()
            )
            rank_spinbox.pack()

            # Update command when level or rank changes
            level_var.trace('w', lambda *args: update_command())
            rank_var.trace('w', lambda *args: update_command())

        # Update item list function
        def update_item_list():
            search_text = search_var.get().lower()

            # Clear the listbox
            item_listbox.delete(0, tk.END)

            # Populate the listbox with items matching the search
            for item in item_list:
                display_text = f"{item.title} ({item.id})"
                if search_text in item.title.lower() or search_text in item.id:
                    item_listbox.insert(tk.END, display_text)

            # Clear the command
            self.command_manager.update_command('')

        # Update command function
        def update_command():
            if not selected_item_id:
                self.command_manager.update_command('')
                return

            quantity = quantity_var.get()
            if not quantity.isdigit() or int(quantity) <= 0:
                self.command_manager.update_command('')
                return

            command = f"/give {selected_item_id} x{quantity}"

            if additional_options:
                # For lightcones, add level and rank
                level = level_var.get()
                rank = rank_var.get()

                # Validate inputs
                if not level.isdigit() or not (additional_options['level'][0] <= int(level) <= additional_options['level'][1]):
                    self.command_manager.update_command('')
                    return
                if not rank.isdigit() or not (additional_options['rank'][0] <= int(rank) <= additional_options['rank'][1]):
                    self.command_manager.update_command('')
                    return
                

                if self.server_type == 'LunarCore':
                    command += f" lv{level} r{rank}"
                elif self.server_type == 'DanhengServer':
                    command += f" l{level} r{rank}"

            self.command_manager.update_command(command)

        # Initialize the item list
        update_item_list()

