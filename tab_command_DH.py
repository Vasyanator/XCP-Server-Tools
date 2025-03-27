import tkinter as tk
from tkinter import ttk
import json

# Словари для Frequently Commands и Starter Commands
FREQUENT_COMMANDS = {
    "Unstuck": "/unstuck",
    "reload_banner_config": "/reload banner"
}

STARTER_COMMANDS = {
    "All_avatars": "/giveall avatars r6 l80",
    "All_equipment": "/giveall equipment r6 l80 x5",
    "Give_everything_else": "/giveall unlock",
    "unlock_all_missions": "/unlockall mission",
    "finish_all_tutorials": "/unlockall tutorial",
    "unlock_SU": "/unlockall rogue",
    "Level 80": "/setlevel 80",
    "Unlock_scene": "/scene unlockall",

}

class CommandTab:
    def __init__(self, parent, command_manager, localization, server_type):
        self.frame = tk.Frame(parent)
        self.command_manager = command_manager
        self.localization = localization

        # Создаем внутренний Notebook для двух подтабов
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # Подтаб Frequently Commands
        self.frequently_frame = tk.Frame(self.sub_notebook)
        tab_frequently_text = self.localization.get("tab_frequently", "Frequently Commands")
        self.sub_notebook.add(self.frequently_frame, text=tab_frequently_text)
        self.setup_frequently_commands()

        # Подтаб Custom Commands
        self.custom_frame = tk.Frame(self.sub_notebook)
        tab_custom_text = self.localization.get("tab_custom", "Custom Commands")
        self.sub_notebook.add(self.custom_frame, text=tab_custom_text)
        self.setup_custom_commands()

    def setup_frequently_commands(self):
        # Секция Frequently Commands
        section_frequent_text = self.localization.get("section_frequently", "Frequently Commands")
        self.section_frequent = ttk.LabelFrame(self.frequently_frame, text=section_frequent_text)
        self.section_frequent.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for title, command in FREQUENT_COMMANDS.items():
            localized_title = self.localization.get("commands", {}).get(title, title)
            btn = tk.Button(self.section_frequent, text=localized_title,
                            command=lambda cmd=command: self.generate_command(cmd))
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Секция Starter Commands
        section_starter_text = self.localization.get("section_starter", "Starter Commands")
        self.section_starter = ttk.LabelFrame(self.frequently_frame, text=section_starter_text)
        self.section_starter.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for title, command in STARTER_COMMANDS.items():
            localized_title = self.localization.get("commands", {}).get(title, title)
            btn = tk.Button(self.section_starter, text=localized_title,
                            command=lambda cmd=command: self.generate_command(cmd))
            btn.pack(side=tk.LEFT, padx=5, pady=5)

    def setup_custom_commands(self):
        self.custom_commands_file = "custom_commands_DH.json"
        self.custom_commands = self.load_custom_commands()

        # Фрейм для отображения кнопок кастомных команд
        self.buttons_frame = tk.Frame(self.custom_frame)
        self.buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.custom_buttons = {}  # ключ: имя команды, значение: виджет кнопки
        self.selected_key = None  # Текущая выбранная команда
        self.draw_custom_command_buttons()

        # Фрейм для редактирования названия и команды
        self.edit_frame = tk.Frame(self.custom_frame)
        self.edit_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(self.edit_frame, text=self.localization.get("Name:", "Name:")).pack(side=tk.LEFT)
        self.name_entry = tk.Entry(self.edit_frame)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.edit_frame, text=self.localization.get("Command:", "Command:")).pack(side=tk.LEFT)
        self.command_entry = tk.Entry(self.edit_frame, width=40)
        self.command_entry.pack(side=tk.LEFT, padx=5)

        # Фрейм для кнопок управления кастомными командами
        self.edit_buttons_frame = tk.Frame(self.custom_frame)
        self.edit_buttons_frame.pack(fill=tk.X, padx=10, pady=5)

        self.add_button = tk.Button(self.edit_buttons_frame, text=self.localization.get("Add Command:", "Add Command:"), command=self.add_custom_command)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.overwrite_button = tk.Button(self.edit_buttons_frame, text=self.localization.get("Rewrite", "Rewrite"), command=self.overwrite_custom_command)
        self.overwrite_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.edit_buttons_frame, text=self.localization.get("Delete", "Delete"), command=self.delete_custom_command)
        self.delete_button.pack(side=tk.LEFT, padx=5)

    def load_custom_commands(self):
        try:
            with open(self.custom_commands_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_custom_commands(self):
        with open(self.custom_commands_file, "w", encoding="utf-8") as f:
            json.dump(self.custom_commands, f, ensure_ascii=False, indent=4)

    def draw_custom_command_buttons(self):
        # Удаляем все существующие кнопки
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        self.custom_buttons.clear()
        for key, command in self.custom_commands.items():
            btn = tk.Button(self.buttons_frame, text=key, relief=tk.RAISED,
                            command=lambda k=key: self.select_custom_command(k))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.custom_buttons[key] = btn

    def select_custom_command(self, key):
        # Снимаем выделение с предыдущей кнопки
        if self.selected_key and self.selected_key in self.custom_buttons:
            self.custom_buttons[self.selected_key].config(relief=tk.RAISED)
        self.selected_key = key
        self.custom_buttons[key].config(relief=tk.SUNKEN)
        # Загружаем данные выбранной команды в поля ввода
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, key)
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, self.custom_commands[key])
        # Обновляем глобальную командную строку главного окна
        self.command_manager.update_command(self.custom_commands[key])

    def overwrite_custom_command(self):
        if not self.selected_key:
            return
        new_name = self.name_entry.get().strip()
        new_command = self.command_entry.get().strip()
        if not new_name or not new_command:
            return
        # Если изменилось название, удаляем старую запись
        if new_name != self.selected_key:
            del self.custom_commands[self.selected_key]
            self.selected_key = new_name
        self.custom_commands[new_name] = new_command
        self.save_custom_commands()
        self.draw_custom_command_buttons()
        if new_name in self.custom_buttons:
            self.select_custom_command(new_name)

    def delete_custom_command(self):
        if not self.selected_key:
            return
        del self.custom_commands[self.selected_key]
        self.save_custom_commands()
        self.draw_custom_command_buttons()
        self.selected_key = None
        self.name_entry.delete(0, tk.END)
        self.command_entry.delete(0, tk.END)

    def add_custom_command(self):
        new_name = self.name_entry.get().strip()
        new_command = self.command_entry.get().strip()
        if not new_name or not new_command:
            return
        if new_name in self.custom_commands:
            # Можно добавить сообщение об ошибке, если команда с таким именем уже существует
            return
        self.custom_commands[new_name] = new_command
        self.save_custom_commands()
        self.draw_custom_command_buttons()

    def generate_command(self, cmd):
        # Вызывается при нажатии на кнопки во вкладках Frequently и Starter Commands
        self.command_manager.update_command(cmd)
