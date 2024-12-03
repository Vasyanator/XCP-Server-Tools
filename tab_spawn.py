# tab_spawn.py

import tkinter as tk
from tkinter import ttk
from tkinter import VERTICAL, RIGHT, LEFT, Y, StringVar, IntVar
from tkinter import messagebox

class SpawnTab:
    def __init__(self, notebook, props_list, npc_monsters_list, battle_stages, battle_monsters_list, command_manager, localization):
        self.notebook = notebook
        self.props_list = props_list
        self.npc_monsters_list = npc_monsters_list
        self.battle_stages = battle_stages
        self.battle_monsters_list = battle_monsters_list
        self.command_manager = command_manager
        self.localization = localization

        self.frame = ttk.Frame(notebook)
        self.init_tab()

    def init_tab(self):
        # Create sub-tabs
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # Create 'Props' tab
        self.create_props_tab()

        # Create 'Monsters' tab
        self.create_monsters_tab()

    def create_props_tab(self):
        tab_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab_frame, text=self.localization['Props'])

        selected_prop_id = None
        search_var = StringVar()

        # Main frame
        main_frame = tk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search functionality
        search_label = tk.Label(main_frame, text=self.localization["Search"])
        search_label.pack()

        search_entry = tk.Entry(main_frame, textvariable=search_var)
        search_entry.pack()
        search_var.trace('w', lambda *args: update_prop_list())

        # Prop selection with scrollbar
        prop_frame = tk.Frame(main_frame)
        prop_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(prop_frame, orient=VERTICAL)
        prop_listbox = tk.Listbox(prop_frame, width=50, height=20, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=prop_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        prop_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Bind selection event
        def on_prop_select(event):
            nonlocal selected_prop_id
            selected_indices = prop_listbox.curselection()
            if selected_indices:
                index = selected_indices[0]
                selected_prop = prop_listbox.get(index)
                if '(' in selected_prop and ')' in selected_prop:
                    id_str = selected_prop.split('(')[-1].split(')')[0]
                    selected_prop_id = id_str
                    # Update the command
                    update_command()
                else:
                    self.command_manager.update_command('')
            else:
                self.command_manager.update_command('')

        prop_listbox.bind('<<ListboxSelect>>', on_prop_select)

        # Update prop list function
        def update_prop_list():
            search_text = search_var.get().lower()

            props_data = self.props_list

            # Clear the listbox
            prop_listbox.delete(0, tk.END)

            # Populate the listbox
            for entry in props_data:
                display_text = f"{entry['name']} ({entry['id']})"
                if search_text in entry['name'].lower() or search_text in entry['id']:
                    prop_listbox.insert(tk.END, display_text)

            # Clear the command
            self.command_manager.update_command('')


        # Update command function
        def update_command():
            if not selected_prop_id:
                self.command_manager.update_command('')
                return

            command = f"/spawn {selected_prop_id}"

            self.command_manager.update_command(command)

        # Initialize the prop list
        update_prop_list()

    def create_monsters_tab(self):
        tab_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab_frame, text=self.localization['Monsters'])

        # Variables to hold selections
        selected_npc_monster_id = None
        selected_battle_monster_ids = []
        selected_stage_id = None

        level_var = StringVar(value='1')
        amount_var = StringVar(value='1')
        radius_var = StringVar(value='1')

        level_enabled_var = IntVar(value=1)
        amount_enabled_var = IntVar(value=1)
        radius_enabled_var = IntVar(value=0)

        # Toggle between 'Custom monsters' and 'Stages'
        toggle_var = StringVar(value=self.localization['Custom_monsters'])

        # Define update_command function before it's used
        def update_command():
            if not selected_npc_monster_id:
                self.command_manager.update_command('')
                return

            command = f"/spawn {selected_npc_monster_id}"

            # Add parameters if enabled
            if amount_enabled_var.get():
                amount = amount_var.get()
                if amount.isdigit() and int(amount) > 0:
                    command += f" x{amount}"
                else:
                    self.command_manager.update_command('')
                    return

            if level_enabled_var.get():
                level = level_var.get()
                if level.isdigit() and int(level) > 0:
                    command += f" lv{level}"
                else:
                    self.command_manager.update_command('')
                    return

            if radius_enabled_var.get():
                radius = radius_var.get()
                if radius.isdigit() and int(radius) > 0:
                    command += f" r{radius}"
                else:
                    self.command_manager.update_command('')
                    return

            # Add either 's{stage id}' or battle monster ids
            if toggle_var.get() == self.localization['Stages']:
                if selected_stage_id:
                    command += f" s{selected_stage_id}"
                else:
                    self.command_manager.update_command('')
                    return
            elif toggle_var.get() == self.localization['Custom_monsters']:
                if selected_battle_monster_ids:
                    for battle_monster_id in selected_battle_monster_ids:
                        command += f" {battle_monster_id}"
                else:
                    self.command_manager.update_command('')
                    return
            else:
                self.command_manager.update_command('')
                return

            self.command_manager.update_command(command)

        # Main frame
        main_frame = tk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for NPC Monsters list and options
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right frame for Battle Monsters or Stages
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # NPC Monsters list
        npc_monster_frame = tk.Frame(left_frame)
        npc_monster_frame.pack(fill=tk.BOTH, expand=True)

        npc_search_var = StringVar()
        npc_search_label = tk.Label(npc_monster_frame, text=self.localization["Search_NPC_Monsters"])
        npc_search_label.pack()
        npc_search_entry = tk.Entry(npc_monster_frame, textvariable=npc_search_var)
        npc_search_entry.pack()
        npc_search_var.trace('w', lambda *args: update_npc_monster_list())

        npc_scrollbar = tk.Scrollbar(npc_monster_frame, orient=VERTICAL)
        npc_listbox = tk.Listbox(npc_monster_frame, width=50, height=20, yscrollcommand=npc_scrollbar.set, exportselection=False)
        npc_scrollbar.config(command=npc_listbox.yview)
        npc_scrollbar.pack(side=RIGHT, fill=Y)
        npc_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Bind selection event
        def on_npc_select(event):
            nonlocal selected_npc_monster_id
            selected_indices = npc_listbox.curselection()
            if selected_indices:
                index = selected_indices[0]
                selected_npc = npc_listbox.get(index)
                if '(' in selected_npc and ')' in selected_npc:
                    id_str = selected_npc.split('(')[-1].split(')')[0]
                    selected_npc_monster_id = id_str
                    # Update the command
                    update_command()
                else:
                    selected_npc_monster_id = None
                    self.command_manager.update_command('')
            else:
                selected_npc_monster_id = None
                self.command_manager.update_command('')

        npc_listbox.bind('<<ListboxSelect>>', on_npc_select)

        # Parameters under NPC Monsters list
        params_frame = tk.Frame(left_frame)
        params_frame.pack()

        # Level parameter
        level_checkbox = tk.Checkbutton(params_frame, text=self.localization["Level"], variable=level_enabled_var, command=update_command)
        level_checkbox.grid(row=0, column=0, sticky='w')
        level_entry = tk.Entry(params_frame, textvariable=level_var, width=5)
        level_entry.grid(row=0, column=1)
        level_var.trace('w', lambda *args: update_command())

        # Amount parameter
        amount_checkbox = tk.Checkbutton(params_frame, text=self.localization["Number"], variable=amount_enabled_var, command=update_command)
        amount_checkbox.grid(row=1, column=0, sticky='w')
        amount_entry = tk.Entry(params_frame, textvariable=amount_var, width=5)
        amount_entry.grid(row=1, column=1)
        amount_var.trace('w', lambda *args: update_command())

        # Radius parameter
        radius_checkbox = tk.Checkbutton(params_frame, text=self.localization["Radius"], variable=radius_enabled_var, command=update_command)
        radius_checkbox.grid(row=2, column=0, sticky='w')
        radius_entry = tk.Entry(params_frame, textvariable=radius_var, width=5)
        radius_entry.grid(row=2, column=1)
        radius_var.trace('w', lambda *args: update_command())

        # Battle Monsters or Stages toggle
        toggle_frame = tk.Frame(right_frame)
        toggle_frame.pack()

        toggle_label = tk.Label(toggle_frame, text=self.localization["Select"])
        toggle_label.pack(side=LEFT)

        toggle_optionmenu = ttk.OptionMenu(toggle_frame, toggle_var, self.localization['Custom_monsters'], self.localization['Custom_monsters'], self.localization['Stages'], command=lambda _: update_battle_ui())
        toggle_optionmenu.pack(side=LEFT)

        # Frame to hold dynamic battle UI
        battle_frame = tk.Frame(right_frame)
        battle_frame.pack(fill=tk.BOTH, expand=True)

        # Function to update battle UI
        def update_battle_ui():
            # Clear the battle_frame
            for widget in battle_frame.winfo_children():
                widget.destroy()

            if toggle_var.get() == self.localization['Custom_monsters']:
                # Custom Monsters UI
                setup_custom_monsters_ui()
            else:
                # Stages UI
                setup_stages_ui()

            update_command()

        # Functions for custom monsters and stages
        def setup_custom_monsters_ui():
            # Search functionality for Battle Monsters
            battle_search_var = StringVar()
            battle_search_label = tk.Label(battle_frame, text=self.localization["Search_Battle_Monsters"])
            battle_search_label.pack()
            battle_search_entry = tk.Entry(battle_frame, textvariable=battle_search_var)
            battle_search_entry.pack()
            battle_search_var.trace('w', lambda *args: update_battle_monster_list())

            # Available Battle Monsters list
            battle_monster_frame = tk.Frame(battle_frame)
            battle_monster_frame.pack(fill=tk.BOTH, expand=True)

            battle_monster_scrollbar = tk.Scrollbar(battle_monster_frame, orient=VERTICAL)
            battle_monster_listbox = tk.Listbox(battle_monster_frame, width=50, height=10, yscrollcommand=battle_monster_scrollbar.set, exportselection=False)
            battle_monster_scrollbar.config(command=battle_monster_listbox.yview)
            battle_monster_scrollbar.pack(side=RIGHT, fill=Y)
            battle_monster_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

            # 'Add' button
            add_button = tk.Button(battle_frame, text=self.localization["Add"], command=lambda: add_battle_monster(battle_monster_listbox))
            add_button.pack()

            # Selected Battle Monsters list
            selected_battle_label = tk.Label(battle_frame, text=self.localization["Selected_Battle_Monsters"])
            selected_battle_label.pack()

            selected_battle_frame = tk.Frame(battle_frame)
            selected_battle_frame.pack(fill=tk.BOTH, expand=True)

            selected_battle_scrollbar = tk.Scrollbar(selected_battle_frame, orient=VERTICAL)
            selected_battle_listbox = tk.Listbox(selected_battle_frame, width=50, height=10, yscrollcommand=selected_battle_scrollbar.set, exportselection=False)
            selected_battle_scrollbar.config(command=selected_battle_listbox.yview)
            selected_battle_scrollbar.pack(side=RIGHT, fill=Y)
            selected_battle_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

            # 'Remove' and 'Clear' buttons
            buttons_frame = tk.Frame(battle_frame)
            buttons_frame.pack()

            remove_button = tk.Button(buttons_frame, text=self.localization["Remove"], command=lambda: remove_selected_battle_monster(selected_battle_listbox))
            remove_button.pack(side=LEFT)
            clear_button = tk.Button(buttons_frame, text=self.localization["Clear"], command=lambda: clear_selected_battle_monsters(selected_battle_listbox))
            clear_button.pack(side=LEFT)

            def update_battle_monster_list():
                battle_search_text = battle_search_var.get().lower()

                battle_monsters_data = self.battle_monsters_list

                # Clear the listbox
                battle_monster_listbox.delete(0, tk.END)

                # Populate the listbox
                for entry in battle_monsters_data:
                    display_text = f"{entry['name']} ({entry['id']})"
                    if battle_search_text in entry['name'].lower() or battle_search_text in entry['id']:
                        battle_monster_listbox.insert(tk.END, display_text)

            def add_battle_monster(listbox):
                selected_indices = listbox.curselection()
                for index in selected_indices:
                    selected_item = listbox.get(index)
                    if selected_item not in selected_battle_listbox.get(0, tk.END):
                        selected_battle_listbox.insert(tk.END, selected_item)
                        # Extract the ID
                        if '(' in selected_item and ')' in selected_item:
                            id_str = selected_item.split('(')[-1].split(')')[0]
                            selected_battle_monster_ids.append(id_str)
                update_command()

            def remove_selected_battle_monster(listbox):
                selected_indices = listbox.curselection()
                for index in reversed(selected_indices):
                    selected_item = listbox.get(index)
                    listbox.delete(index)
                    # Remove the ID from selected_battle_monster_ids
                    if '(' in selected_item and ')' in selected_item:
                        id_str = selected_item.split('(')[-1].split(')')[0]
                        if id_str in selected_battle_monster_ids:
                            selected_battle_monster_ids.remove(id_str)
                update_command()

            def clear_selected_battle_monsters(listbox):
                listbox.delete(0, tk.END)
                selected_battle_monster_ids.clear()
                update_command()

            update_battle_monster_list()

        def setup_stages_ui():
            # Level selection
            level_frame = tk.Frame(battle_frame)
            level_frame.pack()

            level_label = tk.Label(level_frame, text=self.localization["For_world_level"])
            level_label.pack(side=LEFT)

            level_var_stage = StringVar(value='6')
            level_options = ['All', '0', '1', '2', '3', '4', '5', '6']
            level_menu = ttk.OptionMenu(level_frame, level_var_stage, level_options[0], *level_options)
            level_menu.pack(side=LEFT)

            # Bind level selection change to update the list
            level_var_stage.trace('w', lambda *args: update_battle_stage_list())

            # Search functionality for Battle Stages
            battle_search_var = StringVar()
            battle_search_label = tk.Label(battle_frame, text=self.localization["Search_Battle_Stages"])
            battle_search_label.pack()
            battle_search_entry = tk.Entry(battle_frame, textvariable=battle_search_var)
            battle_search_entry.pack()

            # Define update_battle_stage_list before it's used
            def update_battle_stage_list():
                battle_search_text = battle_search_var.get().lower()
                selected_level = level_var_stage.get()

                battle_stages_data = self.battle_stages

                # Clear the listbox
                battle_stage_listbox.delete(0, tk.END)

                # Populate the listbox
                for entry in battle_stages_data:
                    # Filter by level
                    stage_id = entry['id']
                    if selected_level != 'All':
                        if not stage_id[-1].isdigit():
                            continue  # Skip if last character is not a digit
                        if stage_id[-1] != selected_level:
                            continue  # Skip stages that don't match the selected level

                    # Filter by search text
                    if battle_search_text in entry['name'].lower() or battle_search_text in entry['id']:
                        display_text = f"{entry['name']} ({entry['id']})"
                        battle_stage_listbox.insert(tk.END, display_text)

            # 'Search' button
            search_button = tk.Button(battle_frame, text=self.localization["Search"], command=update_battle_stage_list)
            search_button.pack()

            # Battle Stages list
            battle_stage_scrollbar = tk.Scrollbar(battle_frame, orient=VERTICAL)
            battle_stage_listbox = tk.Listbox(battle_frame, width=50, height=20, yscrollcommand=battle_stage_scrollbar.set, exportselection=False)
            battle_stage_scrollbar.config(command=battle_stage_listbox.yview)
            battle_stage_scrollbar.pack(side=RIGHT, fill=Y)
            battle_stage_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

            # Bind selection event
            def on_battle_stage_select(event):
                nonlocal selected_stage_id
                selected_indices = battle_stage_listbox.curselection()
                if selected_indices:
                    index = selected_indices[0]
                    selected_item = battle_stage_listbox.get(index)
                    if '(' in selected_item and ')' in selected_item:
                        id_str = selected_item.split('(')[-1].split(')')[0]
                        selected_stage_id = id_str
                        selected_battle_monster_ids.clear()
                        update_command()
                else:
                    selected_stage_id = None
                    update_command()

            battle_stage_listbox.bind('<<ListboxSelect>>', on_battle_stage_select)

            # Initialize the battle stage list
            update_battle_stage_list()


        # Initialize the battle UI
        update_battle_ui()

        # Update NPC Monster list function
        def update_npc_monster_list():
            search_text = npc_search_var.get().lower()

            npc_monsters_data = self.npc_monsters_list

            # Clear the listbox
            npc_listbox.delete(0, tk.END)

            # Populate the listbox
            for entry in npc_monsters_data:
                display_text = f"{entry['name']} ({entry['id']})"
                if search_text in entry['name'].lower() or search_text in entry['id']:
                    npc_listbox.insert(tk.END, display_text)

        # Initialize the NPC monster list
        update_npc_monster_list()

        # Trace the toggle variable to update UI when changed
        toggle_var.trace('w', lambda *args: update_battle_ui())

        # Initial command update
        update_command()
