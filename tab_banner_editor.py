import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
from datetime import datetime
import threading  # Для оптимизации загрузки файла

class BannerEditorTab:
    def __init__(self, parent, lightcones_list, avatars_list, localization):
        self.frame = tk.Frame(parent)
        self.lightcones_list = lightcones_list
        self.avatars_list = avatars_list
        self.localization = localization
        self.banners = []  # Список баннеров (список словарей)
        self.current_banner_index = None
        self.current_file = None
        self.create_widgets()

    def create_widgets(self):
        # Основной контейнер разбит на две части: слева – список баннеров, справа – панель редактирования.
        main_frame = self.frame

        # Левая панель: список баннеров
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.banner_listbox = tk.Listbox(left_frame, width=40)
        self.banner_listbox.pack(fill=tk.BOTH, expand=True)
        self.banner_listbox.bind("<<ListboxSelect>>", self.on_banner_select)
        banner_btn_frame = tk.Frame(left_frame)
        banner_btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(banner_btn_frame, text=self.localization['add_banner'], command=self.add_banner).pack(side=tk.LEFT, padx=2)
        tk.Button(banner_btn_frame, text=self.localization['delete_banner'], command=self.delete_banner).pack(side=tk.LEFT, padx=2)

        # Правая панель: редактор выбранного баннера
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Верхняя часть: параметры баннера ---
        param_frame = tk.Frame(right_frame)
        param_frame.pack(fill=tk.X, pady=5)
        # Тип баннера
        tk.Label(param_frame, text=self.localization['gacha_type']).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.gacha_type_var = tk.StringVar()
        self.gacha_type_cb = ttk.Combobox(param_frame, textvariable=self.gacha_type_var,
                                          values=["Normal", "Newbie", "WeaponUp", "AvatarUp"],
                                          state="readonly")
        self.gacha_type_cb.grid(row=0, column=1, pady=2)
        self.gacha_type_cb.bind("<<ComboboxSelected>>", self.on_gacha_type_change)
        # Номер баннера (последние 3 цифры)
        tk.Label(param_frame, text=self.localization['gacha_id']).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.gacha_id_var = tk.StringVar()
        self.gacha_id_entry = tk.Entry(param_frame, textvariable=self.gacha_id_var)
        self.gacha_id_entry.grid(row=1, column=1, pady=2)
        # Время начала и окончания (отображается в формате "YYYY-MM-DD HH:MM:SS")
        tk.Label(param_frame, text=self.localization['begin_time']).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.begin_time_var = tk.StringVar()
        self.begin_time_entry = tk.Entry(param_frame, textvariable=self.begin_time_var)
        self.begin_time_entry.grid(row=2, column=1, pady=2)
        tk.Label(param_frame, text=self.localization['end_time']).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.end_time_var = tk.StringVar()
        self.end_time_entry = tk.Entry(param_frame, textvariable=self.end_time_var)
        self.end_time_entry.grid(row=3, column=1, pady=2)

        # --- Средняя часть: текущие бонусы ---
        current_frame = tk.Frame(right_frame)
        current_frame.pack(fill=tk.X, pady=5)
        # Текущие элементы rateUpItems5
        rate5_frame = tk.Frame(current_frame)
        rate5_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(rate5_frame, text=self.localization['current_rate5']).pack(anchor=tk.W)
        self.current_rate5_lb = tk.Listbox(rate5_frame, height=5)
        self.current_rate5_lb.pack(fill=tk.BOTH, expand=True)
        # Текущие элементы rateUpItems4
        rate4_frame = tk.Frame(current_frame)
        rate4_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(rate4_frame, text=self.localization['current_rate4']).pack(anchor=tk.W)
        self.current_rate4_lb = tk.Listbox(rate4_frame, height=5)
        self.current_rate4_lb.pack(fill=tk.BOTH, expand=True)

        # --- Нижняя часть: выбор доступных элементов ---
        avail_frame = tk.Frame(right_frame)
        avail_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.available_notebook = ttk.Notebook(avail_frame)
        self.available_notebook.pack(fill=tk.BOTH, expand=True)
        # Вкладка "Available Lightcones"
        self.lightcones_tab = tk.Frame(self.available_notebook)
        self.available_notebook.add(self.lightcones_tab, text=self.localization['available_lightcones'])
        self.available_lightcones_lb = tk.Listbox(self.lightcones_tab)
        self.available_lightcones_lb.pack(fill=tk.BOTH, expand=True)
        for item in self.lightcones_list:
            if isinstance(item, dict):
                display = f"{item.get('id', '')}: {item.get('title', '')}"
            elif hasattr(item, 'id') and hasattr(item, 'title'):
                display = f"{item.id}: {item.title}"
            else:
                display = str(item)
            self.available_lightcones_lb.insert(tk.END, display)
        # Вкладка "Available Avatars"
        self.avatars_tab = tk.Frame(self.available_notebook)
        self.available_notebook.add(self.avatars_tab, text=self.localization['available_avatars'])
        self.available_avatars_lb = tk.Listbox(self.avatars_tab)
        self.available_avatars_lb.pack(fill=tk.BOTH, expand=True)
        for item in self.avatars_list:
            if isinstance(item, dict):
                display = f"{item.get('id', '')}: {item.get('name', '')}"
            else:
                display = str(item)
            self.available_avatars_lb.insert(tk.END, display)

        # --- Кнопки для добавления выбранного элемента в бонусный список ---
        add_btn_frame = tk.Frame(right_frame)
        add_btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(add_btn_frame, text=self.localization['add_to_rate5'], command=lambda: self.add_item_to_rate('5')).pack(side=tk.LEFT, padx=5)
        tk.Button(add_btn_frame, text=self.localization['add_to_rate4'], command=lambda: self.add_item_to_rate('4')).pack(side=tk.LEFT, padx=5)

        # --- Файл-операции и кнопка обновления баннера ---
        file_btn_frame = tk.Frame(right_frame)
        file_btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(file_btn_frame, text=self.localization['open_file'], command=self.open_file).pack(side=tk.LEFT, padx=5)
        tk.Button(file_btn_frame, text=self.localization['save_file'], command=self.save_file).pack(side=tk.LEFT, padx=5)
        tk.Button(file_btn_frame, text=self.localization['save_as'], command=self.save_as_file).pack(side=tk.LEFT, padx=5)
        tk.Button(file_btn_frame, text=self.localization['update_banner'], command=self.update_banner).pack(side=tk.RIGHT, padx=5)

    def format_unix_time(self, ts):
        try:
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""

    def parse_time_str(self, time_str):
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except Exception:
            return 0

    def on_banner_select(self, event):
        selection = self.banner_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_banner_index = index
            banner = self.banners[index]
            self.gacha_type_var.set(banner.get('gachaType', 'Normal'))
            gacha_id = str(banner.get('gachaId', ''))
            self.gacha_id_var.set(gacha_id[1:] if len(gacha_id) == 4 else gacha_id)
            self.begin_time_var.set(self.format_unix_time(banner.get('beginTime', 0)))
            self.end_time_var.set(self.format_unix_time(banner.get('endTime', 0)))
            self.refresh_current_rate_listboxes(banner)

    def refresh_current_rate_listboxes(self, banner):
        self.current_rate5_lb.delete(0, tk.END)
        for item in banner.get('rateUpItems5', []):
            self.current_rate5_lb.insert(tk.END, self.get_item_name(item))
        self.current_rate4_lb.delete(0, tk.END)
        for item in banner.get('rateUpItems4', []):
            self.current_rate4_lb.insert(tk.END, self.get_item_name(item))

    def add_banner(self):
        new_banner = {
            'gachaType': 'Normal',
            'gachaId': 1000,  # По умолчанию: префикс 1 + "000"
            'beginTime': 0,
            'endTime': 0,
            'rateUpItems5': [],
            'rateUpItems4': []
        }
        self.banners.append(new_banner)
        self.banner_listbox.insert(tk.END, self.format_banner_display(new_banner))
        self.banner_listbox.select_clear(0, tk.END)
        self.banner_listbox.select_set(tk.END)
        self.on_banner_select(None)

    def delete_banner(self):
        selection = self.banner_listbox.curselection()
        if selection:
            index = selection[0]
            del self.banners[index]
            self.banner_listbox.delete(index)
            self.clear_form()

    def update_banner(self):
        if self.current_banner_index is None:
            return
        banner = self.banners[self.current_banner_index]
        banner['gachaType'] = self.gacha_type_var.get()
        prefix = {'Normal': '1', 'Newbie': '4', 'WeaponUp': '3', 'AvatarUp': '2'}.get(banner['gachaType'], '1')
        last_three = self.gacha_id_var.get().zfill(3)[-3:]
        banner['gachaId'] = int(prefix + last_three)
        banner['beginTime'] = self.parse_time_str(self.begin_time_var.get())
        banner['endTime'] = self.parse_time_str(self.end_time_var.get())
        self.banner_listbox.delete(self.current_banner_index)
        self.banner_listbox.insert(self.current_banner_index, self.format_banner_display(banner))

    def on_gacha_type_change(self, event):
        # При смене типа можно реализовать дополнительные действия (например, сброс бонусов)
        pass

    def get_item_name(self, item):
        """
        Возвращает название элемента:
          - Если item является словарём, возвращает 'title' или 'name'
          - Если item – объект с атрибутами, пытается вернуть item.title или item.name
          - Если item – число или строка, выполняется поиск по lightcones_list (для id длиной 5)
            или avatars_list (для id длиной 4)
        """
        # Если item – словарь
        if isinstance(item, dict):
            if 'title' in item:
                return item.get('title', str(item.get('id', '')))
            if 'name' in item:
                return item.get('name', str(item.get('id', '')))
        # Если item – объект с атрибутами title или name
        if hasattr(item, 'title'):
            return item.title
        if hasattr(item, 'name'):
            return item.name

        # Рассматриваем item как id (число или строку)
        item_id_str = str(item)
        if len(item_id_str) == 5:  # Предполагаем, что это lightcone (оружие)
            for obj in self.lightcones_list:
                if isinstance(obj, dict) and str(obj.get('id', '')) == item_id_str:
                    return obj.get('title', item_id_str)
                elif hasattr(obj, 'id') and str(obj.id) == item_id_str and hasattr(obj, 'title'):
                    return obj.title
        elif len(item_id_str) == 4:  # Персонаж (avatar)
            for obj in self.avatars_list:
                if isinstance(obj, dict) and str(obj.get('id', '')) == item_id_str:
                    return obj.get('name', item_id_str)
                elif hasattr(obj, 'id') and str(obj.id) == item_id_str and hasattr(obj, 'name'):
                    return obj.name
        return item_id_str

    def format_banner_display(self, banner):
        banner_type = banner.get('gachaType', '')
        if banner_type in ['Normal', 'Newbie']:
            return banner_type
        elif banner_type == 'WeaponUp':
            items = banner.get('rateUpItems5', [])
            if items:
                # Для WeaponUp отображаем название первого бонусного элемента через get_item_name
                return f"{banner_type} - {self.get_item_name(items[0])}"
            else:
                return banner_type
        else:  # Для AvatarUp и других типов – отображаем тип и название первого бонусного элемента
            items = banner.get('rateUpItems5', [])
            first_item = self.get_item_name(items[0]) if items else self.localization.get('no_item', "No item")
            return f"{banner_type} - {first_item}"

    def add_item_to_rate(self, rate):
        # rate: '5' или '4'
        if self.current_banner_index is None:
            messagebox.showerror(self.localization['error_title'],
                                 self.localization.get('no_banner_selected', "No banner selected"))
            return
        # Определяем активную вкладку в Notebook
        active_tab = self.available_notebook.index("current")
        selected_item = None
        if active_tab == 0:  # вкладка Lightcones
            sel = self.available_lightcones_lb.curselection()
            if sel:
                index = sel[0]
                selected_item = self.lightcones_list[index]
        elif active_tab == 1:  # вкладка Avatars
            sel = self.available_avatars_lb.curselection()
            if sel:
                index = sel[0]
                selected_item = self.avatars_list[index]
        if not selected_item:
            messagebox.showerror(self.localization['error_title'],
                                 self.localization.get('no_item_selected', "No item selected"))
            return

        # Извлекаем id выбранного элемента, приводим к числу, если возможно
        if isinstance(selected_item, dict):
            raw_id = selected_item.get('id')
        elif hasattr(selected_item, 'id'):
            raw_id = selected_item.id
        else:
            raw_id = selected_item
        try:
            item_id = int(raw_id)
        except Exception:
            item_id = raw_id  # Если не число, оставляем как есть

        banner = self.banners[self.current_banner_index]
        if rate == '5':
            banner.setdefault('rateUpItems5', []).append(item_id)
        else:
            banner.setdefault('rateUpItems4', []).append(item_id)
        self.refresh_current_rate_listboxes(banner)
        self.banner_listbox.delete(self.current_banner_index)
        self.banner_listbox.insert(self.current_banner_index, self.format_banner_display(banner))

    def clear_form(self):
        self.gacha_type_var.set('')
        self.gacha_id_var.set('')
        self.begin_time_var.set('')
        self.end_time_var.set('')
        self.current_rate5_lb.delete(0, tk.END)
        self.current_rate4_lb.delete(0, tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(title=self.localization['open_file'],
                                               filetypes=[("JSON files", "*.json")])
        if file_path:
            # Запускаем загрузку файла в отдельном потоке для избежания зависания интерфейса
            threading.Thread(target=self.load_file, args=(file_path,), daemon=True).start()

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.banners = data.get('Banners', [])
            self.current_file = file_path
            # Обновляем список баннеров в главном потоке
            self.frame.after(0, self.refresh_banner_list)
        except Exception as e:
            self.frame.after(0, lambda: messagebox.showerror(self.localization['error_title'], str(e)))

    def save_file(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(title=self.localization['save_as'],
                                                 defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")])
        if file_path:
            self.current_file = file_path
            self._save_to_file(file_path)

    def _save_to_file(self, file_path):
        data = {"Banners": self.banners}
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo(self.localization['success_title'], self.localization['save_success'])
        except Exception as e:
            messagebox.showerror(self.localization['error_title'], str(e))

    def refresh_banner_list(self):
        self.banner_listbox.delete(0, tk.END)
        for banner in self.banners:
            self.banner_listbox.insert(tk.END, self.format_banner_display(banner))
