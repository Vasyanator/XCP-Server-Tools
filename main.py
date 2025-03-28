# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import sys

from process_handbook import process_handbook, identify_handbook
from settings import SettingsWindow, get_path # Import the SettingsWindow class

program_name = "HSR server Tools"
program_version = "1.3"
settings_file = 'settings.json'

def load_settings():
    # Load settings from settings.json
    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}
    return settings

def load_localization(language_code):
    # Load localization based on language_code

    # locales_dir = 'locales'
    locales_dir = get_path()

    lang = language_code if language_code else 'en'

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

    merged_localization = merge_localizations(default_localization, localization)
    return merged_localization

def create_tabs(notebook, command_manager, server_type, data, localization, settings, settings_file):
    main_locale = localization['main']
    tabs = []

    if server_type == 'LunarCore':
        # Import necessary modules
        import tab_planars_gen.main as tab_planars_gen
        #import tab_prepared_relics
        import tab_items
        import tab_spawn
        import tab_mazes_LC
        import tab_avatars_LC
        import tab_commands_LC
        import tab_opencommand
        import tab_server

        # Unpack data
        avatars_list = data['avatars_list']
        relics_list = data['relics_list']
        props_list = data['props_list']
        npc_monsters_list = data['npc_monsters_list']
        battle_stages = data['battle_stages']
        battle_monsters_list = data['battle_monsters_list']
        mazes_list = data['mazes_list']
        lightcones_list = data['lightcones_list']
        materials_list = data['materials_list']
        base_materials_list = data['base_materials_list']
        unknown_items_list = data['unknown_items_list']
        other_items_list = data['other_items_list']

        # Create tabs
        # Relic Generation Tab
        planars_tab = tab_planars_gen.PlanarsTab(notebook, relics_list, command_manager, localization['planars_tab'], server_type)
        notebook.add(planars_tab.frame, text=main_locale['tab_relic_generation'])
        tabs.append(planars_tab)

        #Best Relics Tab
        # best_relics_tab = tab_prepared_relics.PreparedRelicsTab(
        #     notebook,
        #     avatars_list,
        #     relics_list,
        #     other_items_list,
        #     localization=localization.get('outfits_tab', {}),
        #     stats_localization=localization['planars_tab']['Stats']
        # )
        # notebook.add(best_relics_tab.frame, text=main_locale.get('tab_outfits', 'Outfits'))
        # tabs.append(best_relics_tab)

        # Items Tab
        items_tab = tab_items.ItemsTab(
            notebook,
            base_materials=base_materials_list,
            lightcones=lightcones_list,
            materials=materials_list,
            other_items=other_items_list,
            unknown_items=unknown_items_list,
            command_manager=command_manager,
            localization=localization['items_tab'],
            server_type=server_type
        )
        notebook.add(items_tab.frame, text=main_locale['tab_items'])
        tabs.append(items_tab)

        # Spawn Tab
        spawn_tab = tab_spawn.SpawnTab(
            notebook,
            props_list=props_list,
            npc_monsters_list=npc_monsters_list,
            battle_stages=battle_stages,
            battle_monsters_list=battle_monsters_list,
            command_manager=command_manager,
            localization=localization['spawn_tab'],
            # server_type=server_type
        )
        notebook.add(spawn_tab.frame, text=main_locale['tab_spawn'])
        tabs.append(spawn_tab)

        # Mazes Tab
        mazes_tab = tab_mazes_LC.MazesTab(notebook, mazes_list, command_manager, localization['mazes_tab'])
        notebook.add(mazes_tab.frame, text=main_locale['tab_mazes'])
        tabs.append(mazes_tab)

        # Avatars Tab
        avatars_tab = tab_avatars_LC.AvatarsTab(notebook, avatars_list, command_manager, localization['avatars_tab'])
        notebook.add(avatars_tab.frame, text=main_locale['tab_avatars'])
        tabs.append(avatars_tab)

        # Commands Tab
        commands_tab = tab_commands_LC.CommandsTab(notebook, command_manager=command_manager, localization=localization['commands_tab_LC'], server_type=server_type)
        notebook.add(commands_tab.frame, text=main_locale['tab_commands'])
        tabs.append(commands_tab)

        # OpenCommand Tab
        opencommand_tab = tab_opencommand.OpenCommandTab(notebook, localization=localization['opencommand_tab'])
        notebook.add(opencommand_tab.frame, text=main_locale['tab_opencommand_plugin'])
        tabs.append(opencommand_tab)

        # Server tab
        server_tab = tab_server.ServerTab(
            notebook, 
            command_manager, 
            localization['server_tab'], 
            server_type, 
            settings,          # Pass the current settings
            settings_file      # Pass the settings file path
        )
        notebook.add(server_tab.frame, text=main_locale['tab_server'])
        tabs.append(server_tab)

    elif server_type == 'DanhengServer':
        # Import necessary modules
        import tab_planars_gen.main as tab_planars_gen
        # import tab_prepared_relics
        import tab_items
        import tab_avatars_DH
        import tab_rogue_buffs.main as rogue_buffs_main
        import tab_opencommand
        import tab_command_DH
        import tab_banner_editor
        # import tab_server

        # Unpack data
        avatars_list = data['avatars_list']
        relics_list = data['relics_list']
        lightcones_list = data['lightcones_list']
        materials_list = data['materials_list']
        base_materials_list = data['base_materials_list']
        unknown_items_list = data['unknown_items_list']
        other_items_list = data['other_items_list']
        rogue_buffs_su = data['rogue_buffs_su']
        rogue_buffs_food = data['rogue_buffs_food']
        rogue_buffs_various = data['rogue_buffs_various']
        rogue_buffs_from_entities = data['rogue_buffs_from_entities']
        rogue_buffs_other = data['rogue_buffs_other']
        rogue_buffs_unknown = data['rogue_buffs_unknown']
        rogue_miracles = data['rogue_miracles']

        # Create tabs
        # Relic Generation Tab
        planars_tab = tab_planars_gen.PlanarsTab(notebook, relics_list, command_manager, localization['planars_tab'], server_type)
        notebook.add(planars_tab.frame, text=main_locale['tab_relic_generation'])
        tabs.append(planars_tab)

        #Best Relics Tab
        # best_relics_tab = tab_prepared_relics.PreparedRelicsTab(
        #     notebook,
        #     avatars_list,
        #     relics_list,
        #     other_items_list,
        #     localization=localization.get('outfits_tab', {}),
        #     stats_localization=localization['planars_tab']['Stats']
        # )
        # notebook.add(best_relics_tab.frame, text=main_locale.get('tab_outfits', 'Outfits'))
        # tabs.append(best_relics_tab)

        # print(localization['planars_tab']['Stats'])

        # Items Tab
        items_tab = tab_items.ItemsTab(
            notebook,
            base_materials=base_materials_list,
            lightcones=lightcones_list,
            materials=materials_list,
            other_items=other_items_list,
            unknown_items=unknown_items_list,
            command_manager=command_manager,
            localization=localization['items_tab'],
            server_type=server_type
        )
        notebook.add(items_tab.frame, text=main_locale['tab_items'])
        tabs.append(items_tab)

        # Rogue Buffs Tab
        rogue_tab = rogue_buffs_main.RogueBuffsTab(
            notebook,
            rogue_buffs_su=rogue_buffs_su,
            rogue_buffs_food=rogue_buffs_food,
            rogue_buffs_various=rogue_buffs_various,
            rogue_buffs_from_entities=rogue_buffs_from_entities,
            rogue_buffs_other=rogue_buffs_other,
            rogue_buffs_unknown=rogue_buffs_unknown,
            rogue_miracles=rogue_miracles,
            command_manager=command_manager,
            localization=localization['rogue_buffs_tab'],
            # server_type=server_type
        )
        notebook.add(rogue_tab.frame, text=main_locale['tab_rogue'])
        tabs.append(rogue_tab)

        # Avatars Tab
        avatars_tab = tab_avatars_DH.AvatarsTab(notebook, avatars_list, command_manager, localization['avatars_tab'])
        notebook.add(avatars_tab.frame, text=main_locale['tab_avatars'])
        tabs.append(avatars_tab)

        command_tab = tab_command_DH.CommandTab(notebook, command_manager, localization['command_tab_DH'], server_type)
        # Здесь можно использовать, например, ключ 'tab_command' из локализации, если он есть,
        # либо задать текст напрямую
        notebook.add(command_tab.frame, text=main_locale.get('tab_commands', "Commands"))
        tabs.append(command_tab)

        banner_editor_tab = tab_banner_editor.BannerEditorTab(notebook, lightcones_list, avatars_list, localization['banner_editor'])
        notebook.add(banner_editor_tab.frame, text=main_locale.get('tab_banner_editor', "Редактор баннеров"))
        tabs.append(banner_editor_tab)

        # OpenCommand Tab
        opencommand_tab = tab_opencommand.OpenCommandTab(notebook, localization=localization['opencommand_tab'])
        notebook.add(opencommand_tab.frame, text=main_locale['tab_opencommand_plugin'])
        tabs.append(opencommand_tab)

        # Server tab (if applicable for DanhengServer)
        # server_tab = tab_server.ServerTab(
        #     notebook, 
        #     command_manager, 
        #     localization['server_tab'], 
        #     server_type, 
        #     settings,          # Pass the current settings
        #     settings_file      # Pass the settings file path
        # )
        # notebook.add(server_tab.frame, text=main_locale['tab_server'])
        # tabs.append(server_tab)


    return tabs

