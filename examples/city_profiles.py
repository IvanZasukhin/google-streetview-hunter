#!/usr/bin/env python3
"""
Примеры профилей городов для StreetViewHunter.
"""

import yaml
import os
from streetview_hunter import StreetViewHunter


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
    },
    
    "санкт-петербург": {
        "name": "Санкт-Петербург",
        "bounds": {
            "lat_min": 59.93,
            "lat_max": 59.96,
            "lon_min": 30.30,
            "lon_max": 30.35
        },
        "search_params": {
            "step_km": 0.12,
            "search_radius": 60,
            "max_points": 1200,
            "delay": 0.03
        },
        "description": "Центр Санкт-Петербурга"
    },
    
    "казань": {
        "name": "Казань",
        "bounds": {
            "lat_min": 55.78,
            "lat_max": 55.82,
            "lon_min": 49.10,
            "lon_max": 49.15
        },
        "search_params": {
            "step_km": 0.14,
            "search_radius": 70,
            "max_points": 1000,
            "delay": 0.03
        },
        "description": "Столица Татарстана"
    },
    
    "малый_город": {
        "name": "Малый город (шаблон)",
        "bounds": {
            "lat_min": 55.00,
            "lat_max": 55.03,
            "lon_min": 82.00,
            "lon_max": 82.03
        },
        "search_params": {
            "step_km": 0.08,
            "search_radius": 40,
            "max_points": 500,
            "delay": 0.04
        },
        "description": "Шаблон для малых городов"
    }
}


def save_city_profiles():
    """Сохраняет профили городов в YAML файлы."""
    
    # Создаём папку configs если её нет
    os.makedirs("configs", exist_ok=True)
    
    for city_id, profile in CITY_PROFILES.items():
        filename = f"configs/{city_id}.yaml"
        
        # Добавляем секцию output
        full_profile = profile.copy()
        full_profile["output"] = {
            "filename": f"{city_id}_панорамы.txt",
            "format": "google.de"
        }
        
        # Сохраняем в файл
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(full_profile, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Сохранён профиль: {filename}")
    
    print(f"\n📁 Все профили сохранены в папку configs/")


def search_city(api_key: str, city_id: str):
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


def batch_search(api_key: str, city_ids: list):
    """Пакетный поиск в нескольких городах."""
    
    print(f"\n{'='*60}")
    print(f"🔍 ПАКЕТНЫЙ ПОИСК ({len(city_ids)} городов)")
    print(f"{'='*60}")
    
    total_panoramas = 0
    
    for city_id in city_ids:
        if city_id in CITY_PROFILES:
            print(f"\n📍 {CITY_PROFILES[city_id]['name']}...")
            
            try:
                stats = search_city(api_key, city_id)
                if stats:
                    total_panoramas += stats.get('total', 0)
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        else:
            print(f"   ⚠️  Город '{city_id}' пропущен (профиль не найден)")
    
    print(f"\n{'='*60}")
    print(f"📊 ИТОГО ПО ВСЕМ ГОРОДАМ: {total_panoramas} панорам")
    print(f"{'='*60}")


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
        print("  1. Сохранить профили городов в YAML файлы")
        print("  2. Поиск в конкретном городе")
        print("  3. Пакетный поиск по всем городам")
        print("  4. Пакетный поиск по выбранным городам")
        print("  0. Выход")
        
        choice = input("\nВаш выбор (0-4): ").strip()
        
        if choice == "1":
            save_city_profiles()
            
        elif choice == "2":
            city_id = input("Введите ID города: ").strip().lower()
            if city_id:
                search_city(api_key, city_id)
            
        elif choice == "3":
            # Все города
            batch_search(api_key, list(CITY_PROFILES.keys()))
            
        elif choice == "4":
            # Выбранные города
            print("Введите ID городов через запятую:")
            print("Пример: сыктывкар, москва_центр, казань")
            cities_input = input("Города: ").strip()
            
            if cities_input:
                city_ids = [c.strip().lower() for c in cities_input.split(',')]
                batch_search(api_key, city_ids)
            
        elif choice == "0":
            print("\n👋 До свидания!")
            break
            
        else:
            print("⚠️  Неверный выбор")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
