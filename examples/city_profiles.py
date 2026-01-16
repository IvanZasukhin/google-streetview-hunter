#!/usr/bin/env python3
"""
Примеры профилей городов для StreetViewHunter.
"""

import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streetview_hunter.core import StreetViewHunter


# Профили городов
CITY_PROFILES = {
    "сыктывкар": {
        "name": "Сыктывкар",
        "bounds": {
            "lat_min": 61.66,
            "lat_max": 61.69,
            "lon_min": 50.81,
            "lon_max": 50.86
        },
        "search_params": {
            "step_km": 0.12,
            "search_radius": 50,
            "max_points": 800,
            "delay": 0.03
        },
        "description": "Столица Республики Коми, Россия"
    },
    
    "москва_центр": {
        "name": "Москва (центр)",
        "bounds": {
            "lat_min": 55.75,
            "lat_max": 55.78,
            "lon_min": 37.60,
            "lon_max": 37.65
        },
        "search_params": {
            "step_km": 0.15,
            "search_radius": 80,
            "max_points": 1500,
            "delay": 0.02
        },
        "description": "Центральная часть Москвы"
    }
}


def search_city(api_key, city_id):
    """Ищет панорамы в указанном городе."""
    
    if city_id not in CITY_PROFILES:
        print(f"❌ Профиль города '{city_id}' не найден")
        print(f"   Доступные города: {', '.join(CITY_PROFILES.keys())}")
        return
    
    profile = CITY_PROFILES[city_id]
    
    print(f"\n{'='*60}")
    print(f"🔍 Поиск в городе: {profile['name']}")
    print(f"📝 Описание: {profile['description']}")
    print(f"{'='*60}")
    
    hunter = StreetViewHunter(api_key)
    
    stats = hunter.search_area(
        lat_min=profile['bounds']['lat_min'],
        lat_max=profile['bounds']['lat_max'],
        lon_min=profile['bounds']['lon_min'],
        lon_max=profile['bounds']['lon_max'],
        step_km=profile['search_params']['step_km'],
        search_radius=profile['search_params']['search_radius'],
        max_points=profile['search_params']['max_points'],
        output_file=f"{city_id}_панорамы.txt",
        delay=profile['search_params']['delay']
    )
    
    return stats


def main():
    """Основная функция."""
    
    print("🏙️  ПРОФИЛИ ГОРОДОВ ДЛЯ STREETVIEWHUNTER")
    print("=" * 60)
    
    # Показываем доступные города
    print("\nДоступные профили городов:")
    for i, (city_id, profile) in enumerate(CITY_PROFILES.items(), 1):
        print(f"  {i:2d}. {city_id:20} - {profile['name']}")
    
    # Запрос API ключа
    api_key = input("\nВведите ваш Google API ключ: ").strip()
    
    if not api_key or api_key == "ВАШ_GOOGLE_API_КЛЮЧ":
        print("⚠️  Необходимо указать действительный API ключ")
        return
    
    while True:
        print("\nВыберите действие:")
        print("  1. Поиск в конкретном городе")
        print("  0. Выход")
        
        choice = input("\nВаш выбор (0-1): ").strip()
        
        if choice == "1":
            city_id = input("Введите ID города: ").strip().lower()
            if city_id:
                search_city(api_key, city_id)
        
        elif choice == "0":
            print("\n👋 До свидания!")
            break
            
        else:
            print("⚠️  Неверный выбор")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
