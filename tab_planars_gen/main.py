import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import VERTICAL, RIGHT, LEFT, Y, END

from tab_planars_gen.stats_id import substats, substats_levels, stats_3, stats_4, stats_5, stats_6
from tab_planars_gen.substats_interface import SubstatsInterface

class PlanarsTab:

    def __init__(self, notebook, items, command_manager, localization, server_type):
        self.localization = localization
        self.server_type = server_type  # 'LunarCore' or 'DanhengServer'

        # Localize stat dictionaries
        self.localized_substats = self.localize_stat_keys(substats)
        self.localized_stats_3 = self.localize_stat_keys(stats_3)
        self.localized_stats_4 = self.localize_stat_keys(stats_4)
        self.localized_stats_5 = self.localize_stat_keys(stats_5)
        self.localized_stats_6 = self.localize_stat_keys(stats_6)

        # For LunarCore, we need substat levels
        if self.server_type == 'LunarCore':
            self.localized_substats_levels = self.localize_stat_keys(substats_levels)
        else:
            self.localized_substats_levels = None

        self.notebook = notebook
        self.items = items
        self.command_manager = command_manager
        self.frame = ttk.Frame(notebook)
        self.init_tab()

    def init_tab(self):
        self.selected_item_id = None
        self.additional_stats = {}
        self.type_var = tk.StringVar(value='default')
        self.rarity_var = tk.StringVar(value='5')
        self.search_var = tk.StringVar()
        self.main_stat_var = tk.StringVar()
        self.main_stat_options = [self.localization['Select_an_item_first']]
        self.main_stat_var.set(self.main_stat_options[0])

        # Variables that differ between servers
        if self.server_type == 'DanhengServer':
            self.amount_var = tk.StringVar(value='1')  # For amount selection
        elif self.server_type == 'LunarCore':
            self.level_var = tk.StringVar(value='15')

        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Type selection
        type_label = tk.Label(right_frame, text=self.localization['Select_Type'])
        type_label.pack()
        type_frame = tk.Frame(right_frame)
        type_frame.pack()
        default_radio = tk.Radiobutton(type_frame, text=self.localization['Default'], variable=self.type_var, value='default', command=self.update_item_list)
        default_radio.pack(side=tk.LEFT)
        planars_radio = tk.Radiobutton(type_frame, text=self.localization['Planars'], variable=self.type_var, value='planars', command=self.update_item_list)
        planars_radio.pack(side=tk.LEFT)

        # Rarity selection
        rarity_label = tk.Label(right_frame, text=self.localization['Select_Rarity:'])
        rarity_label.pack()
        rarity_combobox = ttk.Combobox(right_frame, textvariable=self.rarity_var, values=[str(i) for i in range(2, 6)], state='readonly')
        rarity_combobox.pack()
        rarity_combobox.bind('<<ComboboxSelected>>', self.update_item_list)

        # Search bar
        search_label = tk.Label(right_frame, text=self.localization['Search:'])
        search_label.pack()
        search_entry = tk.Entry(right_frame, textvariable=self.search_var)
        search_entry.pack()
        self.search_var.trace('w', lambda *args: self.update_item_list())

        # Item listbox
        item_frame = tk.Frame(right_frame)
        item_frame.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(item_frame, orient=VERTICAL)
        self.item_listbox = tk.Listbox(item_frame, width=50, height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.item_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.item_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)
        self.item_listbox.bind('<<ListboxSelect>>', self.on_item_select)

        # Main stat selection
        self.main_stat_label = tk.Label(left_frame, text=self.localization['Main_Stat:'])
        self.main_stat_label.pack()
        self.main_stat_menu = tk.OptionMenu(left_frame, self.main_stat_var, *self.main_stat_options)
        self.main_stat_menu.config(state='disabled')
        self.main_stat_menu.pack()

        # Level selection
        level_label = tk.Label(left_frame, text=self.localization['Select_Level:'])
        level_label.pack()
        if self.server_type == 'LunarCore':
            level_spinbox = tk.Spinbox(left_frame, from_=1, to=15, textvariable=self.level_var, width=5, command=self.update_command)
            level_spinbox.pack()
            self.level_var.trace('w', lambda *args: self.update_command())
        elif self.server_type == 'DanhengServer':
            self.level_var = tk.StringVar(value='15')
            level_spinbox = tk.Spinbox(left_frame, from_=1, to=9999, textvariable=self.level_var, width=5, command=self.update_command)
            level_spinbox.pack()
            self.level_var.trace('w', lambda *args: self.update_command())

            # Amount selection
            amount_label = tk.Label(left_frame, text=self.localization['Select_Amount:'])
            amount_label.pack()
            amount_spinbox = tk.Spinbox(left_frame, from_=1, to=99, textvariable=self.amount_var, width=5, command=self.update_command)
            amount_spinbox.pack()
            self.amount_var.trace('w', lambda *args: self.update_command())

        # Create SubstatsInterface instance
        self.substats_interface = SubstatsInterface(
            parent_frame=left_frame,
            localization=self.localization,
            server_type=self.server_type,
            command_manager=self.command_manager,
            localized_substats=self.localized_substats,
            localized_substats_levels=self.localized_substats_levels,
            additional_stats=self.additional_stats,
            update_command_callback=self.update_command,
            get_main_stat_callback=self.get_main_stat  # Pass a method to get the current main stat
        )

        self.update_item_list()
        self.main_stat_var.trace('w', self.update_command)
        self.update_command()

    def localize_stat_keys(self, original_dict):
        return {
            self.localization['Stats'].get(key, key): value
            for key, value in original_dict.items()
        }
    
    def get_main_stat(self):
        # Return the current main stat name
        main_stat_name = self.main_stat_var.get()
        if main_stat_name in ['Fixed', 'No Main Stats Available']:
            return None
        return main_stat_name

    def update_item_list(self, *args):
        type_selected = self.type_var.get()
        rarity_selected = self.rarity_var.get()
        search_text = self.search_var.get().lower()
        items = [item for item in self.items if item.type == type_selected and str(item.rarity) == rarity_selected]
        groups = {}
        for item in items:
            id_prefix = item.id[:-1]
            if id_prefix not in groups:
                groups[id_prefix] = []
            groups[id_prefix].append(item)
        self.item_listbox.delete(0, tk.END)
        for group in groups.values():
            group_items = []
            for item in group:
                display_text = f'{item.title} ({item.id})'
                if search_text in item.title.lower() or search_text in item.id:
                    group_items.append(display_text)
            if group_items:
                for display_text in group_items:
                    self.item_listbox.insert(tk.END, display_text)
                self.item_listbox.insert(tk.END, '---')
        if self.item_listbox.size() > 0:
            last_item = self.item_listbox.get(tk.END)
            if last_item == '---':
                self.item_listbox.delete(tk.END)
        self.command_manager.update_command('')

    def on_item_select(self, event):
        selected_indices = self.item_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_item = self.item_listbox.get(index)
            if selected_item != '---':
                if '(' in selected_item and ')' in selected_item:
                    id_str = selected_item.split('(')[-1].split(')')[0]
                    self.selected_item_id = id_str
                    last_digit = int(id_str[-1])
                    if last_digit in [1, 2]:
                        self.main_stat_label.config(text=self.localization['Main_Stat:_Fixed'])
                        self.main_stat_var.set('Fixed')
                        self.main_stat_menu['menu'].delete(0, 'end')
                        self.main_stat_menu.config(state='disabled')
                    else:
                        self.main_stat_menu.config(state='normal')
                        self.main_stat_label.config(text=self.localization['Select_Main_Stat:'])
                        if last_digit == 3:
                            main_stats = self.localized_stats_3
                        elif last_digit == 4:
                            main_stats = self.localized_stats_4
                        elif last_digit == 5:
                            main_stats = self.localized_stats_5
                        elif last_digit == 6:
                            main_stats = self.localized_stats_6
                        else:
                            main_stats = {}
                        self.main_stat_options = list(main_stats.keys())
                        if self.main_stat_options:
                            self.main_stat_var.set(self.main_stat_options[0])
                            self.main_stat_menu['menu'].delete(0, 'end')
                            for option in self.main_stat_options:
                                self.main_stat_menu['menu'].add_command(label=option, command=tk._setit(self.main_stat_var, option, self.update_command))
                        else:
                            self.main_stat_var.set('No Main Stats Available')
                            self.main_stat_menu['menu'].delete(0, 'end')
                            self.main_stat_menu['menu'].add_command(label=self.localization['No_Main_Stats_Available'], command=tk._setit(self.main_stat_var, 'No Main Stats Available', self.update_command))
                            self.main_stat_menu.config(state='disabled')
                    self.update_command()
                else:
                    self.command_manager.update_command('')
            else:
                self.command_manager.update_command('')
        else:
            self.command_manager.update_command('')

    def update_command(self, *args):
        if not self.selected_item_id:
            self.command_manager.update_command('')
            return

        command_parts = []

        # Command structure differs based on server type
        if self.server_type == 'LunarCore':
            if self.substats_interface.additional_levels_var.get():
                command_parts.append(f'/relics {self.selected_item_id}')
            else:
                command_parts.append(f'/give {self.selected_item_id}')
        elif self.server_type == 'DanhengServer':
            command_parts.append(f'/relic {self.selected_item_id}')

        last_digit = int(self.selected_item_id[-1])

        # Main stat handling
        if last_digit not in [1, 2]:
            main_stat_name = self.main_stat_var.get()
            if main_stat_name in ['Fixed', 'No Main Stats Available']:
                main_affix_id = '1'  # Use main characteristic 1 if fixed or not available
            else:
                if last_digit == 3:
                    main_stats = self.localized_stats_3
                elif last_digit == 4:
                    main_stats = self.localized_stats_4
                elif last_digit == 5:
                    main_stats = self.localized_stats_5
                elif last_digit == 6:
                    main_stats = self.localized_stats_6
                else:
                    main_stats = {}
                main_affix_id = main_stats.get(main_stat_name, '1')  # Default to '1' if not found

            if self.server_type == 'LunarCore':
                if main_affix_id != '1':
                    command_parts.append(f's{main_affix_id}')
            elif self.server_type == 'DanhengServer':
                command_parts.append(f'{main_affix_id}')
        else:
            # Fixed main stat
            if self.server_type == 'DanhengServer':
                command_parts.append('1')  # Use main characteristic 1

        # Additional stats
        for stat_name, data in self.additional_stats.items():
            stat_id = self.localized_substats.get(stat_name)
            if stat_id:
                if self.server_type == 'LunarCore':
                    quantity, level_index = data
                    if self.substats_interface.additional_levels_var.get() and level_index is not None:
                        level_in_command = level_index * quantity  # Level is index + 1
                        command_parts.append(f'{stat_id}:{quantity}:{level_in_command}')
                    else:
                        command_parts.append(f'{stat_id}:{quantity}')
                elif self.server_type == 'DanhengServer':
                    quantity = data  # In DanhengServer, data is just quantity
                    command_parts.append(f'{stat_id}:{quantity}')

        # Level
        level = self.level_var.get()
        if self.server_type == 'LunarCore':
            command_parts.append(f'lv{level}')
        elif self.server_type == 'DanhengServer':
            command_parts.append(f'l{level}')

        # Additional options
        if self.server_type == 'LunarCore':
            if self.substats_interface.maxsteps_var.get():
                command_parts.append('-maxsteps')
        elif self.server_type == 'DanhengServer':
            amount = self.amount_var.get()
            command_parts.append(f'x{amount}')

        command = ' '.join(command_parts)
        self.command_manager.update_command(command)

