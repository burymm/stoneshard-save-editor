# Stoneshard Position Editor

GUI tool to edit player position in Stoneshard save files.

## Features

- Auto-detects all saves across characters
- **Tab 1 — Position**: view and edit coordinates (global localX/Y, local playerGridX/Y) and location
- **Tab 2 — Stats**: edit character attributes (STR, AGL, PRC, Vitality, WIL, HP, MP, XP, SP, AP)
- Automatic backup before saving
- Correctly recalculates checksum (salted hash)

## Build

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "StoneshardPosEditor" StoneshardPosEditor.py
```

The exe will be in the `dist/` folder.

## Usage

1. Run `StoneshardPosEditor.exe`
2. Select character and save from dropdowns
3. Edit the coordinates
4. Click "Save"

First backup is saved as `data.sav.bak` next to the save file.

---

# Stoneshard Position Editor

GUI-редактор позиции персонажа для игры Stoneshard.

## Возможности

- Автоматическое определение всех сохранений
- **Вкладка 1 — Позиция**: просмотр и редактирование координат (глобальные localX/Y, локальные playerGridX/Y) и локации
- **Вкладка 2 — Характеристики**: редактирование атрибутов (STR, AGL, PRC, Vitality, WIL, HP, MP, XP, SP, AP)
- Автоматический бэкап перед сохранением
- Корректный пересчёт контрольной суммы (hash с солью)

## Сборка

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "StoneshardPosEditor" StoneshardPosEditor.py
```

Готовый exe будет в папке `dist/`.

## Использование

1. Запустить `StoneshardPosEditor.exe`
2. Выбрать персонажа и сейв из выпадающих списков
3. Изменить координаты
4. Нажать «Сохранить»

Первый бэкап сохраняется как `data.sav.bak` рядом с сейвом.
