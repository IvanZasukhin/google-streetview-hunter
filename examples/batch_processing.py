#!/usr/bin/env python3
"""
Пример пакетной обработки для StreetViewHunter.
"""

import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streetview_hunter.core import StreetViewHunter


def main():
    """Простой пример пакетной обработки."""
    
    print("🏙️  ПАКЕТНАЯ ОБРАБОТКА STREETVIEWHUNTER")
    print("=" * 60)
    
    # Запрос API ключа
    api_key = input("Введите ваш Google API ключ: ").strip()
    
    if not api_key or api_key == "ВАШ_GOOGLE_API_КЛЮЧ":
        print("⚠️  Необходимо указать действительный API ключ")
        return
    
    print("\nВыберите города для обработки:")
    print("1. Сыктывкар")
    print("2. Москва (центр)")
    print("3. Оба города")
    
    choice = input("\nВаш выбор (1-3): ").strip()
    
    cities_to_process = []
    
    if choice == "1":
        cities_to_process.append("сыктывкар")
    elif choice == "2":
        cities_to_process.append("москва_центр")
    elif choice == "3":
        cities_to_process.extend(["сыктывкар", "москва_центр"])
    else:
        print("⚠️  Неверный выбор")
        return
    
    total_panoramas = 0
    
    for city in cities_to_process:
        print(f"\n{'='*60}")
        print(f"🔍 Обрабатываю: {city}")
        print(f"{'='*60}")
        
        hunter = StreetViewHunter(api_key)
        
        if city == "сыктывкар":
            stats = hunter.search_area(
                lat_min=61.66,
                lat_max=61.69,
                lon_min=50.81,
                lon_max=50.86,
                step_km=0.12,
                search_radius=50,
                output_file="сыктывкар_панорамы.txt"
            )
        elif city == "москва_центр":
            stats = hunter.search_area(
                lat_min=55.75,
                lat_max=55.78,
                lon_min=37.60,
                lon_max=37.65,
                step_km=0.15,
                search_radius=80,
                output_file="москва_центр_панорамы.txt"
            )
        
        total_panoramas += stats.get('total', 0)
    
    print(f"\n{'='*60}")
    print(f"📊 ИТОГО: {total_panoramas} панорам")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
