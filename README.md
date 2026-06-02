# Stoneshard Position Editor

GUI-редактор позиции персонажа для игры Stoneshard.

## Возможности

- Автоматическое определение всех сохранений
- Просмотр текущих координат (глобальные localX/Y и локальные playerGridX/Y)
- Редактирование координат и локации
- Автоматический бэкап перед сохранением
- Корректный пересчёт контрольной суммы (hash с солью)

## Как собрать

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
