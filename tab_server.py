import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import queue
import os
import json

class ServerTab:
    def __init__(self, parent, command_manager, localization, server_type, settings, settings_file):
        # Ensure settings is a dictionary
        self.settings = settings if isinstance(settings, dict) else {}
        self.settings_file = settings_file
        self.command_manager = command_manager
        self.localization = localization
        self.server_type = server_type

        self.frame = ttk.Frame(parent)
        self.process = None
        self.output_queue = queue.Queue()
        self.running = False

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Configuration frame for selecting server and java paths
        config_frame = ttk.LabelFrame(self.frame, text=self.localization.get('config_frame_label', 'Configuration'))
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Server path row
        server_path_label = ttk.Label(config_frame, text=self.localization.get('server_path_label', 'Server Path:'))
        server_path_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.server_path_var = tk.StringVar(value=self.get_server_path())
        server_path_entry = ttk.Entry(config_frame, textvariable=self.server_path_var, width=50)
        server_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        server_path_browse = ttk.Button(config_frame, text=self.localization.get('browse_button_label', 'Browse'), command=self.browse_server_executable)
        server_path_browse.grid(row=0, column=2, padx=5, pady=5)

        # UID row
        uid_label = ttk.Label(config_frame, text=self.localization.get('uid_label', 'UID:'))
        uid_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.uid_var = tk.StringVar(value="")
        uid_entry = ttk.Entry(config_frame, textvariable=self.uid_var, width=20)
        uid_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Java path row (only for LunarCore)
        if self.server_type == 'LunarCore':
            java_path_label = ttk.Label(config_frame, text=self.localization.get('java_path_label', 'Java Path:'))
            java_path_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            self.java_path_var = tk.StringVar(value=self.settings.get('java_path', 'java'))
            java_path_entry = ttk.Entry(config_frame, textvariable=self.java_path_var, width=50)
            java_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            java_path_browse = ttk.Button(config_frame, text=self.localization.get('browse_button_label', 'Browse'), command=self.browse_java_executable)
            java_path_browse.grid(row=1, column=2, padx=5, pady=5)

        # Control frame for start/stop/cleanup buttons
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.start_button = ttk.Button(
            control_frame,
            text=self.localization.get('start_server_button', 'Start Server'),
            command=self.start_server
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            control_frame,
            text=self.localization.get('stop_server_button', 'Stop Server'),
            command=self.stop_server,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.cleanup_button = ttk.Button(
            control_frame,
            text=self.localization.get('cleanup_button_label', 'Cleanup'),
            command=self.cleanup_console
        )
        self.cleanup_button.pack(side=tk.LEFT, padx=5)

        # Server output display
        self.output_display = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, state='disabled', height=20)
        self.output_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Input frame at the bottom
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_entry.bind('<Return>', self.send_command)  # Press Enter to send command

        self.send_button = ttk.Button(
            input_frame,
            text=self.localization.get('send_command_button', 'Send'),
            command=self.send_command
        )
        self.send_button.pack(side=tk.LEFT, padx=5)

    def send_command_to_server(self, cmd):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(cmd + "\n")
                self.process.stdin.flush()
            except Exception as e:
                messagebox.showerror(
                    self.localization.get('command_send_error_title', 'Command Send Error'),
                    self.localization.get('command_send_error_message', 'Failed to send command: {error}').format(error=str(e))
                )
        else:
            messagebox.showwarning(
                self.localization.get('server_not_running_title', 'Server Not Running'),
                self.localization.get('server_not_running_message', 'The server is not running.')
            )

    def get_server_path(self):
        if self.server_type == 'LunarCore':
            return self.settings.get('lunarcore_server_path', '')
        else:
            return self.settings.get('danheng_server_path', '')

    def browse_server_executable(self):
        # Different default file types based on server type
        if self.server_type == 'LunarCore':
            filetypes = [
                (self.localization.get('jar_file_type', 'JAR Files'), '*.jar'),
                (self.localization.get('all_files', 'All Files'), '*.*')
            ]
        else:
            filetypes = [
                (self.localization.get('exe_file_type', 'Executable Files'), '*.exe'),
                (self.localization.get('all_files', 'All Files'), '*.*')
            ]

        path = filedialog.askopenfilename(
            title=self.localization.get('browse_server_title', 'Select Server Executable'),
            filetypes=filetypes
        )
        if path:
            self.server_path_var.set(path)
            if self.server_type == 'LunarCore':
                key = 'lunarcore_server_path'
            else:
                key = 'danheng_server_path'
            self.update_settings(key, path)

    def browse_java_executable(self):
        path = filedialog.askopenfilename(
            title=self.localization.get('browse_java_title', 'Select Java Executable'),
            filetypes=[
                (self.localization.get('exe_file_type', 'Executable Files'), '*.exe'),
                (self.localization.get('all_files', 'All Files'), '*.*')
            ]
        )
        if path:
            self.java_path_var.set(path)
            self.update_settings('java_path', path)

    def update_settings(self, key, value):
        # Load the entire settings file, update the key, and then save
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
            else:
                all_settings = {}

            all_settings[key] = value

            # Update the in-memory settings as well
            self.settings[key] = value

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=4)
        except Exception as e:
            messagebox.showerror(
                self.localization.get('settings_save_error_title', 'Settings Save Error'),
                self.localization.get('settings_save_error_message', 'Error saving settings: {error}').format(error=str(e))
            )

    def start_server(self):
        if self.process is not None and self.process.poll() is None:
            messagebox.showinfo(
                self.localization.get('server_already_running_title', 'Server Already Running'),
                self.localization.get('server_already_running_message', 'The server is already running.')
            )
            return

        # Determine server command
        server_path = self.get_server_path()
        if not server_path or not os.path.exists(server_path):
            messagebox.showerror(
                self.localization.get('no_server_path_title', 'No Server Path'),
                self.localization.get('no_server_path_message', 'Please select a valid server executable.')
            )
            return

        # Determine the server's root directory
        server_dir = os.path.dirname(server_path)

        if self.server_type == 'LunarCore':
            java_path = self.settings.get('java_path', 'java')
            cmd = [java_path, '-jar', server_path]
        elif self.server_type == 'DanhengServer':
            cmd = [server_path]
        else:
            messagebox.showerror(
                self.localization.get('unknown_server_type_title', 'Unknown Server Type'),
                self.localization.get('unknown_server_type_message', 'Unknown server type: {server_type}').format(server_type=self.server_type)
            )
            return

        # Start the subprocess with the specified working directory
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=server_dir,  # Set the working directory to the server's root directory
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
        except Exception as e:
            messagebox.showerror(
                self.localization.get('server_start_error_title', 'Server Start Error'),
                self.localization.get('server_start_error_message', 'Failed to start the server: {error}').format(error=str(e))
            )
            return

        self.running = True
        self.command_manager.autocopy_var.set(False)
        self.command_manager.set_server_state(True)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start threads to read output
        threading.Thread(target=self.read_stdout, daemon=True).start()
        threading.Thread(target=self.read_stderr, daemon=True).start()

        # Start updating the UI
        self.update_output()


    def stop_server(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.running = False
        self.command_manager.set_server_state(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def send_command(self, event=None):
        cmd = self.input_var.get().strip()
        if not cmd:
            return
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(cmd + "\n")
                self.process.stdin.flush()
            except Exception as e:
                messagebox.showerror(
                    self.localization.get('command_send_error_title', 'Command Send Error'),
                    self.localization.get('command_send_error_message', 'Failed to send command: {error}').format(error=str(e))
                )
        else:
            messagebox.showwarning(
                self.localization.get('server_not_running_title', 'Server Not Running'),
                self.localization.get('server_not_running_message', 'The server is not running.')
            )
        self.input_var.set('')

    def cleanup_console(self):
        self.output_display.config(state='normal')
        self.output_display.delete('1.0', tk.END)
        self.output_display.config(state='disabled')

    def read_stdout(self):
        for line in iter(self.process.stdout.readline, ''):
            if line:
                self.output_queue.put(line)
        self.running = False

    def read_stderr(self):
        for line in iter(self.process.stderr.readline, ''):
            if line:
                self.output_queue.put(line)
        self.running = False

    def update_output(self):
        # Periodically check the queue for new output
        while True:
            try:
                line = self.output_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self.append_output(line)

        if self.running:
            self.frame.after(100, self.update_output)  # Check again in 100ms

    def append_output(self, text):
        self.output_display.config(state='normal')
        self.output_display.insert(tk.END, text)
        self.output_display.see(tk.END)
        self.output_display.config(state='disabled')
