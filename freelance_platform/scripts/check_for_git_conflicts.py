#!/usr/bin/env python
"""
Скрипт для проверки наличия маркеров конфликтов Git в кодовой базе.
Запускается перед деплоем или в CI, чтобы предотвратить попадание незакоммиченных
конфликтов в рабочую версию платформы.
"""

import os
import re
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple

# Регулярное выражение для поиска маркеров конфликтов
CONFLICT_MARKERS = re.compile(r'(?:^|\s)(?:<{7}|={7}|>{7})')

# Директории по умолчанию для исключения из проверки
DEFAULT_EXCLUDE_DIRS = [
    '.git',
    'node_modules',
    'venv',
    '.venv',  # Добавляем .venv в игнорируемые папки
    'env',
    'static/vendor',
    'media',
    '__pycache__',
    'migrations',
]

# Расширения файлов, которые нужно проверять
DEFAULT_INCLUDE_EXTS = [
    '.py', '.js', '.html', '.css', '.scss', '.jsx', '.ts', '.tsx', '.md',
    '.yml', '.yaml', '.json', '.txt', '.sh', '.xml', '.vue'
]


def find_conflict_markers(file_path: str) -> List[Tuple[int, str]]:
    """Находит маркеры конфликтов Git в файле."""
    conflicts = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f, 1):
                if CONFLICT_MARKERS.search(line):
                    conflicts.append((i, line.strip()))
    except Exception as e:
        print(f"Ошибка при проверке файла {file_path}: {e}")
    
    return conflicts


def should_check_file(file_path: str, include_exts: List[str], exclude_dirs: List[str]) -> bool:
    """Проверяет, нужно ли проверять данный файл."""
    # Проверяем расширение
    if not any(file_path.endswith(ext) for ext in include_exts) and include_exts:
        return False
    
    # Проверяем, не находится ли файл в исключенной директории
    path_str = str(file_path)
    for exclude_dir in exclude_dirs:
        if f"{os.sep}{exclude_dir}{os.sep}" in path_str or path_str.startswith(f"{exclude_dir}{os.sep}"):
            return False
            
    return True


def main():
    parser = ArgumentParser(description='Проверка наличия маркеров конфликтов Git в кодовой базе')
    parser.add_argument('--path', '-p', default='.', help='Директория для проверки')
    parser.add_argument('--exclude', '-e', default=','.join(DEFAULT_EXCLUDE_DIRS),
                        help='Список директорий для исключения (через запятую)')
    parser.add_argument('--include-exts', '-i', default=','.join(DEFAULT_INCLUDE_EXTS),
                        help='Список расширений файлов для проверки (через запятую)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    
    args = parser.parse_args()
    
    exclude_dirs = args.exclude.split(',') if args.exclude else DEFAULT_EXCLUDE_DIRS
    include_exts = args.include_exts.split(',') if args.include_exts else DEFAULT_INCLUDE_EXTS
    
    start_dir = os.path.abspath(args.path)
    conflict_files = []
    
    # Рекурсивный обход директорий
    for root, dirs, files in os.walk(start_dir):
        # Исключаем директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in files:
            file_path = os.path.join(root, filename)
            
            if should_check_file(file_path, include_exts, exclude_dirs):
                conflicts = find_conflict_markers(file_path)
                if conflicts:
                    conflict_files.append((file_path, conflicts))
                    if args.verbose:
                        print(f"КОНФЛИКТ в {file_path}:")
                        for line_num, line in conflicts:
                            print(f"  Строка {line_num}: {line}")
                        print()
    
    if conflict_files:
        print(f"\nНайдено {len(conflict_files)} файлов с маркерами конфликтов Git:")
        for file_path, conflicts in conflict_files:
            rel_path = os.path.relpath(file_path, start_dir)
            conflict_lines = [str(line) for line, _ in conflicts]
            print(f"- {rel_path} (строки: {', '.join(conflict_lines[:10])}{'...' if len(conflict_lines) > 10 else ''})")
        
        print("\nПожалуйста, решите эти конфликты перед продолжением.")
        sys.exit(1)
    else:
        print("Маркеров конфликтов Git не найдено. Всё в порядке!")
        sys.exit(0)


if __name__ == "__main__":
    main() 