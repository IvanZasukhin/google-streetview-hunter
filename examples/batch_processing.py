#!/usr/bin/env python3
"""
Пример пакетной обработки для StreetViewHunter.
"""

import sys
import os
import yaml
import json
from datetime import datetime
from typing import List, Dict, Any

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from streetview_hunter import StreetViewHunter


class BatchProcessor:
    """
    Класс для пакетной обработки нескольких областей.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.results = []
        self.stats = {
            "total_cities": 0,
            "total_panoramas": 0,
            "successful_cities": 0,
            "failed_cities": 0,
            "start_time": None,
            "end_time": None
        }
    
    def process_config_file(self, config_path: str) -> Dict[str, Any]:
        """
        Обрабатывает один конфигурационный файл.
        
        Args:
            config_path: Путь к YAML-конфигурации
            
        Returns:
            Результаты обработки
        """
        print(f"\n📁 Загружаю конфигурацию: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            city_name = config.get('name', 'Неизвестный город')
            print(f"📍 Город: {city_name}")
            
            # Создаём нового охотника для каждого города
            # (чтобы не было дубликатов между городами)
            hunter = StreetViewHunter(self.api_key)
            
            # Запускаем поиск
            result = hunter.search_from_config(config)
            
            # Добавляем информацию о городе
            result['city_name'] = city_name
            result['config_file'] = config_path
            
            self.results.append(result)
            self.stats['successful_cities'] += 1
            self.stats['total_panoramas'] += result.get('total', 0)
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка обработки {config_path}: {e}")
            self.stats['failed_cities'] += 1
            
            return {
                'city_name': os.path.basename(config_path),
                'error': str(e),
                'total': 0
            }
    
    def process_directory(self, config_dir: str):
        """
        Обрабатывает все конфигурационные файлы в директории.
        
        Args:
            config_dir: Путь к директории с конфигами
        """
        print(f"\n🔍 Начинаю пакетную обработку из: {config_dir}")
        
        # Получаем список YAML файлов
        config_files = []
        for file in os.listdir(config_dir):
            if file.endswith('.yaml') or file.endswith('.yml'):
                config_files.append(os.path.join(config_dir, file))
        
        self.stats['total_cities'] = len(config_files)
        self.stats['start_time'] = datetime.now().isoformat()
        
        print(f"📊 Всего городов для обработки: {len(config_files)}")
        
        # Обрабатываем каждый файл
        for i, config_file in enumerate(config_files, 1):
            print(f"\n{'='*60}")
            print(f"Город {i}/{len(config_files)}")
            print(f"{'='*60}")
            
            self.process_config_file(config_file)
        
        # Завершение
        self.stats['end_time'] = datetime.now().isoformat()
        
        # Сохраняем сводный отчёт
        self.save_summary_report()
    
    def process_city_list(self, city_configs: List[Dict[str, Any]]):
        """
        Обрабатывает список конфигураций городов.
        
        Args:
            city_configs: Список конфигураций городов
        """
        print(f"\n🔍 Начинаю пакетную обработку списка городов")
        
        self.stats['total_cities'] = len(city_configs)
        self.stats['start_time'] = datetime.now().isoformat()
        
        print(f"📊 Всего городов для обработки: {len(city_configs)}")
        
        for i, config in enumerate(city_configs, 1):
            print(f"\n{'='*60}")
            print(f"Город {i}/{len(city_configs)}: {config.get('name', 'Неизвестный')}")
            print(f"{'='*60}")
            
            try:
                hunter = StreetViewHunter(self.api_key)
                result = hunter.search_from_config(config)
                
                result['city_name'] = config.get('name', 'Неизвестный')
                self.results.append(result)
                self.stats['successful_cities'] += 1
                self.stats['total_panoramas'] += result.get('total', 0)
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                self.stats['failed_cities'] += 1
        
        # Завершение
        self.stats['end_time'] = datetime.now().isoformat()
        self.save_summary_report()
    
    def save_summary_report(self):
        """Сохраняет сводный отчёт по пакетной обработке."""
        report = {
            "batch_processing_summary": self.stats,
            "cities": self.results,
            "processing_date": datetime.now().isoformat()
        }
        
        # Имя файла с датой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"batch_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"📊 СВОДНЫЙ ОТЧЁТ")
        print(f"{'='*60}")
        print(f"Всего городов:        {self.stats['total_cities']}")
        print(f"Успешно обработано:   {self.stats['successful_cities']}")
        print(f"Ошибок:               {self.stats['failed_cities']}")
        print(f"Всего панорам:        {self.stats['total_panoramas']}")
        print(f"Отчёт сохранён в:     {report_file}")
        print(f"{'='*60}")
        
        # Также сохраняем краткий отчёт в TXT
        txt_report = f"""СВОДНЫЙ ОТЧЁТ ПАКЕТНОЙ ОБРАБОТКИ
Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Всего городов: {self.stats['total_cities']}
Успешно: {self.stats['successful_cities']}
Ошибок: {self.stats['failed_cities']}
Всего панорам: {self.stats['total_panoramas']}

