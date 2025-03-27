import tkinter as tk
from tkinter import ttk
from tkinter import VERTICAL, RIGHT, LEFT, Y, StringVar, messagebox

class AvatarsTab:
    def __init__(self, notebook, avatars_list, command_manager, localization):
        self.notebook = notebook
        self.avatars_list = avatars_list
        self.command_manager = command_manager
        self.localization = localization

        self.frame = tk.Frame(notebook)
        self.init_tab()

    def init_tab(self):
        self.init_dangheng_ui()

    def init_dangheng_ui(self):
        # Создаем основной контейнер
        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть для списка аватаров
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Правая часть для свойств
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Создаем секцию списка аватаров
        self.create_dangheng_avatar_list_section(left_frame)
        # Создаем секцию свойств
        self.create_dangheng_properties_section(right_frame)

    def create_dangheng_avatar_list_section(self, parent_frame):
        # Заголовок
        avatar_label = tk.Label(parent_frame, text=self.localization.get("Avatars", "Avatars"), font=("Arial", 12, "bold"))
        avatar_label.pack(pady=5)

        # Чекбокс "All"
        self.all_var = tk.BooleanVar(value=False)
        all_checkbox = tk.Checkbutton(parent_frame, text=self.localization.get("All", "All"), variable=self.all_var,
                                      command=self.on_all_checkbox)
        all_checkbox.pack()

        # Поисковая строка
        search_var = StringVar()
        search_label = tk.Label(parent_frame, text=self.localization.get("Search", "Search"))
        search_label.pack()
        search_entry = tk.Entry(parent_frame, textvariable=search_var)
        search_entry.pack()
        search_var.trace('w', lambda *args: self.update_dangheng_avatar_list(search_var.get()))

        # Список аватаров
        avatar_frame = tk.Frame(parent_frame)
        avatar_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(avatar_frame, orient=VERTICAL)
        self.avatar_listbox = tk.Listbox(avatar_frame, width=30, height=15, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=self.avatar_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.avatar_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Инициализация переменной выбранного аватара
        self.selected_avatar_id = None

        # Обработка выбора аватара
        self.avatar_listbox.bind('<<ListboxSelect>>', self.on_avatar_select)

        self.update_dangheng_avatar_list('')

    def update_dangheng_avatar_list(self, search_text):
        search_text = search_text.lower()
        self.avatar_listbox.delete(0, tk.END)
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
                self.selected_avatar_id = selected_avatar.split('(')[-1].split(')')[0]
            else:
                self.selected_avatar_id = None
        else:
            self.selected_avatar_id = None

        # Снимаем отметку с "All", если выбран отдельный аватар
        self.all_var.set(False)

    def on_all_checkbox(self):
        if self.all_var.get():
            self.avatar_listbox.selection_clear(0, tk.END)
            self.selected_avatar_id = '-1'  # -1 означает выбор всех аватаров
        else:
            self.selected_avatar_id = None

    def create_dangheng_properties_section(self, parent_frame):
        # Заголовок секции
        properties_label = tk.Label(parent_frame, text=self.localization.get("Properties", "Properties"), font=("Arial", 12, "bold"))
        properties_label.pack(pady=5)

        # Уровень
        level_frame = tk.Frame(parent_frame)
        level_frame.pack(pady=5)
        set_level_button = tk.Button(level_frame, text=self.localization.get("Set_Level", "Set Level"), command=self.execute_set_level)
        set_level_button.pack(side=tk.LEFT)
        level_label = tk.Label(level_frame, text=self.localization.get("Level_(1-80)", "Level (1-80)"))
        level_label.pack(side=tk.LEFT)
        self.level_var = StringVar(value='80')
        level_entry = tk.Spinbox(level_frame, from_=1, to=80, textvariable=self.level_var, width=5)
        level_entry.pack(side=tk.LEFT)

        # Ранг
        rank_frame = tk.Frame(parent_frame)
        rank_frame.pack(pady=5)
        set_rank_button = tk.Button(rank_frame, text=self.localization.get("Set_Rank", "Set Rank"), command=self.execute_set_rank)
        set_rank_button.pack(side=tk.LEFT)
        rank_label = tk.Label(rank_frame, text=self.localization.get("Rank_(0-6)", "Rank (0-6)"))
        rank_label.pack(side=tk.LEFT)
        self.rank_var = StringVar(value='6')
        rank_entry = tk.Spinbox(rank_frame, from_=0, to=6, textvariable=self.rank_var, width=5)
        rank_entry.pack(side=tk.LEFT)

        # Talent
        talent_frame = tk.Frame(parent_frame)
        talent_frame.pack(pady=5)
        set_talent_button = tk.Button(talent_frame, text=self.localization.get("Set_Talent", "Set Talent"), command=self.execute_set_talent)
        set_talent_button.pack(side=tk.LEFT)
        talent_label = tk.Label(talent_frame, text=self.localization.get("Talent_(0-10)", "Talent (0-10)"))
        talent_label.pack(side=tk.LEFT)
        self.talent_var = StringVar(value='10')
        talent_entry = tk.Spinbox(talent_frame, from_=0, to=10, textvariable=self.talent_var, width=5)
        talent_entry.pack(side=tk.LEFT)

        # Кнопка для получения команды
        get_button = tk.Button(parent_frame, text=self.localization.get("Get_Avatar", "Get Avatar"), command=self.execute_get_command)
        get_button.pack(pady=5)

        # --- Новый раздел: Main Character ---
        main_char_frame = tk.LabelFrame(parent_frame, text=self.localization.get("Main_Character", "Main Character"))
        main_char_frame.pack(pady=5, fill=tk.X)
        # Подраздел Gender
        gender_label = tk.Label(main_char_frame, text=self.localization.get("Gender", "Gender"))
        gender_label.pack(pady=(5, 0))
        gender_buttons_frame = tk.Frame(main_char_frame)
        gender_buttons_frame.pack(pady=5)
        male_button = tk.Button(gender_buttons_frame, text=self.localization.get("Male", "Male"),
                                command=lambda: self.command_manager.update_command("/hero gender 1"))
        male_button.pack(side=tk.LEFT, padx=2)
        female_button = tk.Button(gender_buttons_frame, text=self.localization.get("Female", "Female"),
                                  command=lambda: self.command_manager.update_command("/hero gender 2"))
        female_button.pack(side=tk.LEFT, padx=2)

        # --- Новый раздел: Path ---
        path_frame = tk.LabelFrame(parent_frame, text=self.localization.get("Path", "Path"))
        path_frame.pack(pady=5, fill=tk.X)
        path_buttons_frame = tk.Frame(path_frame)
        path_buttons_frame.pack(pady=5)
        destruction_button = tk.Button(path_buttons_frame, text=self.localization.get("Destruction", "Destruction"),
                                       command=lambda: self.command_manager.update_command("/hero type 8001"))
        destruction_button.pack(side=tk.LEFT, padx=2)
        preservation_button = tk.Button(path_buttons_frame, text=self.localization.get("Preservation", "Preservation"),
                                        command=lambda: self.command_manager.update_command("/hero type 8003"))
        preservation_button.pack(side=tk.LEFT, padx=2)
        harmony_button = tk.Button(path_buttons_frame, text=self.localization.get("Harmony", "Harmony"),
                                   command=lambda: self.command_manager.update_command("/hero type 8005"))
        harmony_button.pack(side=tk.LEFT, padx=2)
        remembrance_button = tk.Button(path_buttons_frame, text=self.localization.get("Remembrance", "Remembrance"),
                                       command=lambda: self.command_manager.update_command("/hero type 8007"))
        remembrance_button.pack(side=tk.LEFT, padx=2)

        # --- Новый раздел: Lineup ---
        lineup_frame = tk.LabelFrame(parent_frame, text=self.localization.get("Lineup", "Lineup"))
        lineup_frame.pack(pady=5, fill=tk.X)
        lineup_buttons_frame = tk.Frame(lineup_frame)
        lineup_buttons_frame.pack(pady=5)
        refill_button = tk.Button(lineup_buttons_frame, text=self.localization.get("Refill_Skillpoints", "Refill Skillpoints"),
                                  command=lambda: self.command_manager.update_command("/lineup mp 5"))
        refill_button.pack(side=tk.LEFT, padx=2)
        heal_button = tk.Button(lineup_buttons_frame, text=self.localization.get("Heal", "Heal"),
                                command=lambda: self.command_manager.update_command("/lineup heal"))
        heal_button.pack(side=tk.LEFT, padx=2)

    def execute_set_level(self):
        target_id = self.get_target_id()
        if not target_id:
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("No_avatar_selected", "No avatar selected"))
            return

        level = self.level_var.get()
        if not level.isdigit() or not (1 <= int(level) <= 80):
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("Invalid_level", "Invalid level"))
            return

        level_command = f"/avatar level {target_id} {level}"
        self.command_manager.update_command(level_command)

    def execute_set_rank(self):
        target_id = self.get_target_id()
        if not target_id:
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("No_avatar_selected", "No avatar selected"))
            return

        rank = self.rank_var.get()
        if not rank.isdigit() or not (0 <= int(rank) <= 6):
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("Invalid_rank", "Invalid rank"))
            return

        rank_command = f"/avatar rank {target_id} {rank}"
        self.command_manager.update_command(rank_command)

    def execute_set_talent(self):
        target_id = self.get_target_id()
        if not target_id:
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("No_avatar_selected", "No avatar selected"))
            return

        talent = self.talent_var.get()
        if not talent.isdigit() or not (0 <= int(talent) <= 10):
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("Invalid_talent_level", "Invalid talent level"))
            return

        talent_command = f"/avatar talent {target_id} {talent}"
        self.command_manager.update_command(talent_command)

    def execute_get_command(self):
        target_id = self.selected_avatar_id
        if not target_id or target_id == '-1':
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("Please_select_a_single_avatar_to_get", "Please select a single avatar to get"))
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
