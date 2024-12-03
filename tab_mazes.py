# tab_mazes.py

import tkinter as tk
from tkinter import ttk
from tkinter import VERTICAL, RIGHT, LEFT, Y, StringVar

class MazesTab:
    def __init__(self, notebook, mazes_list, command_manager, localization):
        self.notebook = notebook
        self.mazes_list = mazes_list
        self.command_manager = command_manager
        self.localization = localization

        self.frame = ttk.Frame(notebook)
        self.init_tab()

    def init_tab(self):
        selected_maze_id = None
        search_var = StringVar()

        # Main frame
        main_frame = tk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search functionality
        search_label = tk.Label(main_frame, text=self.localization["Search"])
        search_label.pack()

        search_entry = tk.Entry(main_frame, textvariable=search_var)
        search_entry.pack()
        search_var.trace('w', lambda *args: update_maze_list())

        # Maze selection with scrollbar
        maze_frame = tk.Frame(main_frame)
        maze_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(maze_frame, orient=VERTICAL)
        maze_listbox = tk.Listbox(maze_frame, width=50, height=20, yscrollcommand=scrollbar.set, exportselection=False)
        scrollbar.config(command=maze_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        maze_listbox.pack(side=LEFT, fill=tk.BOTH, expand=True)

        # Bind selection event
        def on_maze_select(event):
            nonlocal selected_maze_id
            selected_indices = maze_listbox.curselection()
            if selected_indices:
                index = selected_indices[0]
                selected_maze = maze_listbox.get(index)
                if '(' in selected_maze and ')' in selected_maze:
                    id_str = selected_maze.split('(')[-1].split(')')[0]
                    selected_maze_id = id_str
                    # Update the command
                    update_command()
                else:
                    selected_maze_id = None
                    self.command_manager.update_command('')
            else:
                selected_maze_id = None
                self.command_manager.update_command('')

        maze_listbox.bind('<<ListboxSelect>>', on_maze_select)

        # Update maze list function
        def update_maze_list():
            search_text = search_var.get().lower()

            # Clear the listbox
            maze_listbox.delete(0, tk.END)

            # Populate the listbox
            for entry in self.mazes_list:
                display_text = f"{entry['name']} ({entry['id']})"
                if search_text in entry['name'].lower() or search_text in entry['id']:
                    maze_listbox.insert(tk.END, display_text)

            # Clear the command
            self.command_manager.update_command('')

        # Update command function
        def update_command():
            if not selected_maze_id:
                self.command_manager.update_command('')
                return

            command = f"/scene {selected_maze_id}"
            self.command_manager.update_command(command)

        # Initialize the maze list
        update_maze_list()