Детальный отчёт: {report_file}
"""
        
        with open(f"summary_{timestamp}.txt", 'w', encoding='utf-8') as f:
            f.write(txt_report)


def main():
    """Основная функция пакетной обработки."""
    
    print("🏙️  ПАКЕТНАЯ ОБРАБОТКА STREETVIEWHUNTER")
    print("=" * 60)
    
    # Запрос API ключа
    api_key = input("Введите ваш Google API ключ: ").strip()
    
    if not api_key or api_key == "ВАШ_GOOGLE_API_КЛЮЧ":
        print("⚠️  Необходимо указать действительный API ключ")
        return
    
    processor = BatchProcessor(api_key)
    
    while True:
        print("\nВыберите режим пакетной обработки:")
        print("  1. Обработать все конфиги в папке configs/")
        print("  2. Обработать выбранные города из examples/city_profiles.py")
        print("  3. Создать тестовую пакетную обработку")
        print("  0. Выход")
        
        choice = input("\nВаш выбор (0-3): ").strip()
        
        if choice == "1":
            # Обработка папки configs
            config_dir = "configs"
            
            if not os.path.exists(config_dir):
                print(f"⚠️  Папка {config_dir} не найдена")
                print("   Сначала запустите examples/city_profiles.py для создания конфигов")
            else:
                processor.process_directory(config_dir)
        
        elif choice == "2":
            # Обработка выбранных городов
            from examples.city_profiles import CITY_PROFILES
            
            print("\nДоступные города:")
            for city_id, profile in CITY_PROFILES.items():
                print(f"  {city_id:20} - {profile['name']}")
            
            print("\nВведите ID городов через запятую:")
            print("Пример: сыктывкар, москва_центр, казань")
            cities_input = input("Города: ").strip()
            
            if cities_input:
                city_ids = [c.strip().lower() for c in cities_input.split(',')]
                
                # Собираем конфигурации выбранных городов
                selected_configs = []
                for city_id in city_ids:
                    if city_id in CITY_PROFILES:
                        config = CITY_PROFILES[city_id].copy()
                        config['output'] = {
                            'filename': f"{city_id}_панорамы.txt",
                            'format': 'google.de'
                        }
                        selected_configs.append(config)
                    else:
                        print(f"⚠️  Город '{city_id}' не найден, пропускаю")
                
                if selected_configs:
                    processor.process_city_list(selected_configs)
                else:
                    print("⚠️  Не выбрано ни одного города")
        
        elif choice == "3":
            # Тестовая обработка
            print("\n🔧 Тестовая пакетная обработка (2 маленьких города)")
            
            test_configs = [
                {
                    "name": "Тестовый город 1",
                    "bounds": {
                        "lat_min": 61.667,
                        "lat_max": 61.668,
                        "lon_min": 50.834,
                        "lon_max": 50.835
                    },
                    "search_params": {
                        "step_km": 0.05,
                        "search_radius": 30,
                        "max_points": 50,
                        "delay": 0.05
                    },
                    "output": {
                        "filename": "test_city_1.txt",
                        "format": "google.de"
                    }
                },
                {
                    "name": "Тестовый город 2",
                    "bounds": {
                        "lat_min": 61.669,
                        "lat_max": 61.670,
                        "lon_min": 50.836,
                        "lon_max": 50.837
                    },
                    "search_params": {
                        "step_km": 0.05,
                        "search_radius": 30,
                        "max_points": 50,
                        "delay": 0.05
                    },
                    "output": {
                        "filename": "test_city_2.txt",
                        "format": "google.de"
                    }
                }
            ]
            
            processor.process_city_list(test_configs)
        
        elif choice == "0":
            print("\n👋 До свидания!")
            break
        
        else:
            print("⚠️  Неверный выбор")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
