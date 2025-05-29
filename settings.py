screensize = (1280,720)
mode = "release"
gravity = 2000 
jump_power = -700
sprint_power = 22
import os
import pyperclip

def copy_py_files_to_clipboard():
    # Папка с проектом
    target_directory = os.path.join(os.getcwd(), '')
    
    # Путь к текущему скрипту
    current_script_path = os.path.abspath(__file__)

    result = ""

    # Рекурсивно обходим все папки и файлы
    for root, dirs, files in os.walk(target_directory):
        for filename in files:
            if filename.endswith(".py") or filename.endswith(".json"):
                file_path = os.path.abspath(os.path.join(root, filename))

                # Пропускаем сам скрипт
                if file_path == current_script_path:
                    continue

                # Читаем содержимое файла
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Добавляем в результат: путь к файлу + содержимое
                relative_path = os.path.relpath(file_path, target_directory)
                result += f"{relative_path}\n{content}\n"

    # Копируем всё в буфер обмена
    pyperclip.copy(result)
    print(result)

# Запуск
copy_py_files_to_clipboard()