def main():
    # Load settings
    settings = load_settings()
    language_code = settings.get('language')
    localization = load_localization(language_code)
    main_locale = localization['main']

    # Check if settings are valid
    selected_handbook = settings.get('selected_handbook', '')
    if not selected_handbook or not os.path.exists(selected_handbook):
        # Open settings window without displaying root window
        root = tk.Tk()
        root.withdraw()
        settings_window = SettingsWindow(root, settings_file=settings_file)
        root.wait_window(settings_window.window)
        root.destroy()
        # After settings are saved, reload settings and localization
        settings = load_settings()
        language_code = settings.get('language')
        localization = load_localization(language_code)
        main_locale = localization['main']

    # Now check if selected_handbook is valid
    selected_handbook = settings.get('selected_handbook', '')
    if not selected_handbook or not os.path.exists(selected_handbook):
        # Still no valid Handbook, exit
        messagebox.showerror(main_locale.get('no_handbook_title', 'No Handbook'),
                             main_locale.get('no_handbook_message', 'No valid Handbook selected. Exiting.'))
        return

    # Now create the root window
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

class Application:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.settings_file = settings_file
        self.initialize_app()

    def initialize_app(self):
        self.load_settings()
        self.load_localization()

        self.create_widgets()

    def load_settings(self):
        self.settings = load_settings()
        self.language_code = self.settings.get('language')

    def load_localization(self):
        self.localization = load_localization(self.language_code)
        self.main_locale = self.localization['main']

    def create_widgets(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Set the window title
        selected_handbook = self.settings.get('selected_handbook', '')
        if not selected_handbook or not os.path.exists(selected_handbook):
            # No valid Handbook selected, open settings
            self.open_settings()
            return

        server_type, handbook_version = identify_handbook(selected_handbook)
        if not server_type:
            # Invalid Handbook selected
            messagebox.showerror(self.main_locale.get('invalid_handbook_title', 'Invalid Handbook'),
                                 self.main_locale.get('invalid_handbook_message', 'The selected Handbook is invalid. Please select a valid Handbook in settings.'))
            self.open_settings()
            return

        self.server_type = server_type
        self.handbook_version = handbook_version
        self.selected_handbook = selected_handbook

        self.root.title(self.main_locale['window_title'].format(
            program_name=program_name,
            program_version=program_version,
            server_type=self.server_type,
            handbook_version=self.handbook_version
        ))

        self.root.state('zoomed')

        # Menu bar with Settings button
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.main_locale['settings_menu'], menu=settings_menu)
        settings_menu.add_command(label=self.main_locale['settings_button'], command=self.open_settings)

        # Initialize shared variables
        self.give_command = tk.StringVar()
        self.autocopy_var = tk.BooleanVar()
        self.autocopy_var.set(True)

        # Create the notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create a CommandManager or similar to handle command updates
        self.command_manager = CommandManager(self.root, self.give_command, self.autocopy_var, self.main_locale)

        # Process the file
        handbook_data = process_handbook(self.selected_handbook, self.server_type, program_version)
        # Extract data
        data = handbook_data.get_data()

        # Create and add tabs based on server_type
        self.tabs = create_tabs(
            self.notebook, 
            self.command_manager, 
            self.server_type, 
            data, 
            self.localization, 
            self.settings,
            self.settings_file
        )


        # Get the server tab instance (always the last tab)
        server_tab = self.tabs[-1]
        # Pass the server_tab reference to the command manager
        self.command_manager.set_server_tab(server_tab)

        # Command Entry and copy button
        command_frame = tk.Frame(self.root)
        command_frame.pack(side=tk.BOTTOM, pady=10)

        command_entry = tk.Entry(command_frame, textvariable=self.give_command, font=('Arial', 12), width=50)
        command_entry.pack()

        # Autocopy checkbox
        autocopy_check = tk.Checkbutton(command_frame, text=self.main_locale['autocopy_label'], variable=self.autocopy_var)
        autocopy_check.pack()

        # Copy button
        copy_button = tk.Button(command_frame, text=self.main_locale['copy_button_label'], command=self.command_manager.copy_to_clipboard)
        copy_button.pack()

         # After creating and adding the Copy button:
        self.execute_button = tk.Button(command_frame, text=self.main_locale['execute_button_label'], command=self.execute_command, state=tk.DISABLED)
        self.execute_button.pack()
        self.command_manager.set_execute_button(self.execute_button)

        # Bind F5 key to execute command
        self.root.bind('<F5>', lambda event: self.execute_command())

    def open_settings(self):
        self.root.withdraw()  # Hide the main window
        settings_window = SettingsWindow(self.root, settings_file=self.settings_file)
        self.root.wait_window(settings_window.window)
        self.root.deiconify()  # Show the main window again
        # After settings are changed, reinitialize the application
        self.initialize_app()

    def on_settings_saved(self):
        # This method is called when settings are saved
        # Reload settings and reinitialize the application
        self.initialize_app()

    def execute_command(self):
        self.command_manager.execute_command()

    def on_close(self):
        # Assuming self.tabs were created and the last one is the server tab
        if hasattr(self, 'tabs') and self.tabs:
            if self.server_type == "LunarCore":
                server_tab = self.tabs[-1]
                if server_tab.running:
                    server_tab.stop_server()
        self.root.quit()

