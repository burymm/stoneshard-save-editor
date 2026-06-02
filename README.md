# Stoneshard Position Editor

GUI tool to edit player position in Stoneshard save files.

## Features

- Auto-detects all saves across characters
- **Tab 1 — Position**: view and edit coordinates (global playerGridX/Y, local localX/Y) and location
- **Tab 2 — Stats**: edit character attributes (STR, AGL, PRC, Vitality, WIL, HP, MP, XP, SP, AP)
- **Tab 3 — Bonuses**: edit bonus stats (bCRT, bCRTD, bEVS, bHp, bMp, bmax_hp, bMP_Restoration, bSavvy, bVSN, bFMB)
- **Tab 4 — Items**: browse inventory items in a tree view, edit any property (damage, resistance, charges, stack size, etc.) via double-click
- **Tab 5 — Effects**: view and edit active buffs/debuffs (duration, power, source, parameters); add or remove effects

## Download

Pre-built binary: [StoneshardPosEditor.zip](StoneshardPosEditor.zip) (extract and run, no install needed).
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
- **Вкладка 1 — Позиция**: просмотр и редактирование координат (глобальные playerGridX/Y, локальные localX/Y) и локации
- **Вкладка 2 — Характеристики**: редактирование атрибутов (STR, AGL, PRC, Vitality, WIL, HP, MP, XP, SP, AP)
- **Вкладка 3 — Бонусы**: бонусные характеристики (bCRT, bCRTD, bEVS, bHp, bMp, bmax_hp, bMP_Restoration, bSavvy, bVSN, bFMB)
- **Вкладка 4 — Предметы**: просмотр инвентаря в виде дерева, редактирование любых свойств (урон, сопротивления, заряды, количество, стек и т.д.) двойным кликом
- **Вкладка 5 — Эффекты**: просмотр и редактирование активных баффов/дебаффов (длительность, сила, источник, параметры); добавление и удаление эффектов

## Скачать

Готовый бинарник: [StoneshardPosEditor.zip](StoneshardPosEditor.zip) (распаковать и запустить, установка не требуется).
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
