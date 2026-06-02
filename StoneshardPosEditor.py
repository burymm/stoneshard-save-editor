import zlib, json, re, hashlib, os, shutil, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

BASE_DIR = Path(os.environ.get('LOCALAPPDATA', '')) / 'StoneShard'
CHARACTERS_DIR = BASE_DIR / 'characters_v1'

class StoneshardPosEditor:
    def __init__(self, root):
        self.root = root
        self.root.title('Stoneshard - редактор позиции')
        self.root.geometry('580x480')
        self.root.resizable(False, False)

        self.current_save = None
        self.current_json = None
        self.char_folder = None
        self.save_folder = None

        self._build_ui()
        self._scan_saves()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # Character & save selection
        ttk.Label(main, text='Персонаж:').grid(row=0, column=0, sticky='w')
        self.char_combo = ttk.Combobox(main, state='readonly', width=15)
        self.char_combo.grid(row=0, column=1, sticky='ew', padx=5)
        self.char_combo.bind('<<ComboboxSelected>>', self._on_char_select)

        ttk.Label(main, text='Сейв:').grid(row=0, column=2, sticky='w', padx=(10,0))
        self.save_combo = ttk.Combobox(main, state='readonly', width=15)
        self.save_combo.grid(row=0, column=3, sticky='ew', padx=5)
        self.save_combo.bind('<<ComboboxSelected>>', self._on_save_select)

        ttk.Separator(main, orient='horizontal').grid(row=1, column=0, columnspan=4, sticky='ew', pady=10)

        # Current info
        info_frame = ttk.LabelFrame(main, text='Текущая позиция', padding=8)
        info_frame.grid(row=2, column=0, columnspan=4, sticky='ew', pady=(0, 10))

        self.info_text = tk.Text(info_frame, height=6, width=65, state='disabled')
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # New position
        edit_frame = ttk.LabelFrame(main, text='Новая позиция', padding=8)
        edit_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(0, 10))

        row = 0
        ttk.Label(edit_frame, text='Локация:').grid(row=row, column=0, sticky='w')
        self.entry_location = ttk.Entry(edit_frame, width=30)
        self.entry_location.grid(row=row, column=1, sticky='ew', padx=5)
        row += 1

        ttk.Label(edit_frame, text='Локальная X (playerGridX):').grid(row=row, column=0, sticky='w')
        self.entry_grid_x = ttk.Entry(edit_frame, width=30)
        self.entry_grid_x.grid(row=row, column=1, sticky='ew', padx=5)
        row += 1

        ttk.Label(edit_frame, text='Локальная Y (playerGridY):').grid(row=row, column=0, sticky='w')
        self.entry_grid_y = ttk.Entry(edit_frame, width=30)
        self.entry_grid_y.grid(row=row, column=1, sticky='ew', padx=5)
        row += 1

        ttk.Label(edit_frame, text='Глобальная X (localX):').grid(row=row, column=0, sticky='w')
        self.entry_local_x = ttk.Entry(edit_frame, width=30)
        self.entry_local_x.grid(row=row, column=1, sticky='ew', padx=5)
        row += 1

        ttk.Label(edit_frame, text='Глобальная Y (localY):').grid(row=row, column=0, sticky='w')
        self.entry_local_y = ttk.Entry(edit_frame, width=30)
        self.entry_local_y.grid(row=row, column=1, sticky='ew', padx=5)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=(5, 0))

        ttk.Button(btn_frame, text='Сохранить', command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='Обновить данные', command=self._refresh_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='Выход', command=self.root.destroy).pack(side=tk.RIGHT, padx=5)

        # Status
        self.status_var = tk.StringVar(value='Готов')
        ttk.Label(main, textvariable=self.status_var, foreground='gray').grid(row=5, column=0, columnspan=4, sticky='w', pady=(5, 0))

        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(3, weight=1)

    def _log(self, msg):
        self.status_var.set(msg)

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
            self.current_remaining = text[json_end:]

            self.current_save = path
            self._refresh_info()
            self._log(f'Загружен: {self.char_folder}/{self.save_folder}')
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось прочитать файл:\n{e}')
            self._log('Ошибка чтения')

    def _refresh_info(self):
        if not self.current_json:
            return

        data = json.loads(self.current_json)
        cdm = data.get('characterDataMap', {})

        if not isinstance(cdm, dict):
            return

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

        self.entry_location.delete(0, tk.END)
        self.entry_location.insert(0, str(loc))

        self.entry_grid_x.delete(0, tk.END)
        self.entry_grid_x.insert(0, str(gx))

        self.entry_grid_y.delete(0, tk.END)
        self.entry_grid_y.insert(0, str(gy))

        self.entry_local_x.delete(0, tk.END)
        self.entry_local_x.insert(0, str(lx))

        self.entry_local_y.delete(0, tk.END)
        self.entry_local_y.insert(0, str(ly))

    def _save(self):
        if not self.current_json or not self.current_save:
            messagebox.showwarning('Нет данных', 'Сначала выберите сейв')
            return

        try:
            new_loc = self.entry_location.get().strip()
            new_gx = float(self.entry_grid_x.get().strip())
            new_gy = float(self.entry_grid_y.get().strip())
            new_lx = float(self.entry_local_x.get().strip())
            new_ly = float(self.entry_local_y.get().strip())
        except ValueError:
            messagebox.showerror('Ошибка', 'Неверный формат чисел')
            return

        # Backup
        save_dir = CHARACTERS_DIR / self.char_folder / self.save_folder
        bak_path = save_dir / 'data.sav.bak'
        if not bak_path.exists():
            shutil.copy2(self.current_save, bak_path)
            self._log('Бэкап создан: data.sav.bak')
        else:
            self._log('Бэкап уже существует, пропускаю')

        # Modify JSON
        new_json = self.current_json
        new_json = re.sub(r'"localX":\s*[\d.]+', f'"localX": {new_lx}', new_json)
        new_json = re.sub(r'"localY":\s*[\d.]+', f'"localY": {new_ly}', new_json)
        new_json = re.sub(r'"playerGridX":\s*[\d.-]+', f'"playerGridX": {new_gx}', new_json)
        new_json = re.sub(r'"playerGridY":\s*[\d.-]+', f'"playerGridY": {new_gy}', new_json)
        new_json = re.sub(r'"locationTitleKey":\s*"[^"]*"', f'"locationTitleKey": "{new_loc}"', new_json)
        new_json = re.sub(r'"checkpointLocation":\s*"[^"]*"', f'"checkpointLocation": "r_{new_loc}"', new_json)

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
            map_new_json = re.sub(r'"locationTitleKey":\s*"[^"]*"', f'"locationTitleKey": "{new_loc}"', map_new_json)

            map_md5_input = (map_new_json + salt).encode('utf-8')
            map_new_hash = hashlib.md5(map_md5_input).hexdigest()

            map_new_text = map_new_json + map_new_hash + '\x00'
            map_new_compressed = zlib.compress(map_new_text.encode('utf-8'))
            with open(map_path, 'wb') as f:
                f.write(map_new_compressed)

        self.current_json = new_json
        messagebox.showinfo('Готово', 'Позиция сохранена!')
        self._log('Сохранено')
        self._refresh_info()

if __name__ == '__main__':
    root = tk.Tk()
    app = StoneshardPosEditor(root)
    root.mainloop()
