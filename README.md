# Stoneshard Position Editor

GUI tool to edit player position in Stoneshard save files.

## Features

- Auto-detects all saves across characters
- Displays current coordinates (global localX/Y and local playerGridX/Y)
- Edit coordinates and location
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
- Просмотр текущих координат (глобальные localX/Y и локальные playerGridX/Y)
- Редактирование координат и локации
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
