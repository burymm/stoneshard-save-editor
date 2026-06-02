import zlib, json, re, hashlib, os, shutil, tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

BASE_DIR = Path(os.environ.get('LOCALAPPDATA', '')) / 'StoneShard'
CHARACTERS_DIR = BASE_DIR / 'characters_v1'

FIELD_LABELS = {
    'STR': 'Сила', 'AGL': 'Ловкость', 'PRC': 'Восприятие',
    'Vitality': 'Телосложение', 'WIL': 'Сила воли',
    'HP': 'HP', 'MP': 'MP', 'XP': 'XP', 'LVL': 'Уровень',
    'SP': 'Очки навыков', 'AP': 'Очки статов',
    'playerClass': 'Класс', 'nameKey': 'Имя',
}

class StoneshardEditor:
    def __init__(self, root):
        self.root = root
        self.root.title('Stoneshard Save Editor')
        self.root.geometry('620x560')
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

        # Top bar: character & save selection
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

        # Notebook with tabs
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        # --- Tab 1: Position ---
        self._build_position_tab()

        # --- Tab 2: Stats ---
        self._build_stats_tab()

        # Bottom bar: save + refresh + exit
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
            ('grid_x', 'Локальная X (playerGridX):'),
            ('grid_y', 'Локальная Y (playerGridY):'),
            ('local_x', 'Глобальная X (localX):'),
            ('local_y', 'Глобальная Y (localY):'),
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

        # Player info
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
            self._log(f'Файл не найден: {path}')
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
            self.orig_json = None
            self.current_save = path
            self._refresh_all()
            self._log(f'Загружен: {self.char_folder}/{self.save_folder}')
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось прочитать файл:\n{e}')
            self._log('Ошибка чтения')

    # ========== Refresh ==========
    def _refresh_all(self):
        if not self.current_json:
            return
        data = json.loads(self.current_json)
        cdm = data.get('characterDataMap', {})
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
            f'Глобальные (localX/Y): X={lx}  Y={ly}\n'
            f'Локальные (playerGridX/Y): X={gx}  Y={gy}'
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

    # ========== Save ==========
    def _save(self):
        if not self.current_json or not self.current_save:
            messagebox.showwarning('Нет данных', 'Сначала выберите сейв')
            return

        # Build changes from both tabs
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

        # Backup
        save_dir = CHARACTERS_DIR / self.char_folder / self.save_folder
        bak_path = save_dir / 'data.sav.bak'
        if not bak_path.exists():
            shutil.copy2(self.current_save, bak_path)
            self._log('Бэкап создан: data.sav.bak')
        else:
            self._log('Бэкап уже существует, пропускаю')

        # Apply edits to JSON text
        new_json = self.current_json
        new_json = re.sub(r'"localX":\s*[\d.]+', f'"localX": {edits["local_x"]}', new_json)
        new_json = re.sub(r'"localY":\s*[\d.]+', f'"localY": {edits["local_y"]}', new_json)
        new_json = re.sub(r'"playerGridX":\s*[\d.-]+', f'"playerGridX": {edits["grid_x"]}', new_json)
        new_json = re.sub(r'"playerGridY":\s*[\d.-]+', f'"playerGridY": {edits["grid_y"]}', new_json)
        new_json = re.sub(r'"locationTitleKey":\s*"[^"]*"', f'"locationTitleKey": "{edits["location"]}"', new_json)
        new_json = re.sub(r'"checkpointLocation":\s*"[^"]*"', f'"checkpointLocation": "r_{edits["location"]}"', new_json)

        for key, val in stat_vals.items():
            pattern = rf'"{key}":\s*[\d.]+'
            replacement = f'"{key}": {val}'
            if key in ('HP', 'MP', 'XP', 'SP', 'AP', 'LVL'):
                replacement = f'"{key}": {int(val)}'
            new_json = re.sub(pattern, replacement, new_json)
            if not re.search(pattern, new_json):
                messagebox.showwarning('Предупреждение', f'Поле {key} не найдено в файле')

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
            map_new_json = re.sub(r'"valid":\s*false', '"valid": true', map_json)
            map_new_json = re.sub(r'"locationTitleKey":\s*"[^"]*"', f'"locationTitleKey": "{edits["location"]}"', map_new_json)

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
