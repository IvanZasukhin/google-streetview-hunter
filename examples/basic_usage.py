#!/usr/bin/env python3
"""
Базовые примеры использования StreetViewHunter.
"""

import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from streetview_hunter import StreetViewHunter


def example_syktyvkar():
    """Пример для Сыктывкара."""
    print("=" * 60)
    print("Пример 1: Сыктывкар (центр города)")
    print("=" * 60)
    
    # Инициализация (замените API_KEY на ваш ключ)
    API_KEY = "ВАШ_GOOGLE_API_КЛЮЧ"
    
    if API_KEY == "ВАШ_GOOGLE_API_КЛЮЧ":
        print("⚠️  Замените API_KEY на ваш настоящий ключ Google Cloud API")
        return
    
    hunter = StreetViewHunter(API_KEY)
    
    # Поиск в центре города
    stats = hunter.search_area(
        lat_min=61.66,      # Южная граница
        lat_max=61.69,      # Северная граница
        lon_min=50.81,      # Западная граница
        lon_max=50.86,      # Восточная граница
        step_km=0.12,       # Шаг ~130 метров
        search_radius=50,   # Радиус поиска 50 метров
        max_points=800,     # Проверить не более 800 точек
        output_file="сыктывкар_центр_панорамы.txt",
        delay=0.03          # Задержка 0.03 сек между запросами
    )
    
    print(f"\n🎯 Результат: {stats['total']} панорам")
    return stats


def example_syktyvkar_extended():
    """Пример для расширенной области Сыктывкара."""
    print("\n" + "=" * 60)
    print("Пример 2: Сыктывкар (вся территория)")
    print("=" * 60)
    
    API_KEY = "ВАШ_GOOGLE_API_КЛЮЧ"
    
    if API_KEY == "ВАШ_GOOGLE_API_КЛЮЧ":
        print("⚠️  Замените API_KEY на ваш настоящий ключ")
        return
    
    hunter = StreetViewHunter(API_KEY)
    
    # Поиск по всей территории города
    stats = hunter.search_area(
        lat_min=61.64,      # Эжва
        lat_max=61.70,      # Дырнос
        lon_min=50.78,      # Западные районы
        lon_max=50.90,      # Восточные районы
        step_km=0.18,       # Более редкая сетка
        search_radius=70,   # Больший радиус поиска
        max_points=1500,    # Больше точек
        output_file="сыктывкар_полный_панорамы.txt",
        delay=0.02          # Чуть быстрее
    )
    
    print(f"\n🎯 Результат: {stats['total']} панорам")
    return stats


def example_custom_city():
    """Пример для произвольного города."""
    print("\n" + "=" * 60)
    print("Пример 3: Произвольный город")
    print("=" * 60)
    
    API_KEY = "ВАШ_GOOGLE_API_КЛЮЧ"
    
    if API_KEY == "ВАШ_GOOGLE_API_КЛЮЧ":
        print("⚠️  Замените API_KEY на ваш настоящий ключ")
        return
    
    hunter = StreetViewHunter(API_KEY)
    
    # Параметры для вашего города
    city_name = input("Введите название города: ").strip()
    
    if not city_name:
        city_name = "мой_город"
    
    # Запрос координат
    print("\nВведите координаты области поиска:")
    try:
        lat_min = float(input("  Минимальная широта: ") or "55.75")
        lat_max = float(input("  Максимальная широта: ") or "55.78")
        lon_min = float(input("  Минимальная долгота: ") or "37.60")
        lon_max = float(input("  Максимальная долгота: ") or "37.65")
    except ValueError:
        print("⚠️  Неверный формат координат. Использую значения по умолчанию.")
        lat_min, lat_max, lon_min, lon_max = 55.75, 55.78, 37.60, 37.65
    
    # Автоподбор параметров на основе размера области
    from streetview_hunter.utils import calculate_area_size
    width_km, height_km = calculate_area_size(lat_min, lat_max, lon_min, lon_max)
    
    # Автоматический подбор шага
    if width_km * height_km > 100:  # Очень большая область
        step_km = 0.25
        search_radius = 100
    elif width_km * height_km > 25:  # Большая область
        step_km = 0.18
        search_radius = 80
    else:  # Небольшая область
        step_km = 0.12
        search_radius = 50
    
    print(f"\n📏 Размер области: {width_km:.1f} × {height_km:.1f} км")
    print(f"⚙️  Автоматически выбрано: шаг={step_km}км, радиус={search_radius}м")
    
    stats = hunter.search_area(
        lat_min=lat_min,
        lat_max=lat_max,
        lon_min=lon_min,
        lon_max=lon_max,
        step_km=step_km,
        search_radius=search_radius,
        max_points=1000,
        output_file=f"{city_name}_панорамы.txt"
    )
    
    print(f"\n🎯 Результат для {city_name}: {stats['total']} панорам")
    return stats


def example_api_test():
    """Тест API ключа."""
    print("\n" + "=" * 60)
    print("Пример 4: Тестирование API ключа")
    print("=" * 60)
    
    API_KEY = input("Введите ваш Google API ключ: ").strip()
    
    if not API_KEY:
        print("⚠️  Ключ не введён")
        return
    
    import requests
    
    # Тестовый запрос
    test_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    params = {
        "location": "61.668742,50.835369",  # Центр Сыктывкара
        "radius": 50,
        "key": API_KEY
    }
    
    print("\n🔍 Тестирую API ключ...")
    
    try:
        response = requests.get(test_url, params=params, timeout=10)
        data = response.json()
        
        print(f"Статус: {data.get('status')}")
        
        if data.get("status") == "OK":
            print("✅ API ключ рабочий!")
            print(f"  ID панорамы: {data.get('pano_id', '')[:30]}...")
            print(f"  Координаты: {data.get('location', {}).get('lat')}, "
                  f"{data.get('location', {}).get('lng')}")
            print(f"  Дата съёмки: {data.get('date', 'неизвестно')}")
            return True
        else:
            print(f"❌ Проблема с API ключом: {data.get('status')}")
            print(f"  Сообщение: {data.get('error_message', 'нет информации')}")
            
            if data.get("status") == "REQUEST_DENIED":
                print("  Возможные причины:")
                print("    1. Ключ неверный")
                print("    2. Street View Static API не активирован")
                print("    3. Неправильные настройки API ключа")
            
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def main():
    """Основная функция примера."""
    print("🗺️  GOOGLE STREET VIEW HUNTER - Примеры использования")
    print("=" * 60)
    
    while True:
        print("\nВыберите пример:")
        print("  1. Сыктывкар (центр города)")
        print("  2. Сыктывкар (вся территория)")
        print("  3. Произвольный город")
        print("  4. Тестирование API ключа")
        print("  0. Выход")
        
        choice = input("\nВаш выбор (0-4): ").strip()
        
        if choice == "1":
            example_syktyvkar()
        elif choice == "2":
            example_syktyvkar_extended()
        elif choice == "3":
            example_custom_city()
        elif choice == "4":
            example_api_test()
        elif choice == "0":
            print("\n👋 До свидания!")
            break
        else:
            print("⚠️  Неверный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
