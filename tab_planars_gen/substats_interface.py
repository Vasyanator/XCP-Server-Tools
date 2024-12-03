import tkinter as tk
from tkinter import ttk, messagebox

class SubstatsInterface:
    def __init__(self, parent_frame, localization, server_type, command_manager, localized_substats, localized_substats_levels, additional_stats, update_command_callback, get_main_stat_callback):
        self.parent_frame = parent_frame
        self.localization = localization
        self.server_type = server_type
        self.command_manager = command_manager
        self.localized_substats = localized_substats
        self.localized_substats_levels = localized_substats_levels  # Might be None for DanhengServer
        self.additional_stats = additional_stats  # Reference to PlanarsTab's additional_stats dictionary
        self.update_command_callback = update_command_callback  # Function to call to update the command in PlanarsTab
        self.get_main_stat_callback = get_main_stat_callback  # Function to get the current main stat

        # New: Dictionary to hold prioritized substats
        self.prioritized_stats = {}

        self.init_substats_interface()

    def init_substats_interface(self):
        # Create the main frame for substats interface
        substats_main_frame = tk.Frame(self.parent_frame)
        substats_main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for input fields and buttons
        input_frame = tk.Frame(substats_main_frame)
        input_frame.pack()

        # Additional stats section
        additional_label = tk.Label(input_frame, text=self.localization['Additional_stats:'])
        additional_label.grid(row=0, column=0, columnspan=4, pady=5)

        select_stat_label = tk.Label(input_frame, text=self.localization['Select_stat:'])
        select_stat_label.grid(row=1, column=0, sticky='e')
        self.additional_stats_var = tk.StringVar()
        self.additional_stats_var.set(next(iter(self.localized_substats)))
        additional_stats_menu = tk.OptionMenu(input_frame, self.additional_stats_var, *self.localized_substats.keys())
        additional_stats_menu.grid(row=1, column=1, sticky='w')

        quantity_label = tk.Label(input_frame, text=self.localization['Quantity:'])
        quantity_label.grid(row=1, column=2, sticky='e')
        self.additional_quantity_var = tk.StringVar(value='1')
        additional_quantity_entry = tk.Spinbox(input_frame, from_=1, to=15, textvariable=self.additional_quantity_var, width=5)
        additional_quantity_entry.grid(row=1, column=3, sticky='w')

        # Priority Spinbox
        priority_label = tk.Label(input_frame, text=self.localization.get('Priority:', 'Priority:'))
        priority_label.grid(row=2, column=0, sticky='e')
        self.priority_var = tk.IntVar(value=1)
        priority_spinbox = tk.Spinbox(input_frame, from_=1, to=10, textvariable=self.priority_var, width=5)
        priority_spinbox.grid(row=2, column=1, sticky='w')

        # Level selection for additional stats (LunarCore only)
        if self.server_type == 'LunarCore':
            self.level_label = tk.Label(input_frame, text=self.localization['Select_Value:'])
            self.level_label.grid(row=2, column=2, sticky='e')
            self.level_frame = tk.Frame(input_frame)
            self.level_frame.grid(row=2, column=3, sticky='w')
            self.additional_level_index_var = tk.IntVar(value=0)

            # Initialize additional_levels_var here
            self.additional_levels_var = tk.BooleanVar()
            self.additional_levels_var.set(True)
            levels_check = tk.Checkbutton(substats_main_frame, text=self.localization['Levels_of_additional_stats'],
                                          variable=self.additional_levels_var, command=self.on_additional_levels_toggle)
            levels_check.pack()

            self.additional_stats_var.trace('w', self.update_level_options)
            self.update_level_options()
        else:
            self.level_label = None
            self.level_frame = None

        # Buttons: Add, Update Selected, Add to Priority List
        buttons_frame = tk.Frame(substats_main_frame)
        buttons_frame.pack(pady=5)
        add_button = tk.Button(buttons_frame, text=self.localization['Add'], command=self.add_additional_stat)
        add_button.pack(side=tk.LEFT, padx=5)
        self.update_button = tk.Button(buttons_frame, text=self.localization['Update_Selected'], command=self.update_selected_stat, state='disabled')
        self.update_button.pack(side=tk.LEFT, padx=5)
        add_priority_button = tk.Button(buttons_frame, text=self.localization.get('Add_to_Priority_List', 'Add to Priority List'), command=self.add_to_priority_list)
        add_priority_button.pack(side=tk.LEFT, padx=5)

        # Improvement Points label
        self.improvement_points_label = tk.Label(substats_main_frame, text=self.localization['Improvement_points:'] + ' 0')
        self.improvement_points_label.pack()

        # Bottom frame to hold both lists side by side
        lists_frame = tk.Frame(substats_main_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True)

        # Current Additional Stats List
        current_stats_frame = tk.Frame(lists_frame)
        current_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        current_additional_label = tk.Label(current_stats_frame, text=self.localization['Current_additional_stats:'])
        current_additional_label.pack()
        self.additional_stats_listbox = tk.Listbox(current_stats_frame, width=30, height=10)
        self.additional_stats_listbox.pack()
        buttons_frame2 = tk.Frame(current_stats_frame)
        buttons_frame2.pack(pady=5)
        remove_button = tk.Button(buttons_frame2, text=self.localization['Remove_Selected'], command=self.remove_additional_stat)
        remove_button.pack(side=tk.LEFT, padx=5)
        clear_button = tk.Button(buttons_frame2, text=self.localization['Clear_All'], command=self.clear_additional_stats)
        clear_button.pack(side=tk.LEFT, padx=5)

        # Bind selection event for the listbox
        self.additional_stats_listbox.bind('<<ListboxSelect>>', self.on_stat_select)

        # Prioritized Stats Section
        priority_stats_frame = tk.Frame(lists_frame)
        priority_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        priority_label = tk.Label(priority_stats_frame, text=self.localization.get('Priority_List', 'Priority List:'))
        priority_label.pack()
        self.priority_listbox = tk.Listbox(priority_stats_frame, width=30, height=10)
        self.priority_listbox.pack()
        buttons_frame3 = tk.Frame(priority_stats_frame)
        buttons_frame3.pack(pady=5)
        remove_priority_button = tk.Button(buttons_frame3, text=self.localization['Remove_Selected'], command=self.remove_prioritized_stat)
        remove_priority_button.pack(side=tk.LEFT, padx=5)
        clear_priority_button = tk.Button(buttons_frame3, text=self.localization['Clear_All'], command=self.clear_prioritized_stats)
        clear_priority_button.pack(side=tk.LEFT, padx=5)

        # Match Substats Button
        match_button = tk.Button(priority_stats_frame, text=self.localization.get('Match_Substats', 'Match Substats'), command=self.match_substats)
        match_button.pack(pady=5)

        # Additional options (LunarCore only)
        if self.server_type == 'LunarCore':
            self.maxsteps_var = tk.BooleanVar()
            maxsteps_check = tk.Checkbutton(substats_main_frame, text=self.localization['Include_-maxsteps'], variable=self.maxsteps_var, command=self.update_command_callback)
            maxsteps_check.pack()
            #self.additional_levels_var = tk.BooleanVar()
            #self.additional_levels_var.set(True)
            #levels_check = tk.Checkbutton(self.parent_frame, text=self.localization['Levels_of_additional_stats'], variable=self.additional_levels_var, command=self.on_additional_levels_toggle)
            #levels_check.pack()


    def on_priority_stat_select(self, event):
        selected_indices = self.priority_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            stat_entry = self.priority_listbox.get(index)
            stat_name = stat_entry.split(' (Priority:')[0]
            data = self.prioritized_stats.get(stat_name, {})
            self.additional_stats_var.set(stat_name)
            self.priority_var.set(data.get('priority', 1))
            if self.server_type == 'LunarCore':
                level_index = data.get('level_index', 0)
                if level_index is not None:
                    self.additional_level_index_var.set(level_index)
            # Enable the Update Selected button
            self.update_button.config(state='normal')
            # Indicate that we're updating a priority stat
            self.is_updating_priority = True
        else:
            # Disable the Update Selected button
            self.update_button.config(state='disabled')
            self.is_updating_priority = False

    def update_level_options(self, *args):
        if self.server_type != 'LunarCore':
            return

        # Clear existing radiobuttons
        for widget in self.level_frame.winfo_children():
            widget.destroy()
        stat_name = self.additional_stats_var.get()
        if stat_name in self.localized_substats_levels:
            level_values = self.localized_substats_levels[stat_name]
            for i, value in enumerate(level_values):
                # Round value to one decimal
                display_value = round(value, 1)
                rb = tk.Radiobutton(self.level_frame, text=str(display_value), variable=self.additional_level_index_var, value=i)
                rb.pack(side=tk.LEFT)
            # Set default selection
            self.additional_level_index_var.set(0)
        else:
            # No levels available
            self.additional_level_index_var.set(0)
            rb = tk.Radiobutton(self.level_frame, text='N/A', variable=self.additional_level_index_var, value=0, state='disabled')
            rb.pack(side=tk.LEFT)
        # Disable level selection if /give is used
        if not self.additional_levels_var.get():
            for widget in self.level_frame.winfo_children():
                widget.config(state='disabled')

    def add_to_priority_list(self):
        stat_name = self.additional_stats_var.get()
        priority = self.priority_var.get()
        if not stat_name or not isinstance(priority, int):
            messagebox.showwarning('Invalid Input', 'Please select a valid stat and enter a priority.')
            return

        # For LunarCore, level might be important
        if self.server_type == 'LunarCore':
            if self.additional_levels_var.get():
                level_index = self.additional_level_index_var.get()
            else:
                level_index = None
            self.prioritized_stats[stat_name] = {'priority': priority, 'level_index': level_index}
        else:
            self.prioritized_stats[stat_name] = {'priority': priority}

        self.update_priority_listbox()

    def update_priority_listbox(self):
        self.priority_listbox.delete(0, tk.END)
        # Sort the stats based on priority (higher priority first)
        sorted_stats = sorted(self.prioritized_stats.items(), key=lambda x: -x[1]['priority'])
        for stat_name, data in sorted_stats:
            display_text = f"{stat_name} (Priority: {data['priority']})"
            if self.server_type == 'LunarCore' and data.get('level_index') is not None:
                level_value = self.localized_substats_levels[stat_name][data['level_index']]
                display_text += f" (Level: {round(level_value, 1)})"
            self.priority_listbox.insert(tk.END, display_text)

    def remove_prioritized_stat(self):
        selected_indices = self.priority_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            stat_entry = self.priority_listbox.get(index)
            stat_name = stat_entry.split(' (Priority:')[0]
            if stat_name in self.prioritized_stats:
                del self.prioritized_stats[stat_name]
            self.priority_listbox.delete(index)
        else:
            messagebox.showwarning('No Selection', 'Please select a stat to remove.')

    def get_improvement_points(self):
        # Calculate improvement points
        total_quantity = 0
        num_stats = len(self.additional_stats)
        if self.server_type == 'LunarCore':
            for qty, _ in self.additional_stats.values():
                total_quantity += qty
        elif self.server_type == 'DanhengServer':
            for qty in self.additional_stats.values():
                total_quantity += qty
        improvement_points = total_quantity - num_stats
        return improvement_points
    
    def update_improvement_points(self):
        improvement_points = self.get_improvement_points()
        self.improvement_points_label.config(text=self.localization['Improvement_points:'] + f' {improvement_points}')

    def match_substats(self):
        # Clear the current additional stats
        self.additional_stats.clear()

        # Get the main stat to avoid duplicates
        main_stat = self.get_main_stat_callback()

        # Sort the prioritized stats by priority
        sorted_stats = sorted(self.prioritized_stats.items(), key=lambda x: -x[1]['priority'])

        total_improvement_points = 0
        max_improvement_points = 5

        # Exclude the main stat and calculate total priority
        filtered_stats = [(stat_name, data) for stat_name, data in sorted_stats if stat_name != main_stat]

        # If no stats are left after filtering, do nothing
        if not filtered_stats:
            return

        assigned_points = {}
        # First pass: Assign proportional points
        total_priority = sum(data['priority'] for stat_name, data in filtered_stats)
        for stat_name, data in filtered_stats:
            proportion = data['priority'] / total_priority
            points = proportion * max_improvement_points
            assigned_points[stat_name] = points

        # Second pass: Round points and adjust to ensure total does not exceed max
        rounded_points = {}
        total_assigned = 0
        for stat_name, points in assigned_points.items():
            rounded_point = int(points)
            rounded_points[stat_name] = rounded_point
            total_assigned += rounded_point

        # Distribute remaining points starting from highest priority
        remaining_points = max_improvement_points - total_assigned
        for stat_name, data in filtered_stats:
            if remaining_points <= 0:
                break
            rounded_points[stat_name] += 1
            remaining_points -= 1

        # Assign quantities based on rounded points
        total_improvement_points = 0
        num_substats = 0
        for stat_name, data in filtered_stats:
            if num_substats >= 4:
                break

            points = rounded_points.get(stat_name, 0)
            if total_improvement_points >= max_improvement_points:
                points = 0  # No more improvement points available

            quantity = points + 1  # Quantity is points + 1 (since base is 1)

            if self.server_type == 'LunarCore':
                level_index = data.get('level_index')
                self.additional_stats[stat_name] = (quantity, level_index)
            else:
                self.additional_stats[stat_name] = quantity

            total_improvement_points += points
            num_substats += 1

        # If we have fewer than 4 substats, add more with quantity 1
        if num_substats < 4:
            for stat_name, data in filtered_stats:
                if num_substats >= 4:
                    break
                if stat_name in self.additional_stats:
                    continue  # Already added
                # Add with quantity 1
                if self.server_type == 'LunarCore':
                    level_index = data.get('level_index')
                    self.additional_stats[stat_name] = (1, level_index)
                else:
                    self.additional_stats[stat_name] = 1
                num_substats += 1

        # Update the substats listbox and improvement points
        self.update_additional_stats_listbox()
        self.update_improvement_points()
        self.update_command_callback()
    
    def clear_prioritized_stats(self):
        self.prioritized_stats.clear()
        self.priority_listbox.delete(0, tk.END)

    def on_additional_levels_toggle(self):
        if self.server_type != 'LunarCore':
            return

        if self.additional_levels_var.get():
            # Enable level selection
            for widget in self.level_frame.winfo_children():
                widget.config(state='normal')
        else:
            # Disable level selection
            for widget in self.level_frame.winfo_children():
                widget.config(state='disabled')
        self.update_command_callback()

    def add_additional_stat(self):
        stat_name = self.additional_stats_var.get()
        quantity = self.additional_quantity_var.get()
        if not stat_name or not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showwarning('Invalid Input', 'Please select a valid stat and enter a positive quantity.')
            return
        quantity = int(quantity)

        if self.server_type == 'LunarCore':
            if self.additional_levels_var.get():
                level_index = self.additional_level_index_var.get()
                if stat_name in self.localized_substats_levels and 0 <= level_index <= 2:
                    level_value = self.localized_substats_levels[stat_name][level_index]
                else:
                    messagebox.showwarning('Invalid Input', 'Please select a valid level value.')
                    return
            else:
                level_index = None
                level_value = None
            # Add to additional_stats dictionary
            self.additional_stats[stat_name] = (quantity, level_index)
        elif self.server_type == 'DanhengServer':
            if stat_name in self.additional_stats:
                # Update quantity if stat already exists
                self.additional_stats[stat_name] += quantity
            else:
                # Add new stat with quantity
                self.additional_stats[stat_name] = quantity

        self.update_additional_stats_listbox()
        self.update_improvement_points()
        self.update_command_callback()

    def update_additional_stats_listbox(self):
        self.additional_stats_listbox.delete(0, tk.END)
        for stat in self.additional_stats:
            if self.server_type == 'LunarCore':
                qty, lvl_idx = self.additional_stats[stat]
                if lvl_idx is not None:
                    lvl_value = self.localized_substats_levels[stat][lvl_idx]
                    total_val = qty * lvl_value
                    total_val = round(total_val, 1)
                    self.additional_stats_listbox.insert(tk.END, f'{stat} x{qty} ({total_val})')
                else:
                    self.additional_stats_listbox.insert(tk.END, f'{stat} x{qty}')
            elif self.server_type == 'DanhengServer':
                qty = self.additional_stats[stat]
                self.additional_stats_listbox.insert(tk.END, f'{stat} x{qty}')

    def remove_additional_stat(self):
        selected_indices = self.additional_stats_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            stat_entry = self.additional_stats_listbox.get(index)
            stat_name = stat_entry.split(' x')[0]
            if stat_name in self.additional_stats:
                del self.additional_stats[stat_name]
            self.additional_stats_listbox.delete(index)
            self.update_improvement_points()
            self.update_command_callback()
        else:
            messagebox.showwarning('No Selection', 'Please select a stat to remove.')

    def clear_additional_stats(self):
        self.additional_stats.clear()
        self.additional_stats_listbox.delete(0, tk.END)
        self.update_improvement_points()
        self.update_command_callback()

    def on_stat_select(self, event):
        selected_indices = self.additional_stats_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            stat_entry = self.additional_stats_listbox.get(index)
            stat_name = stat_entry.split(' x')[0]
            # Populate the selection widgets with the selected stat's data
            self.additional_stats_var.set(stat_name)
            if self.server_type == 'LunarCore':
                qty, lvl_idx = self.additional_stats[stat_name]
                self.additional_quantity_var.set(str(qty))
                if lvl_idx is not None:
                    self.additional_level_index_var.set(lvl_idx)
            elif self.server_type == 'DanhengServer':
                qty = self.additional_stats[stat_name]
                self.additional_quantity_var.set(str(qty))
            # Disable priority_var since it's not used for regular substats
            self.priority_var.set(1)
            # Enable the Update Selected button
            self.update_button.config(state='normal')
        else:
            # Disable the Update Selected button
            self.update_button.config(state='disabled')

    def update_selected_stat(self):
        if self.is_updating_priority:
            # Update the selected stat in the priority list
            selected_indices = self.priority_listbox.curselection()
            if selected_indices:
                index = selected_indices[0]
                stat_entry = self.priority_listbox.get(index)
                old_stat_name = stat_entry.split(' (Priority:')[0]

                new_stat_name = self.additional_stats_var.get()
                priority = self.priority_var.get()
                if not new_stat_name or not isinstance(priority, int):
                    messagebox.showwarning('Invalid Input', 'Please select a valid stat and enter a priority.')
                    return

                # For LunarCore, level might be important
                if self.server_type == 'LunarCore':
                    if self.additional_levels_var.get():
                        level_index = self.additional_level_index_var.get()
                    else:
                        level_index = None
                    # Update the prioritized_stats dictionary
                    del self.prioritized_stats[old_stat_name]
                    self.prioritized_stats[new_stat_name] = {'priority': priority, 'level_index': level_index}
                else:
                    del self.prioritized_stats[old_stat_name]
                    self.prioritized_stats[new_stat_name] = {'priority': priority}

                self.update_priority_listbox()
                # Reset updating flag
                self.is_updating_priority = False
                # Clear selection
                self.priority_listbox.selection_clear(0, tk.END)
        else:
            # Existing code for updating additional_stats
            self.update_selected_substat()

    def update_selected_substat(self):
        selected_indices = self.additional_stats_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            stat_entry = self.additional_stats_listbox.get(index)
            stat_name = stat_entry.split(' x')[0]
            # Update the additional_stats entry with the new values
            new_stat_name = self.additional_stats_var.get()
            quantity = self.additional_quantity_var.get()
            if not new_stat_name or not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showwarning('Invalid Input', 'Please select a valid stat and enter a positive quantity.')
                return
            quantity = int(quantity)

            if self.server_type == 'LunarCore':
                if self.additional_levels_var.get():
                    level_index = self.additional_level_index_var.get()
                    if new_stat_name in self.localized_substats_levels and 0 <= level_index <= 2:
                        level_value = self.localized_substats_levels[new_stat_name][level_index]
                    else:
                        messagebox.showwarning('Invalid Input', 'Please select a valid level value.')
                        return
                else:
                    level_index = None
                    level_value = None
                # Update the additional_stats dictionary
                del self.additional_stats[stat_name]
                self.additional_stats[new_stat_name] = (quantity, level_index)
            elif self.server_type == 'DanhengServer':
                del self.additional_stats[stat_name]
                self.additional_stats[new_stat_name] = quantity

            self.update_additional_stats_listbox()
            self.update_improvement_points()
            self.update_command_callback()
        else:
            messagebox.showwarning('No Selection', 'Please select a stat to update.')

    def update_improvement_points(self):
        # Calculate improvement points
        total_quantity = 0
        num_stats = len(self.additional_stats)
        if self.server_type == 'LunarCore':
            for qty, _ in self.additional_stats.values():
                total_quantity += qty
        elif self.server_type == 'DanhengServer':
            for qty in self.additional_stats.values():
                total_quantity += qty
        improvement_points = total_quantity - num_stats
        self.improvement_points_label.config(text=self.localization['Improvement_points:'] + f' {improvement_points}')

