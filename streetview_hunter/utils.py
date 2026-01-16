"""
Вспомогательные функции для StreetViewHunter.
"""

import yaml
import json
from typing import Dict, Any, Tuple
import math


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Загружает конфигурацию из YAML-файла.
    
    Args:
        config_path: Путь к YAML-файлу
        
    Returns:
        Словарь с конфигурацией
        
    Raises:
        FileNotFoundError: Если файл не найден
        yaml.YAMLError: Если файл содержит ошибки YAML
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Валидация минимальной конфигурации
    required_keys = ['bounds', 'search_params', 'output']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"В конфигурации отсутствует обязательный ключ: {key}")
    
    return config


def save_config(config: Dict[str, Any], config_path: str):
    """
    Сохраняет конфигурацию в YAML-файл.
    
    Args:
        config: Словарь с конфигурацией
        config_path: Путь для сохранения файла
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def validate_coordinates(lat_min: float, lat_max: float,
                        lon_min: float, lon_max: float) -> bool:
    """
    Проверяет корректность координат.
    
    Args:
        lat_min, lat_max: Границы по широте
        lon_min, lon_max: Границы по долготе
        
    Returns:
        True если координаты корректны
        
    Raises:
        ValueError: Если координаты некорректны
    """
    # Проверка диапазонов
    if not (-90 <= lat_min <= 90):
        raise ValueError(f"Широта lat_min={lat_min} вне диапазона [-90, 90]")
    
    if not (-90 <= lat_max <= 90):
        raise ValueError(f"Широта lat_max={lat_max} вне диапазона [-90, 90]")
    
    if not (-180 <= lon_min <= 180):
        raise ValueError(f"Долгота lon_min={lon_min} вне диапазона [-180, 180]")
    
    if not (-180 <= lon_max <= 180):
        raise ValueError(f"Долгота lon_max={lon_max} вне диапазона [-180, 180]")
    
    # Проверка порядка
    if lat_min >= lat_max:
        raise ValueError(f"lat_min ({lat_min}) должен быть меньше lat_max ({lat_max})")
    
    if lon_min >= lon_max:
        raise ValueError(f"lon_min ({lon_min}) должен быть меньше lon_max ({lon_max})")
    
    # Проверка разумности размеров
    lat_diff = lat_max - lat_min
    lon_diff = lon_max - lon_min
    
    if lat_diff > 10:
        raise ValueError(f"Слишком большая разница по широте: {lat_diff:.2f}° (>10°)")
    
    if lon_diff > 10:
        raise ValueError(f"Слишком большая разница по долготе: {lon_diff:.2f}° (>10°)")
    
    return True


def calculate_area_size(lat_min: float, lat_max: float,
                       lon_min: float, lon_max: float) -> Tuple[float, float]:
    """
    Рассчитывает размер области в километрах.
    
    Args:
        lat_min, lat_max: Границы по широте
        lon_min, lon_max: Границы по долготе
        
    Returns:
        Кортеж (ширина_км, высота_км)
    """
    avg_lat = (lat_min + lat_max) / 2
    
    # Коэффициенты преобразования
    km_per_degree_lat = 111.0
    km_per_degree_lon = 111.0 * math.cos(math.radians(avg_lat))
    
    # Размеры в километрах
    width_km = (lon_max - lon_min) * km_per_degree_lon
    height_km = (lat_max - lat_min) * km_per_degree_lat
    
    return (width_km, height_km)


def estimate_points_count(lat_min: float, lat_max: float,
                         lon_min: float, lon_max: float,
                         step_km: float) -> int:
    """
    Оценивает количество точек в сетке.
    
    Args:
        lat_min, lat_max: Границы по широте
        lon_min, lon_max: Границы по долготе
        step_km: Шаг сетки в километрах
        
    Returns:
        Ориентировочное количество точек
    """
    width_km, height_km = calculate_area_size(lat_min, lat_max, lon_min, lon_max)
    
    points_x = int(width_km / step_km) + 1
    points_y = int(height_km / step_km) + 1
    
    return points_x * points_y


def format_link(link_template: str, pano_id: str, lat: float, lng: float,
               domain: str = "google.de") -> str:
    """
    Форматирует ссылку на панораму.
    
    Args:
        link_template: Шаблон ссылки
        pano_id: ID панорамы
        lat, lng: Координаты
        domain: Домен Google (google.de, google.com и т.д.)
        
    Returns:
        Отформатированная ссылка
    """
    return link_template.format(
        domain=domain,
        lat=lat,
        lng=lng,
        pano_id=pano_id
    )


def save_results_json(results: list, output_path: str):
    """
    Сохраняет результаты в JSON-файл.
    
    Args:
        results: Список найденных панорам
        output_path: Путь для сохранения файла
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def load_results_json(input_path: str) -> list:
    """
    Загружает результаты из JSON-файла.
    
    Args:
        input_path: Путь к JSON-файлу
        
    Returns:
        Список панорам
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)
