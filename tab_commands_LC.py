# tab_commands.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os

class CommandsTab:
    def __init__(self, notebook,  command_manager, localization, server_type):
        self.notebook = notebook
        self.start_commands_dict = {
            "Give all materials": "/giveall materials x9999",
            "Give all avatars": "/giveall avatars lv80 p6 e6 s10",
            "Give all lightcones": "/giveall lightcones x5 lv80 r5",
            "Give all relics": "/giveall relics x5 lv15",
            "Give all usables": "/giveall usables x200",
            "trailblazer level 70": "/setlevel 70",
            "Female MC": "/gender female",
            "Male MC": "/gender mmale",
            # Add more commands as needed
            }
        self.base_commands_dict = {
            "Refill characters energy": "/energy",
            "Heal avatars": "/heal",
            "Refill skill points": "/refill",
            # Add more commands as needed
            }
        self.command_manager = command_manager
        self.custom_commands_file = 'custom_commands.json'
        self.localization = localization
        self.server_type = server_type

        self.frame = ttk.Frame(notebook)
        self.init_tab()

    def init_tab(self):
        # Create sub-tabs
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # Create 'Base Commands' tab
        self.create_base_commands_tab()

        # Create 'Custom Commands' tab
        self.create_custom_commands_tab()

    def create_base_commands_tab(self):
        tab_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab_frame, text='Base Commands')

        # Create frames for Start Commands and Base Commands
        start_commands_frame = ttk.LabelFrame(tab_frame, text=self.localization["Start_Commands"])
        start_commands_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        base_commands_frame = ttk.LabelFrame(tab_frame, text=self.localization["Base_Commands"])
        base_commands_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Display buttons for Start Commands
        for display_name, command in self.start_commands_dict.items():
            button = tk.Button(start_commands_frame, text=display_name, command=lambda cmd=command: self.command_manager.update_command(cmd))
            button.pack(side=tk.LEFT, padx=5, pady=5)

        # Display buttons for Base Commands
        for display_name, command in self.base_commands_dict.items():
            button = tk.Button(base_commands_frame, text=display_name, command=lambda cmd=command: self.command_manager.update_command(cmd))
            button.pack(side=tk.LEFT, padx=5, pady=5)

    def create_custom_commands_tab(self):
        tab_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab_frame, text='Custom Commands')

        # Frame for command buttons
        commands_frame = ttk.LabelFrame(tab_frame, text=self.localization["Custom_Commands"])
        commands_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load custom commands
        self.custom_commands_dict = self.load_custom_commands()

        # Listbox to display custom commands
        self.command_listbox = tk.Listbox(commands_frame)
        self.command_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_custom_commands_listbox()

        # Bind selection event
        self.command_listbox.bind('<<ListboxSelect>>', self.on_custom_command_select)

        # Bottom frame for name entry and buttons
        bottom_frame = tk.Frame(tab_frame)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        name_label = tk.Label(bottom_frame, text=self.localization["Name"])
        name_label.pack(side=tk.LEFT)

        self.name_var = tk.StringVar()
        name_entry = tk.Entry(bottom_frame, textvariable=self.name_var)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        save_button = tk.Button(bottom_frame, text=self.localization["Save"], command=self.save_custom_command)
        save_button.pack(side=tk.LEFT, padx=5)

        load_button = tk.Button(bottom_frame, text=self.localization["Load"], command=self.load_custom_command)
        load_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(bottom_frame, text=self.localization["Delete"], command=self.delete_custom_command)
        delete_button.pack(side=tk.LEFT, padx=5)

    def load_custom_commands(self):
        if os.path.exists(self.custom_commands_file):
            try:
                with open(self.custom_commands_file, 'r', encoding='utf-8') as f:
                    custom_commands = json.load(f)
                    return custom_commands
            except Exception as e:
                messagebox.showerror(self.localization["Error"], f"Failed to load custom commands: {e}")
                return {}
        else:
            return {}

    def save_custom_commands(self):
        try:
            with open(self.custom_commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_commands_dict, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror(self.localization["Error"], f"Failed to save custom commands: {e}")

    def update_custom_commands_listbox(self):
        self.command_listbox.delete(0, tk.END)
        for display_name in self.custom_commands_dict.keys():
            self.command_listbox.insert(tk.END, display_name)

    def on_custom_command_select(self, event):
        selected_indices = self.command_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            display_name = self.command_listbox.get(index)
            command = self.custom_commands_dict.get(display_name)
            if command:
                self.command_manager.update_command(command)
                self.name_var.set(display_name)
        else:
            self.command_manager.update_command('')
            self.name_var.set('')

    def save_custom_command(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning(self.localization["Warning"], "Please enter a name for the custom command.")
            return
        command = self.command_manager.give_command.get()
        if not command:
            messagebox.showwarning(self.localization["Warning"], "There is no command to save.")
            return

        # Save or overwrite the custom command
        self.custom_commands_dict[name] = command
        self.save_custom_commands()
        self.update_custom_commands_listbox()
        messagebox.showinfo("Info", f"Custom command '{name}' saved.")

    def load_custom_command(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning(self.localization["Warning"], "Please enter the name of the custom command to load.")
            return
        command = self.custom_commands_dict.get(name)
        if command:
            self.command_manager.update_command(command)
            messagebox.showinfo("Info", f"Custom command '{name}' loaded.")
        else:
            messagebox.showwarning(self.localization["Warning"], f"Custom command '{name}' not found.")

    def delete_custom_command(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning(self.localization["Warning"], "Please enter the name of the custom command to delete.")
            return
        if name in self.custom_commands_dict:
            del self.custom_commands_dict[name]
            self.save_custom_commands()
            self.update_custom_commands_listbox()
            self.command_manager.update_command('')
            self.name_var.set('')
            messagebox.showinfo("Info", f"Custom command '{name}' deleted.")
        else:
            messagebox.showwarning(self.localization["Warning"], f"Custom command '{name}' not found.")
