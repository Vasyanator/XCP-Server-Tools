import tkinter as tk
from tkinter import ttk, VERTICAL, RIGHT, LEFT, Y, StringVar, messagebox

class SimpleListTab:
    def __init__(self, notebook, items, command_manager, localization, tab_key):
        self.command_manager = command_manager
        self.localization = localization
        self.items = items  # Ожидается список словарей с ключами 'id' и 'name'
        self.selected_item_id = None

        # Создаём фрейм вкладки
        self.tab_frame = ttk.Frame(notebook)
        notebook.add(self.tab_frame, text=localization.get(tab_key, tab_key))

        # Основной фрейм
        main_frame = tk.Frame(self.tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Секция поиска (только по имени)
        search_frame = tk.Frame(main_frame)
        search_frame.pack(pady=5, padx=5, anchor='w')
        search_label = tk.Label(search_frame, text=localization.get("Search", "Search"))
        search_label.pack(side=tk.LEFT)
        self.search_var = StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', self.on_search)

        # Список с прокруткой
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = tk.Scrollbar(list_frame, orient=VERTICAL)
        self.listbox = tk.Listbox(list_frame, width=80, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        # Панель команд
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=5)
        get_button = tk.Button(button_frame, text=localization.get("Get_Blessing", "Get Buff"), command=self.execute_get)
        get_button.grid(row=0, column=0, padx=5)
        enhance_selected_button = tk.Button(button_frame, text=localization.get("Enhance_Selected", "Enhance Selected"), command=self.execute_enhance_selected)
        enhance_selected_button.grid(row=0, column=1, padx=5)
        enhance_all_button = tk.Button(button_frame, text=localization.get("Enhance_All", "Enhance All"), command=self.execute_enhance_all)
        enhance_all_button.grid(row=0, column=2, padx=5)

        self.update_list()

    def update_list(self):
        self.listbox.delete(0, tk.END)
        search_text = self.search_var.get().lower()
        for item in self.items:
            if search_text and search_text not in item['name'].lower():
                continue
            display_text = f"{item['name']} ({item['id']})"
            self.listbox.insert(tk.END, display_text)

    def on_search(self, event=None):
        self.update_list()

    def on_select(self, event):
        selected_indices = self.listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_text = self.listbox.get(index)
            if '(' in selected_text and ')' in selected_text:
                id_str = selected_text.split('(')[-1].split(')')[0]
                self.selected_item_id = id_str
            else:
                self.selected_item_id = None
        else:
            self.selected_item_id = None

    def execute_get(self):
        if not self.selected_item_id:
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("No_buff_selected", "No buff selected"))
            return
        command = f"/rogue buff {self.selected_item_id}"
        self.command_manager.update_command(command)

    def execute_enhance_selected(self):
        if not self.selected_item_id:
            messagebox.showwarning(self.localization.get("Warning", "Warning"), self.localization.get("No_buff_selected", "No buff selected"))
            return
        command = f"/rogue enhance {self.selected_item_id}"
        self.command_manager.update_command(command)

    def execute_enhance_all(self):
        command = "/rogue enhance -1"
        self.command_manager.update_command(command)

class VirtualUniverseMiscTab:
    def __init__(self, notebook, rogue_buffs_food, rogue_buffs_various, rogue_buffs_from_entities, rogue_buffs_other, command_manager, localization):
        self.localization = localization
        self.command_manager = command_manager

        # Основной фрейм для новой группы вкладок
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=localization.get("Misc_Rogue_Buffs", "Misc Rogue Buffs"))

        # Создаём суб-ноутбук для простых вкладок
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка для rogue_buffs_food
        self.food_tab = SimpleListTab(
            self.sub_notebook,
            rogue_buffs_food,
            command_manager,
            localization,
            "Rogue_Buffs_Food"
        )

        # Вкладка для rogue_buffs_various
        self.various_tab = SimpleListTab(
            self.sub_notebook,
            rogue_buffs_various,
            command_manager,
            localization,
            "Rogue_Buffs_Various"
        )

        # Вкладка для объединённого списка: rogue_buffs_from_entities + rogue_buffs_other
        combined_list = rogue_buffs_from_entities + rogue_buffs_other
        self.entities_other_tab = SimpleListTab(
            self.sub_notebook,
            combined_list,
            command_manager,
            localization,
            "Rogue_Buffs_Entities_Other"
        )
