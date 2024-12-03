# tab_avatars.py

import tkinter as tk
from tkinter import ttk
from tkinter import VERTICAL, RIGHT, LEFT, Y, StringVar, IntVar, messagebox

class AvatarsTab:
    def __init__(self, notebook, avatars_list, command_manager, localization, server_type):
        self.notebook = notebook
        self.avatars_list = avatars_list
        self.command_manager = command_manager
        self.localization = localization
        self.server_type = server_type

        self.frame = ttk.Frame(notebook)
        self.init_tab()

    def init_tab(self):
        if self.server_type == 'LunarCore':
            self.init_lunarcore_ui()
        elif self.server_type == 'DanhengServer':
            self.init_dangheng_ui()

    def init_lunarcore_ui(self):
        # Create sub-tabs
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # Create 'Lineup & Properties' tab
        self.create_lunarcore_lineup_properties_tab()

    def create_lunarcore_lineup_properties_tab(self):
        tab_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab_frame, text=self.localization['Lineup_&_Properties'])

        # Main frame
        main_frame = tk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for Lineup section
        lineup_frame = tk.Frame(main_frame)
        lineup_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right frame for Properties section
        properties_frame = tk.Frame(main_frame)
        properties_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Lineup Section
        self.create_lunarcore_lineup_section(lineup_frame)

        # Properties Section
        self.create_lunarcore_properties_section(properties_frame)

    def create_lunarcore_lineup_section(self, parent_frame):
        # Title
        lineup_label = tk.Label(parent_frame, text=self.localization["Lineup"], font=("Arial", 12, "bold"))
        lineup_label.pack(pady=5)

        # Warning label
        warning_label = tk.Label(parent_frame, text=self.localization["USE_AT_YOUR_OWN_RISK"], fg="red", font=("Arial", 14, "bold"))
        warning_label.pack(pady=5)

        # Search functionality
        search_var = StringVar()
        search_label = tk.Label(parent_frame, text=self.localization["Search"])
        search_label.pack()
        search_entry = tk.Entry(parent_frame, textvariable=search_var)
        search_entry.pack()
        search_var.trace('w', lambda *args: update_avatar_list())

        # Avatar listbox
        avatar_frame = tk.Frame(parent_frame)
        avatar_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(avatar_frame, orient=VERTICAL)
        avatar_listbox = tk.Listbox(avatar_frame, width=30, height=15, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=avatar_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        avatar_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Lineup listbox
        lineup_list_label = tk.Label(parent_frame, text=self.localization["Lineup_List"])
        lineup_list_label.pack(pady=5)
        lineup_listbox = tk.Listbox(parent_frame, width=30, height=10, exportselection=False)
        lineup_listbox.pack(fill=tk.BOTH, expand=True)

        # Buttons
        buttons_frame = tk.Frame(parent_frame)
        buttons_frame.pack(pady=5)
        add_button = tk.Button(buttons_frame, text=self.localization["Add"], command=lambda: add_to_lineup())
        add_button.pack(side=LEFT, padx=5)
        remove_button = tk.Button(buttons_frame, text=self.localization["Remove"], command=lambda: remove_from_lineup())
        remove_button.pack(side=LEFT, padx=5)
        clear_button = tk.Button(buttons_frame, text=self.localization["Clear"], command=lambda: clear_lineup())
        clear_button.pack(side=LEFT, padx=5)

        # Initialize variables
        selected_avatar_id = None
        lineup_ids = []

        # Function to update avatar list based on search
        def update_avatar_list():
            search_text = search_var.get().lower()

            # Clear the listbox
            avatar_listbox.delete(0, tk.END)

            # Populate the listbox
            for entry in self.avatars_list:
                display_text = f"{entry['name']} ({entry['id']})"
                if search_text in entry['name'].lower() or search_text in entry['id']:
                    avatar_listbox.insert(tk.END, display_text)

        # Bind selection event
        def on_avatar_select(event):
            nonlocal selected_avatar_id
            selected_indices = avatar_listbox.curselection()
            if selected_indices:
                index = selected_indices[0]
                selected_avatar = avatar_listbox.get(index)
                if '(' in selected_avatar and ')' in selected_avatar:
                    id_str = selected_avatar.split('(')[-1].split(')')[0]
                    selected_avatar_id = id_str
                else:
                    selected_avatar_id = None
            else:
                selected_avatar_id = None

        avatar_listbox.bind('<<ListboxSelect>>', on_avatar_select)

        # Function to add selected avatar to lineup
        def add_to_lineup():
            if selected_avatar_id:
                lineup_ids.append(selected_avatar_id)
                lineup_listbox.insert(tk.END, selected_avatar_id)
                update_lineup_command()
            else:
                messagebox.showwarning(self.localization["Warning"], self.localization["No_avatar_selected"])

        # Function to remove selected avatar from lineup
        def remove_from_lineup():
            selected_indices = lineup_listbox.curselection()
            if selected_indices:
                index = selected_indices[0]
                avatar_id = lineup_listbox.get(index)
                lineup_listbox.delete(index)
                lineup_ids.remove(avatar_id)
                update_lineup_command()
            else:
                messagebox.showwarning(self.localization["Warning"], self.localization["No_avatar_selected_in_lineup"])

        # Function to clear the lineup
        def clear_lineup():
            lineup_listbox.delete(0, tk.END)
            lineup_ids.clear()
            update_lineup_command()

        # Function to update the lineup command
        def update_lineup_command():
            if lineup_ids:
                command = f"/lineup {' '.join(lineup_ids)}"
                self.command_manager.update_command(command)
            else:
                self.command_manager.update_command('')

        # Initialize the avatar list
        update_avatar_list()

    def create_lunarcore_properties_section(self, parent_frame):
        # Title
        properties_label = tk.Label(parent_frame, text=self.localization["Properties"], font=("Arial", 12, "bold"))
        properties_label.pack(pady=5)

        # Target selection
        target_label = tk.Label(parent_frame, text=self.localization["Target"])
        target_label.pack()
        target_var = StringVar(value='cur')
        target_options = ['cur', 'all', 'lineup']
        target_menu = ttk.OptionMenu(parent_frame, target_var, target_options[0], *target_options, command=lambda _: update_properties_command())
        target_menu.pack()

        # Level
        level_label = tk.Label(parent_frame, text=self.localization["Level_(1_80)"])
        level_label.pack()
        level_var = StringVar(value='1')
        level_entry = tk.Entry(parent_frame, textvariable=level_var)
        level_entry.pack()
        level_var.trace('w', lambda *args: update_properties_command())

        # Ascension
        ascension_label = tk.Label(parent_frame, text=self.localization["Ascension_(0_6)"])
        ascension_label.pack()
        ascension_var = StringVar(value='0')
        ascension_entry = tk.Entry(parent_frame, textvariable=ascension_var)
        ascension_entry.pack()
        ascension_var.trace('w', lambda *args: update_properties_command())

        # Eidolon
        eidolon_label = tk.Label(parent_frame, text=self.localization["Eidolon_(0_6)"])
        eidolon_label.pack()
        eidolon_var = StringVar(value='0')
        eidolon_entry = tk.Entry(parent_frame, textvariable=eidolon_var)
        eidolon_entry.pack()
        eidolon_var.trace('w', lambda *args: update_properties_command())

        # Skill Levels
        skill_label = tk.Label(parent_frame, text=self.localization["Skill_Levels_(1_12)"])
        skill_label.pack()
        skill_var = StringVar(value='1')
        skill_entry = tk.Entry(parent_frame, textvariable=skill_var)
        skill_entry.pack()
        skill_var.trace('w', lambda *args: update_properties_command())

        # Function to update the properties command
        def update_properties_command():
            target = target_var.get()
            level = level_var.get()
            ascension = ascension_var.get()
            eidolon = eidolon_var.get()
            skill = skill_var.get()

            # Validate inputs
            if not level.isdigit() or not (1 <= int(level) <= 80):
                self.command_manager.update_command('')
                return
            if not ascension.isdigit() or not (0 <= int(ascension) <= 6):
                self.command_manager.update_command('')
                return
            if not eidolon.isdigit() or not (0 <= int(eidolon) <= 6):
                self.command_manager.update_command('')
                return
            if not skill.isdigit() or not (1 <= int(skill) <= 12):
                self.command_manager.update_command('')
                return

            command = f"/avatar {target} lv{level} p{ascension} e{eidolon} s{skill}"
            self.command_manager.update_command(command)

        # Initialize the properties command
        update_properties_command()

    def init_dangheng_ui(self):
        # Create main frame
        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for avatar list
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right frame for properties
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create the avatar list section
        self.create_dangheng_avatar_list_section(left_frame)

        # Create the properties section
        self.create_dangheng_properties_section(right_frame)

    def create_dangheng_avatar_list_section(self, parent_frame):
        # Title
        avatar_label = tk.Label(parent_frame, text=self.localization["Avatars"], font=("Arial", 12, "bold"))
        avatar_label.pack(pady=5)

        # 'All' checkbox
        self.all_var = tk.BooleanVar(value=False)
        all_checkbox = tk.Checkbutton(parent_frame, text=self.localization["All"], variable=self.all_var, command=self.on_all_checkbox)
        all_checkbox.pack()

        # Search functionality
        search_var = StringVar()
        search_label = tk.Label(parent_frame, text=self.localization["Search"])
        search_label.pack()
        search_entry = tk.Entry(parent_frame, textvariable=search_var)
        search_entry.pack()
        search_var.trace('w', lambda *args: self.update_dangheng_avatar_list(search_var.get()))

        # Avatar listbox
        avatar_frame = tk.Frame(parent_frame)
        avatar_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(avatar_frame, orient=VERTICAL)
        self.avatar_listbox = tk.Listbox(avatar_frame, width=30, height=15, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=self.avatar_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.avatar_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Initialize variables
        self.selected_avatar_id = None

        # Bind selection event
        self.avatar_listbox.bind('<<ListboxSelect>>', self.on_avatar_select)

        # Initialize the avatar list
        self.update_dangheng_avatar_list('')

    def update_dangheng_avatar_list(self, search_text):
        search_text = search_text.lower()

        # Clear the listbox
        self.avatar_listbox.delete(0, tk.END)

        # Populate the listbox
        for entry in self.avatars_list:
            display_text = f"{entry['name']} ({entry['id']})"
            if search_text in entry['name'].lower() or search_text in entry['id']:
                self.avatar_listbox.insert(tk.END, display_text)

    def on_avatar_select(self, event):
        selected_indices = self.avatar_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_avatar = self.avatar_listbox.get(index)
            if '(' in selected_avatar and ')' in selected_avatar:
                id_str = selected_avatar.split('(')[-1].split(')')[0]
                self.selected_avatar_id = id_str
            else:
                self.selected_avatar_id = None
        else:
            self.selected_avatar_id = None

        # Uncheck 'All' checkbox when an avatar is selected
        self.all_var.set(False)

    def on_all_checkbox(self):
        if self.all_var.get():
            # Clear avatar selection
            self.avatar_listbox.selection_clear(0, tk.END)
            self.selected_avatar_id = '-1'  # -1 indicates all avatars
        else:
            self.selected_avatar_id = None

    def create_dangheng_properties_section(self, parent_frame):
        # Title
        properties_label = tk.Label(parent_frame, text=self.localization["Properties"], font=("Arial", 12, "bold"))
        properties_label.pack(pady=5)

        # Level
        level_frame = tk.Frame(parent_frame)
        level_frame.pack(pady=5)
        set_level_button = tk.Button(level_frame, text=self.localization["Set_Level"], command=self.execute_set_level)
        set_level_button.pack(side=tk.LEFT)
        level_label = tk.Label(level_frame, text=self.localization["Level_(1-80)"])
        level_label.pack(side=tk.LEFT)
        self.level_var = StringVar(value='80')
        level_entry = tk.Spinbox(level_frame, from_=1, to=80, textvariable=self.level_var, width=5)
        level_entry.pack(side=tk.LEFT)

        # Rank
        rank_frame = tk.Frame(parent_frame)
        rank_frame.pack(pady=5)
        set_rank_button = tk.Button(rank_frame, text=self.localization["Set_Rank"], command=self.execute_set_rank)
        set_rank_button.pack(side=tk.LEFT)
        rank_label = tk.Label(rank_frame, text=self.localization["Rank_(0-6)"])
        rank_label.pack(side=tk.LEFT)
        self.rank_var = StringVar(value='6')
        rank_entry = tk.Spinbox(rank_frame, from_=0, to=6, textvariable=self.rank_var, width=5)
        rank_entry.pack(side=tk.LEFT)

        # Talent
        talent_frame = tk.Frame(parent_frame)
        talent_frame.pack(pady=5)
        set_talent_button = tk.Button(talent_frame, text=self.localization["Set_Talent"], command=self.execute_set_talent)
        set_talent_button.pack(side=tk.LEFT)
        talent_label = tk.Label(talent_frame, text=self.localization["Talent_(0-10)"])
        talent_label.pack(side=tk.LEFT)
        self.talent_var = StringVar(value='10')
        talent_entry = tk.Spinbox(talent_frame, from_=0, to=10, textvariable=self.talent_var, width=5)
        talent_entry.pack(side=tk.LEFT)

        # Get Button
        get_button = tk.Button(parent_frame, text=self.localization["Get_Avatar"], command=self.execute_get_command)
        get_button.pack(pady=5)

    def execute_set_level(self):
        target_id = self.get_target_id()
        if not target_id:
            messagebox.showwarning(self.localization["Warning"], self.localization["No_avatar_selected"])
            return

        level = self.level_var.get()
        if not level.isdigit() or not (1 <= int(level) <= 80):
            messagebox.showwarning(self.localization["Warning"], self.localization["Invalid_level"])
            return

        level_command = f"/avatar level {target_id} {level}"
        self.command_manager.update_command(level_command)

    def execute_set_rank(self):
        target_id = self.get_target_id()
        if not target_id:
            messagebox.showwarning(self.localization["Warning"], self.localization["No_avatar_selected"])
            return

        rank = self.rank_var.get()
        if not rank.isdigit() or not (0 <= int(rank) <= 6):
            messagebox.showwarning(self.localization["Warning"], self.localization["Invalid_rank"])
            return

        rank_command = f"/avatar rank {target_id} {rank}"
        self.command_manager.update_command(rank_command)

    def execute_set_talent(self):
        target_id = self.get_target_id()
        if not target_id:
            messagebox.showwarning(self.localization["Warning"], self.localization["No_avatar_selected"])
            return

        talent = self.talent_var.get()
        if not talent.isdigit() or not (0 <= int(talent) <= 10):
            messagebox.showwarning(self.localization["Warning"], self.localization["Invalid_talent_level"])
            return

        talent_command = f"/avatar talent {target_id} {talent}"
        self.command_manager.update_command(talent_command)

    def execute_get_command(self):
        target_id = self.selected_avatar_id

        if not target_id or target_id == '-1':
            messagebox.showwarning(self.localization["Warning"], self.localization["Please_select_a_single_avatar_to_get"])
            return

        get_command = f"/avatar get {target_id}"
        self.command_manager.update_command(get_command)

    def get_target_id(self):
        if self.all_var.get():
            return '-1'
        elif self.selected_avatar_id:
            return self.selected_avatar_id
        else:
            return None
