# settings.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import locale as pylocale
import sys

from process_handbook import identify_handbook  # Import the identify_handbook function

def get_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Если программа собрана в .exe
        base_path = sys._MEIPASS
    else:
        # Если запускается как скрипт
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "locales")

class SettingsWindow:
    def __init__(self, master, settings_file='settings.json'):
        self.master = master
        self.settings_file = settings_file
        self.load_settings()

        self.window = tk.Toplevel(self.master)
        self.window.title(self.localization.get('settings_title', 'Settings'))
        self.window.grab_set()  # Make the settings window modal

        self.create_widgets()

    def load_settings(self):
        # Load settings from settings.json
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            # Default settings
            self.settings = {
                'language': pylocale.getdefaultlocale()[0][:2] if pylocale.getdefaultlocale()[0] else 'en',
                'handbook_paths': [],
                'selected_handbook': ''
            }

        # Load localization for the settings window
        self.load_localization()

    def load_localization(self):
        # Load localization for the settings window based on selected language
        locales_dir = get_path()
        # locales_dir = 'locales'
        lang = self.settings.get('language', 'en')

        def load_json(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                return {}
            except json.JSONDecodeError as e:
                raise ValueError(f"Error reading file {file_path}: {e}")

        en_path = os.path.join(locales_dir, 'en.json')
        default_localization = load_json(en_path)
        lang_path = os.path.join(locales_dir, f'{lang}.json')
        localization = load_json(lang_path) if lang != 'en' else default_localization

        def merge_localizations(default, override):
            merged = default.copy()
            for key, value in override.items():
                if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                    merged[key] = merge_localizations(merged[key], value)
                else:
                    merged[key] = value
            return merged

        self.localization = merge_localizations(default_localization, localization).get('settings', {})

    def create_widgets(self):
        frame = ttk.Frame(self.window)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Language selection
        lang_label = ttk.Label(frame, text=self.localization.get('language_label', 'Select Language:'))
        lang_label.pack(anchor=tk.W)
        self.language_var = tk.StringVar(value=self.settings.get('language', 'en'))
        languages = self.get_available_languages()
        lang_menu = ttk.OptionMenu(frame, self.language_var, self.language_var.get(), *languages)
        lang_menu.pack(fill=tk.X)

        # Handbook selection
        handbook_label = ttk.Label(frame, text=self.localization.get('handbook_label', 'Select Handbook:'))
        handbook_label.pack(anchor=tk.W, pady=(10, 0))

        self.handbook_var = tk.StringVar()
        handbook_frame = ttk.Frame(frame)
        handbook_frame.pack(fill=tk.X)

        # Create a Combobox for Handbook selection
        self.handbook_combobox = ttk.Combobox(handbook_frame, textvariable=self.handbook_var, state='readonly')
        self.handbook_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bind the selection event
        self.handbook_combobox.bind('<<ComboboxSelected>>', self.on_handbook_selected)

        # Browse button to add new Handbook files
        browse_button = ttk.Button(handbook_frame, text=self.localization.get('browse_button', 'Browse'), command=self.browse_handbook)
        browse_button.pack(side=tk.LEFT, padx=(5, 0))

        # Handbook info label
        self.handbook_info_label = ttk.Label(frame, text='')
        self.handbook_info_label.pack(anchor=tk.W, pady=(5, 0))

        # Load available Handbooks
        self.update_handbook_list()

        # Display info for selected Handbook
        self.display_handbook_info(self.handbook_var.get())

        # Buttons
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=(10, 0))
        save_button = ttk.Button(buttons_frame, text=self.localization.get('save_button', 'Save'), command=self.save_settings)
        save_button.pack(side=tk.LEFT, padx=5)
        cancel_button = ttk.Button(buttons_frame, text=self.localization.get('cancel_button', 'Cancel'), command=self.window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def get_available_languages(self):
        # Get list of available language codes from the locales directory
        locales_dir = get_path()
        languages = []
        for file in os.listdir(locales_dir):
            if file.endswith('.json'):
                lang_code = file[:-5]
                languages.append(lang_code)
        return languages

    def update_handbook_list(self):
        # Get list of Handbook files in the root directory
        root_handbooks = []
        for file in os.listdir():
            if file.endswith('.txt'):
                full_path = os.path.abspath(file)
                server_type, handbook_version = identify_handbook(full_path)
                if server_type:
                    root_handbooks.append(full_path)

        # Combine with previously selected handbooks
        all_handbooks = set(root_handbooks + self.settings.get('handbook_paths', []))

        # Verify that the handbooks are valid
        valid_handbooks = []
        for path in all_handbooks:
            if os.path.exists(path):
                server_type, handbook_version = identify_handbook(path)
                if server_type:
                    valid_handbooks.append(path)

        # Update the settings with valid handbooks
        self.settings['handbook_paths'] = valid_handbooks

        # Update the Combobox values
        self.handbook_combobox['values'] = valid_handbooks

        # Set the selected Handbook
        selected_handbook = self.settings.get('selected_handbook', '')
        if selected_handbook in valid_handbooks:
            self.handbook_var.set(selected_handbook)
        elif valid_handbooks:
            self.handbook_var.set(valid_handbooks[0])
            self.settings['selected_handbook'] = valid_handbooks[0]
        else:
            self.handbook_var.set('')

    def on_handbook_selected(self, event):
        selected_handbook = self.handbook_var.get()
        self.display_handbook_info(selected_handbook)
        self.settings['selected_handbook'] = selected_handbook

    def display_handbook_info(self, handbook_path):
        if handbook_path and os.path.exists(handbook_path):
            server_type, handbook_version = identify_handbook(handbook_path)
            if server_type:
                info_text = f"Type: {server_type}, Version: {handbook_version}"
                self.handbook_info_label.config(text=info_text)
            else:
                self.handbook_info_label.config(text=self.localization.get('invalid_handbook_message', 'Invalid Handbook selected.'))
        else:
            self.handbook_info_label.config(text='')

    def browse_handbook(self):
        filename = filedialog.askopenfilename(
            title=self.localization.get('select_handbook_title', 'Select Handbook File'),
            filetypes=((self.localization.get('text_files', 'Text Files'), "*.txt"),
                       (self.localization.get('all_files', 'All Files'), "*.*"))
        )
        if filename:
            # Verify that it's a valid Handbook
            server_type, handbook_version = identify_handbook(filename)
            if server_type:
                # Add to the list if not already there
                if filename not in self.settings.get('handbook_paths', []):
                    self.settings.setdefault('handbook_paths', []).append(filename)
                self.update_handbook_list()
                self.handbook_var.set(filename)
                self.settings['selected_handbook'] = filename
                self.display_handbook_info(filename)
            else:
                # Show a warning that the selected file is not a valid Handbook
                messagebox.showwarning(self.localization.get('invalid_handbook_title', 'Invalid Handbook'),
                                       self.localization.get('invalid_handbook_message', 'The selected file is not a valid Handbook.'))

    def save_settings(self):
        # Update settings
        self.settings['language'] = self.language_var.get()
        selected_handbook = self.handbook_var.get()
        if selected_handbook and os.path.exists(selected_handbook):
            self.settings['selected_handbook'] = selected_handbook
        else:
            # Show a warning that a valid Handbook must be selected
            messagebox.showwarning(self.localization.get('warning_title', 'Warning'), self.localization.get('handbook_not_found', 'Please select a valid Handbook file.'))
            return

        # Save settings to settings.json
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

        # Close the settings window
        self.window.destroy()

        # Notify the main application to reinitialize
        if hasattr(self.master, 'on_settings_saved'):
            self.master.on_settings_saved()
