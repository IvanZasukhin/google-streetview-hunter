"""
Интерфейс командной строки для StreetViewHunter.
"""

import argparse
import sys
import yaml
from typing import Optional

from .core import StreetViewHunter
from .utils import load_config, validate_coordinates


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Google Street View Hunter - поиск панорам в заданной области",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --api-key=KEY --config=configs/syktyvkar.yaml
  %(prog)s --api-key=KEY --lat-min=61.66 --lat-max=61.69 --lon-min=50.81 --lon-max=50.86
  %(prog)s --api-key=KEY --city сыктывкар --step-km 0.15 --output мои_панорамы.txt
        """
    )
    
    # Обязательные параметры
    parser.add_argument(
        "--api-key",
        required=True,
        help="Google Cloud API ключ (обязательно)"
    )
    
    # Группа: режимы работы
    mode_group = parser.add_argument_group("Режимы работы")
    mode_group.add_argument(
        "--config",
        help="Путь к YAML-конфигурационному файлу"
    )
    
    # Группа: параметры области (если нет конфига)
    area_group = parser.add_argument_group(
        "Параметры области поиска",
        "Используются, если не указан --config"
    )
    area_group.add_argument(
        "--lat-min",
        type=float,
        help="Минимальная широта (например: 61.66)"
    )
    area_group.add_argument(
        "--lat-max",
        type=float,
        help="Максимальная широта (например: 61.69)"
    )
    area_group.add_argument(
        "--lon-min",
        type=float,
        help="Минимальная долгота (например: 50.81)"
    )
    area_group.add_argument(
        "--lon-max",
        type=float,
        help="Максимальная долгота (например: 50.86)"
    )
    
    # Группа: параметры поиска
    search_group = parser.add_argument_group("Параметры поиска")
    search_group.add_argument(
        "--step-km",
        type=float,
        default=0.15,
        help="Шаг сетки в километрах (по умолчанию: 0.15)"
    )
    search_group.add_argument(
        "--search-radius",
        type=int,
        default=50,
        help="Радиус поиска в метрах (по умолчанию: 50)"
    )
    search_group.add_argument(
        "--max-points",
        type=int,
        default=1000,
        help="Максимум точек для проверки (по умолчанию: 1000)"
    )
    search_group.add_argument(
        "--delay",
        type=float,
        default=0.03,
        help="Задержка между запросами в секундах (по умолчанию: 0.03)"
    )
    
    # Группа: выходные данные
    output_group = parser.add_argument_group("Выходные данные")
    output_group.add_argument(
        "--output",
        default="panoramas.txt",
        help="Имя выходного файла (по умолчанию: panoramas.txt)"
    )
    output_group.add_argument(
        "--city",
        help="Название города (для именования файлов)"
    )
    
    # Флаги
    parser.add_argument(
        "--version",
        action="version",
        version="StreetViewHunter 1.0.0"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Подробный вывод"
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """Проверка корректности аргументов."""
    
    # Если указан конфиг, проверяем его существование
    if args.config:
        import os
        if not os.path.exists(args.config):
            print(f"❌ Ошибка: файл конфигурации '{args.config}' не найден")
            return False
    
    # Если конфиг не указан, проверяем обязательные параметры области
    else:
        required = ['lat_min', 'lat_max', 'lon_min', 'lon_max']
        missing = [param for param in required if getattr(args, param) is None]
        
        if missing:
            print("❌ Ошибка: следующие параметры обязательны при отсутствии --config:")
            for param in missing:
                print(f"  --{param.replace('_', '-')}")
            return False
        
        # Проверка корректности координат
        try:
            validate_coordinates(
                args.lat_min, args.lat_max,
                args.lon_min, args.lon_max
            )
        except ValueError as e:
            print(f"❌ Ошибка в координатах: {e}")
            return False
    
    # Проверка числовых параметров
    if args.step_km <= 0:
        print("❌ Ошибка: --step-km должен быть больше 0")
        return False
    
    if args.search_radius <= 0:
        print("❌ Ошибка: --search-radius должен быть больше 0")
        return False
    
    if args.max_points <= 0:
        print("❌ Ошибка: --max-points должен быть больше 0")
        return False
    
    if