class CommandManager:
    def __init__(self, root, give_command_var, autocopy_var, localization):
        self.root = root
        self.give_command = give_command_var
        self.autocopy_var = autocopy_var
        self.localization = localization
        self.server_tab = None
        self.execute_button = None  # Will be set by Application after button creation

    def set_server_tab(self, server_tab):
        self.server_tab = server_tab
        # The Application sets this after the execute button is created
        # We'll need a reference to that button too.
        # We'll do that by searching for the Application’s execute_button dynamically:
        # (Alternatively, the Application can call a setter on CommandManager after button creation.)
        app = self.root  # Tk root is the parent of Application
        # Assuming the Application stored execute_button in self.execute_button:
        for child in app.winfo_children():
            # Searching for the command_frame to find execute_button is complicated,
            # Instead, let’s assume Application calls self.command_manager.execute_button = self.execute_button after creation
            pass

    def set_execute_button(self, button):
        self.execute_button = button

    def execute_command(self):
        if not self.server_tab or not self.server_tab.running:
            return
        cmd = self.give_command.get().strip()
        if not cmd:
            return
        # Remove leading '/'
        if cmd.startswith('/'):
            cmd = cmd[1:]
        # Add "@<uid>" after first word
        parts = cmd.split(' ', 1)
        uid = self.server_tab.uid_var.get().strip()
        if uid:
            if len(parts) > 1:
                modified_cmd = parts[0] + ' @' + uid + ' ' + parts[1]
            else:
                modified_cmd = parts[0] + ' @' + uid
        else:
            # If no UID provided, just use the original cmd (without '/')
            modified_cmd = cmd

        self.server_tab.send_command_to_server(modified_cmd)

    def set_server_state(self, running):
        if self.execute_button:
            self.execute_button.config(state=tk.NORMAL if running else tk.DISABLED)

    def update_command(self, command):
        self.give_command.set(command)
        if self.autocopy_var.get():
            self.copy_to_clipboard()

    def copy_to_clipboard(self):
        command = self.give_command.get()
        if command:
            self.root.clipboard_clear()
            self.root.clipboard_append(command)
            self.root.update()  # Now it stays on the clipboard after the window is closed
            if not self.autocopy_var.get():
                messagebox.showinfo(self.localization['copied_title'], self.localization['command_copied_message'])
        else:
            if not self.autocopy_var.get():
                messagebox.showwarning(self.localization['no_command_title'], self.localization['no_command_message'])

if __name__ == '__main__':
    main()
