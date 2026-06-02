import zlib, json, hashlib, os, shutil, tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

BASE_DIR = Path(os.environ.get('LOCALAPPDATA', '')) / 'StoneShard'
CHARACTERS_DIR = BASE_DIR / 'characters_v1'

class StoneshardEditor:
    def __init__(self, root):
        self.root = root
        self.root.title('Stoneshard Save Editor')
        self.root.geometry('820x680')
        self.root.resizable(False, False)

        self.current_save = None
        self.current_json = None
        self.orig_json = None
        self.char_folder = None
        self.save_folder = None

        self._build_ui()
        self._scan_saves()

    def _log(self, msg):
        self.status_var.set(msg)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(main)
        top.pack(fill=tk.X)
        ttk.Label(top, text='Персонаж:').pack(side=tk.LEFT)
        self.char_combo = ttk.Combobox(top, state='readonly', width=14)
        self.char_combo.pack(side=tk.LEFT, padx=4)
        self.char_combo.bind('<<ComboboxSelected>>', self._on_char_select)

        ttk.Label(top, text='Сейв:').pack(side=tk.LEFT, padx=(10,0))
        self.save_combo = ttk.Combobox(top, state='readonly', width=14)
        self.save_combo.pack(side=tk.LEFT, padx=4)
        self.save_combo.bind('<<ComboboxSelected>>', self._on_save_select)

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self._build_position_tab()
        self._build_stats_tab()
        self._build_bonus_tab()
        self._build_items_tab()
        self._build_buffs_tab()

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(6,0))
        ttk.Button(btn_frame, text='Сохранить', command=self._save).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text='Обновить данные', command=self._refresh_all).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text='Выход', command=self.root.destroy).pack(side=tk.RIGHT, padx=3)

        self.status_var = tk.StringVar(value='Готов')
        ttk.Label(main, textvariable=self.status_var, foreground='gray').pack(anchor='w', pady=(4,0))

    # ========== Position Tab ==========
    def _build_position_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text='Позиция')

        info_frame = ttk.LabelFrame(tab, text='Текущая позиция', padding=8)
        info_frame.pack(fill=tk.X)
        self.info_text = tk.Text(info_frame, height=6, state='disabled')
        self.info_text.pack(fill=tk.BOTH)

        edit_frame = ttk.LabelFrame(tab, text='Новая позиция', padding=8)
        edit_frame.pack(fill=tk.X, pady=(10,0))

        self.pos_entries = {}
        fields = [
            ('location', 'Локация:'),
            ('grid_x', 'Глобальная X (playerGridX):'),
            ('grid_y', 'Глобальная Y (playerGridY):'),
            ('local_x', 'Локальная X (localX):'),
            ('local_y', 'Локальная Y (localY):'),
        ]
        for i, (key, label) in enumerate(fields):
            ttk.Label(edit_frame, text=label).grid(row=i, column=0, sticky='w')
            ent = ttk.Entry(edit_frame, width=35)
            ent.grid(row=i, column=1, sticky='ew', padx=5)
            self.pos_entries[key] = ent
        edit_frame.columnconfigure(1, weight=1)

    # ========== Stats Tab ==========
    def _build_stats_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text='Характеристики')

        info_row = ttk.Frame(tab)
        info_row.pack(fill=tk.X)
        ttk.Label(info_row, text='Имя:').pack(side=tk.LEFT)
        self.st_name = ttk.Label(info_row, text='-')
        self.st_name.pack(side=tk.LEFT, padx=4)
        ttk.Label(info_row, text='Класс:').pack(side=tk.LEFT, padx=(15,0))
        self.st_class = ttk.Label(info_row, text='-')
        self.st_class.pack(side=tk.LEFT, padx=4)
        ttk.Label(info_row, text='Уровень:').pack(side=tk.LEFT, padx=(15,0))
        self.st_lvl = ttk.Label(info_row, text='-')
        self.st_lvl.pack(side=tk.LEFT, padx=4)

        stats_frame = ttk.LabelFrame(tab, text='Характеристики', padding=8)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        self.stat_entries = {}
        stat_fields = [
            ('STR', 'STR (Сила)'),
            ('AGL', 'AGL (Ловкость)'),
            ('PRC', 'PRC (Восприятие)'),
            ('Vitality', 'Vitality (Телосложение)'),
            ('WIL', 'WIL (Сила воли)'),
        ]
        for i, (key, label) in enumerate(stat_fields):
            ttk.Label(stats_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            ent = ttk.Entry(stats_frame, width=12)
            ent.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            self.stat_entries[key] = ent

        ttk.Separator(stats_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky='ew', pady=6)

        other_fields = [
            ('HP', 'HP'),
            ('MP', 'MP'),
            ('XP', 'XP'),
            ('SP', 'SP (Очки навыков)'),
            ('AP', 'AP (Очки статов)'),
        ]
        for i, (key, label) in enumerate(other_fields, start=6):
            ttk.Label(stats_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            ent = ttk.Entry(stats_frame, width=12)
            ent.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            self.stat_entries[key] = ent

    # ========== Bonus Stats Tab ==========
    def _build_bonus_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text='Бонусы')

        frame = ttk.LabelFrame(tab, text='Бонусные характеристики', padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        self.bonus_entries = {}
        bonus_fields = [
            ('bCRT', 'bCRT (крит. шанс)'),
            ('bCRTD', 'bCRTD (крит. урон)'),
            ('bEVS', 'bEVS (уклонение)'),
            ('bHp', 'bHp (HP)'),
            ('bMp', 'bMp (MP)'),
            ('bmax_hp', 'bmax_hp (макс. HP)'),
            ('bMP_Restoration', 'bMP_Restoration (восст. MP)'),
            ('bSavvy', 'bSavvy (смекалка)'),
            ('bVSN', 'bVSN (восприятие)'),
            ('bFMB', 'bFMB (физ.мощь)'),
        ]
        for i, (key, label) in enumerate(bonus_fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            ent = ttk.Entry(frame, width=12)
            ent.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            self.bonus_entries[key] = ent

    # ========== Items Tab ==========
    def _build_items_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text='Предметы')

        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: item list
        left_frame = ttk.LabelFrame(paned, text='Предметы', padding=4)
        self.items_tree = ttk.Treeview(left_frame, columns=('slot',), show='tree',
                                        selectmode='browse', height=20)
        self.items_tree.heading('#0', text='Название')
        self.items_tree.column('#0', width=220)
        self.items_tree.heading('slot', text='Слот')
        self.items_tree.column('slot', width=100)
        scroll_items = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scroll_items.set)
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_items.pack(side=tk.RIGHT, fill=tk.Y)
        self.items_tree.bind('<<TreeviewSelect>>', self._on_item_select)
        paned.add(left_frame, weight=1)

        # Right: item properties as tree
        right_frame = ttk.LabelFrame(paned, text='Свойства предмета', padding=4)
        self.prop_tree = ttk.Treeview(right_frame, columns=('value',), show='tree', height=20)
        self.prop_tree.heading('#0', text='Свойство')
        self.prop_tree.column('#0', width=250)
        self.prop_tree.heading('value', text='Значение')
        self.prop_tree.column('value', width=150)
        scroll_prop = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.prop_tree.yview)
        self.prop_tree.configure(yscrollcommand=scroll_prop.set)
        self.prop_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_prop.pack(side=tk.RIGHT, fill=tk.Y)
        self.prop_tree.bind('<Double-1>', self._on_prop_doubleclick)
        paned.add(right_frame, weight=1)

        self.selected_item_idx = None
        self.prop_edit_popup = None
        self.data = None

    def _on_item_select(self, event):
        sel = self.items_tree.selection()
        if not sel:
            return
        item_id = sel[0]
        if not item_id.startswith('item_'):
            return
        idx = int(item_id.split('_')[1])
        self.selected_item_idx = idx
        self._show_item_props(idx)

    def _show_item_props(self, idx):
        for row in self.prop_tree.get_children():
            self.prop_tree.delete(row)

        if idx < 0 or idx >= len(self.data['inventoryDataList']):
            return
        item = self.data['inventoryDataList'][idx]
        if not isinstance(item, list) or len(item) < 2:
            return
        data = item[1] if isinstance(item[1], dict) else {}
        self._build_prop_tree('', data)

    def _build_prop_tree(self, parent, node):
        if isinstance(node, dict):
            for k, v in node.items():
                node_id = f'{parent}.{k}' if parent else f'root.{k}'
                if isinstance(v, (dict, list)):
                    self.prop_tree.insert(parent, tk.END, iid=node_id, text=str(k),
                                          values=(f'({"dict" if isinstance(v, dict) else "list"})',))
                    self._build_prop_tree(node_id, v)
                else:
                    self.prop_tree.insert(parent, tk.END, iid=node_id, text=str(k), values=(str(v),))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                node_id = f'{parent}[{i}]'
                if isinstance(v, (dict, list)):
                    self.prop_tree.insert(parent, tk.END, iid=node_id, text=f'[{i}]',
                                          values=(f'({"dict" if isinstance(v, dict) else "list"})',))
                    self._build_prop_tree(node_id, v)
                else:
                    self.prop_tree.insert(parent, tk.END, iid=node_id, text=f'[{i}]', values=(str(v),))

    def _on_prop_doubleclick(self, event):
        sel = self.prop_tree.selection()
        if not sel or not self.prop_tree.exists(sel[0]):
            return
        node_id = sel[0]
        current_value = self.prop_tree.item(node_id, 'values')[0] if self.prop_tree.item(node_id, 'values') else ''

        # Only allow editing leaf nodes (not dicts/lists)
        children = self.prop_tree.get_children(node_id)
        if children:
            return  # skip non-leaf

        # Parse the path from node_id to find the actual value
        self._edit_prop_value(node_id, current_value)

    def _edit_prop_value(self, node_id, current_val):
        if self.prop_edit_popup:
            self.prop_edit_popup.destroy()

        popup = tk.Toplevel(self.root)
        popup.title('Изменить значение')
        popup.geometry('380x120')
        popup.resizable(False, False)

        ttk.Label(popup, text=f'{node_id}:').pack(pady=(8,0))
        entry = ttk.Entry(popup, width=45)
        entry.insert(0, current_val)
        entry.pack(pady=5, padx=10, fill=tk.X)
        entry.focus_set()
        entry.selection_range(0, tk.END)

        def save():
            try:
                new_val = entry.get().strip()
                target = self.data['inventoryDataList'][self.selected_item_idx]
                data_dict = target[1] if isinstance(target[1], dict) else target[0]
                self._set_value_by_path(data_dict, node_id, self._parse_val(new_val))
                self._show_item_props(self.selected_item_idx)
                popup.destroy()
            except Exception as ex:
                messagebox.showerror('Ошибка', str(ex))

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text='OK', command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='Отмена', command=popup.destroy).pack(side=tk.LEFT, padx=5)
        entry.bind('<Return>', lambda e: save())
        entry.bind('<Escape>', lambda e: popup.destroy())

        self.prop_edit_popup = popup

    def _set_value_by_path(self, obj, path, val):
        """Set value in nested dict/list by dot/bracket path, e.g. root.Main[0].key or root.Main[11][6]"""
        if path.startswith('root.'):
            path = path[5:]
        # Prepend dot so our regex works for the first segment too
        path = '.' + path

        import re as _re
        tokens = _re.findall(r'\.([^.[]+)|\[(\d+)\]', path)
        segments = []
        for key_part, idx_part in tokens:
            if key_part:
                segments.append(('key', key_part))
            else:
                segments.append(('idx', int(idx_part)))

        current = obj
        for i, (seg_type, seg_val) in enumerate(segments):
            is_last = i == len(segments) - 1
            if is_last:
                if seg_type == 'key':
                    current[seg_val] = val
                else:
                    current[seg_val] = val
                return
            else:
                current = current[seg_val]

    def _parse_val(self, s):
        if s.lower() == 'true':
            return True
        if s.lower() == 'false':
            return False
        try:
            return int(s)
        except ValueError:
            pass
        try:
            return float(s)
        except ValueError:
            pass
        return s

    def _get_inventory(self):
        return self.data['inventoryDataList'] if self.data else []

    def _populate_items(self):
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)
        self.selected_item_idx = None
        for row in self.prop_tree.get_children():
            self.prop_tree.delete(row)

        for idx, item in enumerate(self.data['inventoryDataList']):
            if not isinstance(item, list) or len(item) < 2:
                continue
            item_id = item[0] if isinstance(item[0], str) else 'unknown'
            data = item[1] if isinstance(item[1], dict) else {}
            name = data.get('idName', item_id)
            slot = item[9] if len(item) > 9 else 'N/A'
            self.items_tree.insert('', tk.END, iid=f'item_{idx}', text=name, values=(slot,))

    # ========== Buffs Tab ==========
    def _build_buffs_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text='Эффекты')

        top_row = ttk.Frame(tab)
        top_row.pack(fill=tk.X)
        ttk.Button(top_row, text='Добавить эффект', command=self._add_buff).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_row, text='Удалить эффект', command=self._del_buff).pack(side=tk.LEFT, padx=2)

        columns = ('id', 'duration', 'power', 'source', 'p4', 'p5', 'p6', 'p7')
        self.buffs_tree = ttk.Treeview(tab, columns=columns, show='headings', height=18)
        self.buffs_tree.heading('id', text='ID')
        self.buffs_tree.column('id', width=160)
        self.buffs_tree.heading('duration', text='Duration')
        self.buffs_tree.column('duration', width=80)
        self.buffs_tree.heading('power', text='Power')
        self.buffs_tree.column('power', width=70)
        self.buffs_tree.heading('source', text='Source')
        self.buffs_tree.column('source', width=80)
        self.buffs_tree.heading('p4', text='P4')
        self.buffs_tree.column('p4', width=70)
        self.buffs_tree.heading('p5', text='P5')
        self.buffs_tree.column('p5', width=70)
        self.buffs_tree.heading('p6', text='P6')
        self.buffs_tree.column('p6', width=80)
        self.buffs_tree.heading('p7', text='P7')
        self.buffs_tree.column('p7', width=50)

        scroll = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.buffs_tree.yview)
        self.buffs_tree.configure(yscrollcommand=scroll.set)
        self.buffs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(6,0))
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(6,0))

        self.buffs_tree.bind('<Double-1>', self._on_buff_doubleclick)

    def _populate_buffs(self):
        for row in self.buffs_tree.get_children():
            self.buffs_tree.delete(row)

        buffs = self.data.get('characterDataMap', {}).get('buffs', [])
        for i in range(0, len(buffs), 8):
            chunk = buffs[i:i+8]
            # Pad to 8 if needed
            while len(chunk) < 8:
                chunk.append(0.0)
            vals = [str(v) for v in chunk]
            self.buffs_tree.insert('', tk.END, iid=f'buff_{i//8}', values=vals)

    def _on_buff_doubleclick(self, event):
        sel = self.buffs_tree.selection()
        if not sel:
            return
        item_id = sel[0]
        col = self.buffs_tree.identify_column(event.x)
        col_idx = int(col.replace('#', '')) - 1
        current = self.buffs_tree.item(item_id, 'values')[col_idx]

        popup = tk.Toplevel(self.root)
        popup.title('Изменить')
        popup.geometry('350x100')
        popup.resizable(False, False)

        col_names = ['ID', 'Duration', 'Power', 'Source', 'P4', 'P5', 'P6', 'P7']
        ttk.Label(popup, text=f'{col_names[col_idx]} :').pack(pady=(8,0))
        entry = ttk.Entry(popup, width=45)
        entry.insert(0, current)
        entry.pack(pady=5, padx=10, fill=tk.X)
        entry.focus_set()
        entry.selection_range(0, tk.END)

        def save():
            try:
                new_val = entry.get().strip()
                idx = int(item_id.split('_')[1])
                buffs = self.data['characterDataMap']['buffs']
                offset = idx * 8 + col_idx
                # Extend list if needed
                while len(buffs) <= offset:
                    buffs.append(0.0)
                buffs[offset] = self._parse_val(new_val)
                self._populate_buffs()
                popup.destroy()
            except Exception as ex:
                messagebox.showerror('Ошибка', str(ex))

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text='OK', command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='Отмена', command=popup.destroy).pack(side=tk.LEFT, padx=5)
        entry.bind('<Return>', lambda e: save())
        entry.bind('<Escape>', lambda e: popup.destroy())

    def _add_buff(self):
        buffs = self.data['characterDataMap'].get('buffs')
        if buffs is None:
            self.data['characterDataMap']['buffs'] = []
            buffs = self.data['characterDataMap']['buffs']
        new_buff = ['o_b_bless', 3600.0, 1.0, 'player', -4.0, -4.0, -4.0, 0.0]
        buffs.extend(new_buff)
        self._populate_buffs()
        self._log('Эффект добавлен')

    def _del_buff(self):
        sel = self.buffs_tree.selection()
        if not sel:
            return
        item_id = sel[0]
        idx = int(item_id.split('_')[1])
        buffs = self.data['characterDataMap']['buffs']
        del buffs[idx*8:(idx+1)*8]
        self._populate_buffs()
        self._log('Эффект удалён')

    # ========== Save discovery ==========
    def _scan_saves(self):
        if not CHARACTERS_DIR.exists():
            self._log(f'Папка не найдена: {CHARACTERS_DIR}')
            return
        chars = sorted([d.name for d in CHARACTERS_DIR.iterdir() if d.is_dir() and d.name.startswith('character_')],
                       key=lambda x: int(x.split('_')[-1]))
        self.char_combo['values'] = chars
        if chars:
            self.char_combo.current(0)
            self._on_char_select()

    def _on_char_select(self, event=None):
        self.char_folder = self.char_combo.get()
        if not self.char_folder:
            return
        char_path = CHARACTERS_DIR / self.char_folder
        saves = sorted([d.name for d in char_path.iterdir()
                        if d.is_dir() and (d / 'data.sav').exists() and not d.name.endswith('.backup')],
                       key=lambda x: int(x.split('_')[-1]) if x.split('_')[-1].isdigit() else 0)
        self.save_combo['values'] = saves
        if saves:
            self.save_combo.current(len(saves) - 1)
            self._on_save_select()

    def _on_save_select(self, event=None):
        if not self.char_folder or not self.save_combo.get():
            return
        self.save_folder = self.save_combo.get()
        self._read_save()

    def _read_save(self):
        path = CHARACTERS_DIR / self.char_folder / self.save_folder / 'data.sav'
        if not path.exists():
            msg = f'Файл не найден: {path}'
            self._log(msg)
            messagebox.showerror('Ошибка', msg)
            return
        try:
            with open(path, 'rb') as f:
                compressed = f.read()
            decompressed = zlib.decompress(compressed)
            text = decompressed.decode('utf-8', errors='replace')

            depth = 0
            json_end = -1
            for i, ch in enumerate(text):
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        json_end = i + 1
                        break

            self.current_json = text[:json_end]
            self.data = json.loads(self.current_json)
            self.orig_json = None
            self.current_save = path
            self._refresh_all()
            self._log(f'Загружен: {self.char_folder}/{self.save_folder}')
        except Exception as e:
            msg = f'Не удалось прочитать файл: {e}'
            self._log(msg)
            messagebox.showerror('Ошибка', msg)

    # ========== Refresh ==========
    def _refresh_all(self):
        if not self.data:
            return
        cdm = self.data.get('characterDataMap', {})
        if not isinstance(cdm, dict):
            return

        # Position tab
        name = cdm.get('nameKey', '?')
        loc = cdm.get('locationTitleKey', '?')
        gx = cdm.get('playerGridX', '?')
        gy = cdm.get('playerGridY', '?')
        lx = cdm.get('localX', '?')
        ly = cdm.get('localY', '?')
        cloc = cdm.get('checkpointLocation', '?')

        info = (
            f'Имя: {name}\n'
            f'Локация: {loc}  (чекпоинт: {cloc})\n'
            f'Глобальные (playerGridX/Y): X={gx}  Y={gy}\n'
            f'Локальные (localX/Y): X={lx}  Y={ly}'
        )
        self.info_text.configure(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.configure(state='disabled')

        self.pos_entries['location'].delete(0, tk.END)
        self.pos_entries['location'].insert(0, str(loc))
        self.pos_entries['grid_x'].delete(0, tk.END)
        self.pos_entries['grid_x'].insert(0, str(gx))
        self.pos_entries['grid_y'].delete(0, tk.END)
        self.pos_entries['grid_y'].insert(0, str(gy))
        self.pos_entries['local_x'].delete(0, tk.END)
        self.pos_entries['local_x'].insert(0, str(lx))
        self.pos_entries['local_y'].delete(0, tk.END)
        self.pos_entries['local_y'].insert(0, str(ly))

        # Stats tab
        self.st_name.configure(text=name)
        self.st_class.configure(text=cdm.get('playerClass', '?'))
        self.st_lvl.configure(text=str(cdm.get('LVL', '?')))

        for key in self.stat_entries:
            val = cdm.get(key, 0)
            if isinstance(val, (int, float)):
                val = int(val)
            self.stat_entries[key].delete(0, tk.END)
            self.stat_entries[key].insert(0, str(val))

        # Bonus tab
        for key in self.bonus_entries:
            val = cdm.get(key, 0)
            if isinstance(val, (int, float)):
                val = round(val, 2)
            self.bonus_entries[key].delete(0, tk.END)
            self.bonus_entries[key].insert(0, str(val))

        # Items tab
        self._populate_items()

        # Buffs tab
        self._populate_buffs()

    # ========== Save ==========
    def _save(self):
        if not self.data or not self.current_save:
            messagebox.showwarning('Нет данных', 'Сначала выберите сейв')
            return

        cdm = self.data.get('characterDataMap', {})
        if not isinstance(cdm, dict):
            messagebox.showerror('Ошибка', 'characterDataMap не найден')
            return

        # Read values from all tabs
        edits = {}

        # Position tab
        try:
            edits['location'] = self.pos_entries['location'].get().strip()
            edits['grid_x'] = float(self.pos_entries['grid_x'].get().strip())
            edits['grid_y'] = float(self.pos_entries['grid_y'].get().strip())
            edits['local_x'] = float(self.pos_entries['local_x'].get().strip())
            edits['local_y'] = float(self.pos_entries['local_y'].get().strip())
        except ValueError:
            messagebox.showerror('Ошибка', 'Неверный формат чисел в позиции')
            return

        # Stats tab
        stat_vals = {}
        for key in self.stat_entries:
            try:
                stat_vals[key] = float(self.stat_entries[key].get().strip())
            except ValueError:
                messagebox.showerror('Ошибка', f'Неверное значение для {key}')
                return

        # Bonus tab
        for key in self.bonus_entries:
            raw = self.bonus_entries[key].get().strip()
            if raw:
                try:
                    cdm[key] = float(raw)
                except ValueError:
                    pass

        # Backup
        save_dir = CHARACTERS_DIR / self.char_folder / self.save_folder
        bak_path = save_dir / 'data.sav.bak'
        if not bak_path.exists():
            shutil.copy2(self.current_save, bak_path)
            self._log('Бэкап создан: data.sav.bak')
        else:
            self._log('Бэкап уже существует, пропускаю')

        # Apply position edits to data
        cdm['localX'] = edits['local_x']
        cdm['localY'] = edits['local_y']
        cdm['playerGridX'] = edits['grid_x']
        cdm['playerGridY'] = edits['grid_y']
        cdm['locationTitleKey'] = edits['location']
        cdm['checkpointLocation'] = f'r_{edits["location"]}'

        # Apply stat edits to data
        for key, val in stat_vals.items():
            cdm[key] = int(val) if key in ('HP', 'MP', 'XP', 'SP', 'AP', 'LVL') else val

        # Serialize full JSON (compact format, matching game style)
        new_json = json.dumps(self.data, separators=(',', ':'))

        # Calculate hash
        salt = f'stOne!characters_v1!{self.char_folder}!{self.save_folder}!shArd'
        md5_input = (new_json + salt).encode('utf-8')
        new_hash = hashlib.md5(md5_input).hexdigest()

        # Write data.sav
        new_text = new_json + new_hash + '\x00'
        new_compressed = zlib.compress(new_text.encode('utf-8'))
        with open(self.current_save, 'wb') as f:
            f.write(new_compressed)

        # Update save.map
        map_path = save_dir / 'save.map'
        if map_path.exists():
            with open(map_path, 'rb') as f:
                map_compressed = f.read()
            map_dec = zlib.decompress(map_compressed)
            map_text = map_dec.decode('utf-8', errors='replace')

            depth = 0
            map_json_end = -1
            for i, ch in enumerate(map_text):
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        map_json_end = i + 1
                        break

            map_json = map_text[:map_json_end]
            # rebuild map json clean
            map_obj = json.loads(map_json)
            map_obj['valid'] = True
            map_obj['locationTitleKey'] = edits['location']
            map_new_json = json.dumps(map_obj, separators=(',', ':'))

            map_md5_input = (map_new_json + salt).encode('utf-8')
            map_new_hash = hashlib.md5(map_md5_input).hexdigest()
            map_new_text = map_new_json + map_new_hash + '\x00'
            map_new_compressed = zlib.compress(map_new_text.encode('utf-8'))
            with open(map_path, 'wb') as f:
                f.write(map_new_compressed)

        self.current_json = new_json
        messagebox.showinfo('Готово', 'Сохранение обновлено!')
        self._log('Сохранено')
        self._refresh_all()


if __name__ == '__main__':
    root = tk.Tk()
    app = StoneshardEditor(root)
    root.mainloop()
