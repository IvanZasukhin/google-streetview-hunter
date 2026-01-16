#!/usr/bin/env python3
"""
Google Street View Hunter - Консольный интерфейс
Универсальный инструмент для поиска панорам в любом городе.
"""

import sys
import os
import math
import json
from datetime import datetime

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from streetview_hunter.core import StreetViewHunter
except ImportError:
    print("❌ Ошибка: Модуль streetview_hunter не найден.")
    print("Решение 1: Установите пакет: pip install -e .")
    print("Решение 2: Запускайте из корня проекта: python examples/basic_usage.py")
    sys.exit(1)


class StreetViewHunterConsole:
    """Консольный интерфейс для StreetViewHunter."""
    
    def __init__(self):
        self.api_key = None
        self.hunter = None
        self.config = {}
        
    def clear_screen(self):
        """Очищает экран консоли."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Печатает заголовок."""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def get_api_key(self):
        """Запрашивает и проверяет API ключ."""
        self.print_header("НАСТРОЙКА API КЛЮЧА")
        
        print("\n🔑 Для работы нужен Google Cloud API ключ с активированным Street View Static API")
        print("📋 Получить ключ: https://console.cloud.google.com/")
        print("  1. Создайте проект")
        print("  2. Активируйте 'Street View Static API'")
        print("  3. Создайте ключ в разделе 'Credentials'")
        print("-"*60)
        
        while True:
            api_key = input("\nВведите ваш Google API ключ: ").strip()
            
            if not api_key:
                print("⚠️  Ключ не может быть пустым. Попробуйте снова.")
                continue
            
            # Проверяем базовый формат ключа
            if len(api_key) < 20:
                print("⚠️  Ключ слишком короткий. Возможно, он неверный.")
                choice = input("Продолжить с этим ключом? (y/n): ").lower()
                if choice != 'y':
                    continue
            
            # Тестируем ключ
            if self.test_api_key(api_key):
                self.api_key = api_key
                self.hunter = StreetViewHunter(api_key)
                print("✅ API ключ сохранен!")
                return True
            else:
                print("\n❌ Ключ не прошел проверку.")
                choice = input("Попробовать другой ключ? (y/n): ").lower()
                if choice != 'y':
                    return False
    
    def test_api_key(self, api_key):
        """Тестирует API ключ."""
        import requests
        
        print("\n🔍 Тестирую API ключ...")
        
        # Тестовые локации для проверки
        test_locations = [
            ("55.7558,37.6173", "Москва (Красная площадь)"),
            ("40.7128,-74.0060", "Нью-Йорк"),
            ("48.8566,2.3522", "Париж"),
        ]
        
        for location, name in test_locations:
            url = "https://maps.googleapis.com/maps/api/streetview/metadata"
            params = {
                "location": location,
                "radius": 100,
                "key": api_key
            }
            
            try:
                response = requests.get(url, params=params, timeout=5)
                data = response.json()
                
                if data.get("status") == "OK":
                    print(f"  ✅ {name}: найдены панорамы")
                    return True
                elif data.get("status") == "ZERO_RESULTS":
                    print(f"  ⚠️  {name}: нет панорам (но API работает)")
                    # API работает, просто нет панорам в этом месте
                else:
                    print(f"  ❌ {name}: {data.get('status')}")
            
            except Exception:
                continue
        
        # Если ни один тест не прошел
        print("⚠️  Не удалось подтвердить работу API. Проверьте ключ вручную.")
        return True  # Все равно продолжаем, возможно локальные ограничения
    
    def get_city_parameters(self):
        """Запрашивает параметры для поиска."""
        self.print_header("НАСТРОЙКА ПАРАМЕТРОВ ПОИСКА")
        
        print("\n📍 Введите координаты области поиска:")
        print("   Пример: 55.7558 (широта), 37.6173 (долгота)")
        print("-"*60)
        
        # Получаем координаты
        try:
            lat_min = float(input("Минимальная широта (юг): ") or "55.75")
            lat_max = float(input("Максимальная широта (север): ") or "55.78")
            lon_min = float(input("Минимальная долгота (запад): ") or "37.60")
            lon_max = float(input("Максимальная долгота (восток): ") or "37.65")
        except ValueError:
            print("❌ Неверный формат координат. Использую значения по умолчанию.")
            lat_min, lat_max, lon_min, lon_max = 55.75, 55.78, 37.60, 37.65
        
        # Рассчитываем размер области
        width_km, height_km = self.calculate_area_size(lat_min, lat_max, lon_min, lon_max)
        area_size = width_km * height_km
        
        print(f"\n📏 Размер области: {width_km:.1f} × {height_km:.1f} км")
        print(f"   Площадь: {area_size:.1f} кв. км")
        
        # Рекомендуем параметры на основе размера
        if area_size > 100:
            rec_step = 0.25
            rec_radius = 100
            rec_points = 2000
            city_type = "ОЧЕНЬ БОЛЬШОЙ город"
        elif area_size > 25:
            rec_step = 0.18
            rec_radius = 80
            rec_points = 1500
            city_type = "БОЛЬШОЙ город"
        elif area_size > 5:
            rec_step = 0.12
            rec_radius = 60
            rec_points = 800
            city_type = "СРЕДНИЙ город"
        else:
            rec_step = 0.08
            rec_radius = 40
            rec_points = 300
            city_type = "МАЛЕНЬКИЙ город"
        
        print(f"🏙️  Рекомендация для {city_type}:")
        print(f"  • Шаг сетки: {rec_step} км")
        print(f"  • Радиус поиска: {rec_radius} м")
        print(f"  • Макс. точек: {rec_points}")
        print("-"*60)
        
        # Параметры поиска
        print("\n⚙️  Настройте параметры поиска:")
        print("   (нажмите Enter для использования рекомендаций)")
        
        step_km = input(f"Шаг сетки в км [{rec_step}]: ").strip()
        step_km = float(step_km) if step_km else rec_step
        
        search_radius = input(f"Радиус поиска в метрах [{rec_radius}]: ").strip()
        search_radius = int(search_radius) if search_radius else rec_radius
        
        max_points = input(f"Макс. точек для проверки [{rec_points}]: ").strip()
        max_points = int(max_points) if max_points else rec_points
        
        # Дополнительные параметры
        print("\n📊 Дополнительные настройки:")
        delay = input("Задержка между запросами (сек) [0.03]: ").strip()
        delay = float(delay) if delay else 0.03
        
        city_name = input("Название города (для имени файла): ").strip()
        if not city_name:
            city_name = f"город_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        output_file = input(f"Имя выходного файла [{city_name}_панорамы.txt]: ").strip()
        if not output_file:
            output_file = f"{city_name}_панорамы.txt"
        
        # Сохраняем конфигурацию
        self.config = {
            'bounds': {
                'lat_min': lat_min,
                'lat_max': lat_max,
                'lon_min': lon_min,
                'lon_max': lon_max,
            },
            'search_params': {
                'step_km': step_km,
                'search_radius': search_radius,
                'max_points': max_points,
                'delay': delay,
            },
            'output': {
                'filename': output_file,
                'city_name': city_name,
            },
            'area_info': {
                'width_km': width_km,
                'height_km': height_km,
                'area_km2': area_size,
                'city_type': city_type,
            }
        }
        
        return True
    
    def calculate_area_size(self, lat_min, lat_max, lon_min, lon_max):
        """Рассчитывает размер области в километрах."""
        avg_lat = (lat_min + lat_max) / 2
        km_per_degree_lat = 111.0
        km_per_degree_lon = 111.0 * math.cos(math.radians(avg_lat))
        
        width_km = (lon_max - lon_min) * km_per_degree_lon
        height_km = (lat_max - lat_min) * km_per_degree_lat
        
        return width_km, height_km
    
    def show_config_summary(self):
        """Показывает сводку конфигурации."""
        self.print_header("СВОДКА НАСТРОЕК")
        
        bounds = self.config['bounds']
        params = self.config['search_params']
        area = self.config['area_info']
        output = self.config['output']
        
        print(f"\n📍 Область поиска:")
        print(f"   Широта:  {bounds['lat_min']:.5f} → {bounds['lat_max']:.5f}")
        print(f"   Долгота: {bounds['lon_min']:.5f} → {bounds['lon_max']:.5f}")
        print(f"   Размер:  {area['width_km']:.1f} × {area['height_km']:.1f} км")
        print(f"   Площадь: {area['area_km2']:.1f} кв. км")
        print(f"   Тип:     {area['city_type']}")
        
        print(f"\n⚙️  Параметры поиска:")
        print(f"   Шаг сетки:     {params['step_km']} км (~{params['step_km']*1000:.0f} м)")
        print(f"   Радиус поиска: {params['search_radius']} м")
        print(f"   Макс. точек:   {params['max_points']}")
        print(f"   Задержка:      {params['delay']} сек")
        
        # Оцениваем количество точек
        points_count = self.estimate_points_count(
            bounds['lat_min'], bounds['lat_max'],
            bounds['lon_min'], bounds['lon_max'],
            params['step_km']
        )
        actual_points = min(points_count, params['max_points'])
        
        print(f"\n📊 Прогноз:")
        print(f"   Всего точек в сетке:   {points_count}")
        print(f"   Будет проверено:       {actual_points}")
        print(f"   Ориентировочное время: {actual_points * params['delay'] / 60:.1f} мин")
        
        print(f"\n💾 Выходные данные:")
        print(f"   Город:          {output['city_name']}")
        print(f"   Файл:           {output['filename']}")
        
        return True
    
    def estimate_points_count(self, lat_min, lat_max, lon_min, lon_max, step_km):
        """Оценивает количество точек в сетке."""
        width_km, height_km = self.calculate_area_size(lat_min, lat_max, lon_min, lon_max)
        
        points_x = int(width_km / step_km) + 1
        points_y = int(height_km / step_km) + 1
        
        return points_x * points_y
    
    def start_search(self):
        """Запускает поиск панорам."""
        if not self.config:
            print("❌ Сначала настройте параметры поиска!")
            return
        
        self.print_header("ЗАПУСК ПОИСКА ПАНОРАМ")
        
        bounds = self.config['bounds']
        params = self.config['search_params']
        output = self.config['output']
        
        print("\n⏱️  Запускаю поиск...")
        print("   (для отмены нажмите Ctrl+C)")
        print("-"*60)
        
        try:
            # Запускаем поиск
            stats = self.hunter.search_area(
                lat_min=bounds['lat_min'],
                lat_max=bounds['lat_max'],
                lon_min=bounds['lon_min'],
                lon_max=bounds['lon_max'],
                step_km=params['step_km'],
                search_radius=params['search_radius'],
                max_points=params['max_points'],
                output_file=output['filename'],
                delay=params['delay']
            )
            
            # Сохраняем конфигурацию
            self.save_config_to_file(stats)
            
            return stats
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Поиск прерван пользователем")
            return None
        except Exception as e:
            print(f"\n❌ Ошибка при поиске: {e}")
            return None
    
    def save_config_to_file(self, stats):
        """Сохраняет конфигурацию и результаты в файл."""
        if not self.config:
            return
        
        config_file = f"{self.config['output']['city_name']}_config.json"
        
        save_data = {
            'config': self.config,
            'search_date': datetime.now().isoformat(),
            'results': {
                'total_panoramas': stats.get('total', 0) if stats else 0,
                'output_file': self.config['output']['filename'],
                'csv_file': stats.get('csv_file', '') if stats else '',
            },
            'api_info': {
                'key_used': self.api_key[:10] + '...' if self.api_key else 'не указан',
                'requests_made': self.hunter.request_count if self.hunter else 0,
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Конфигурация сохранена в: {config_file}")
            
        except Exception as e:
            print(f"⚠️  Не удалось сохранить конфигурацию: {e}")
    
    def quick_search_menu(self):
        """Меню быстрого поиска с предустановками."""
        self.print_header("БЫСТРЫЙ ПОИСК")
        
        presets = {
            '1': {
                'name': 'Малый город',
                'step_km': 0.08,
                'radius': 40,
                'points': 500,
                'delay': 0.04,
            },
            '2': {
                'name': 'Средний город',
                'step_km': 0.12,
                'radius': 60,
                'points': 1000,
                'delay': 0.03,
            },
            '3': {
                'name': 'Большой город',
                'step_km': 0.18,
                'radius': 80,
                'points': 1500,
                'delay': 0.03,
            },
            '4': {
                'name': 'Мегаполис',
                'step_km': 0.25,
                'radius': 100,
                'points': 2000,
                'delay': 0.02,
            },
        }
        
        print("\n🎯 Выберите тип города:")
        for key, preset in presets.items():
            print(f"  {key}. {preset['name']}")
            print(f"     • Шаг: {preset['step_km']} км")
            print(f"     • Радиус: {preset['radius']} м")
            print(f"     • Точки: {preset['points']}")
            print()
        
        choice = input("Ваш выбор (1-4): ").strip()
        
        if choice in presets:
            preset = presets[choice]
            
            print(f"\n🏙️  Выбран тип: {preset['name']}")
            
            # Запрашиваем только координаты и название
            city_name = input("Название города: ").strip()
            if not city_name:
                city_name = preset['name'].replace(' ', '_').lower()
            
            print("\n📍 Введите координаты центра города:")
            try:
                center_lat = float(input("  Широта центра: ") or "55.75")
                center_lon = float(input("  Долгота центра: ") or "37.62")
            except ValueError:
                print("⚠️  Неверный формат. Использую Москву по умолчанию.")
                center_lat, center_lon = 55.75, 37.62
            
            # Автоматически задаем область вокруг центра
            # Примерно 5x5 км для малого города, 10x10 для среднего и т.д.
            size_factor = 2.5 + (float(choice) * 2.5)  # 5, 7.5, 10, 12.5 км радиус
            
            self.config = {
                'bounds': {
                    'lat_min': center_lat - (size_factor / 111.0),
                    'lat_max': center_lat + (size_factor / 111.0),
                    'lon_min': center_lon - (size_factor / (111.0 * math.cos(math.radians(center_lat)))),
                    'lon_max': center_lon + (size_factor / (111.0 * math.cos(math.radians(center_lat)))),
                },
                'search_params': {
                    'step_km': preset['step_km'],
                    'search_radius': preset['radius'],
                    'max_points': preset['points'],
                    'delay': preset['delay'],
                },
                'output': {
                    'filename': f"{city_name}_панорамы.txt",
                    'city_name': city_name,
                }
            }
            
            # Рассчитываем информацию об области
            width_km, height_km = self.calculate_area_size(
                self.config['bounds']['lat_min'],
                self.config['bounds']['lat_max'],
                self.config['bounds']['lon_min'],
                self.config['bounds']['lon_max']
            )
            
            self.config['area_info'] = {
                'width_km': width_km,
                'height_km': height_km,
                'area_km2': width_km * height_km,
                'city_type': preset['name'],
            }
            
            return True
        else:
            print("❌ Неверный выбор")
            return False
    
    def main_menu(self):
        """Главное меню программы."""
        while True:
            self.clear_screen()
            self.print_header("GOOGLE STREET VIEW HUNTER")
            
            print("\n🏠 ГЛАВНОЕ МЕНЮ")
            print("="*60)
            
            # Показываем текущий статус
            if self.api_key:
                print(f"🔑 API ключ: {'✓ Установлен'}")
            else:
                print(f"🔑 API ключ: {'✗ Не установлен'}")
            
            if self.config:
                city = self.config.get('output', {}).get('city_name', 'Не задан')
                print(f"📍 Город: {city}")
            
            print("\n1. 📝 Установить/сменить API ключ")
            print("2. ⚙️  Настроить параметры поиска (ручная настройка)")
            print("3. 🎯 Быстрый поиск (предустановки)")
            print("4. 👁️  Показать текущие настройки")
            print("5. 🚀 Запустить поиск панорам")
            print("6. 💾 Сохранить конфигурацию в файл")
            print("7. 📖 Помощь и документация")
            print("0. 🚪 Выход")
            print("-"*60)
            
            choice = input("\nВаш выбор (0-7): ").strip()
            
            if choice == "1":
                self.get_api_key()
                input("\nНажмите Enter чтобы продолжить...")
            
            elif choice == "2":
                if not self.api_key:
                    print("❌ Сначала установите API ключ!")
                    input("\nНажмите Enter чтобы продолжить...")
                    continue
                
                if self.get_city_parameters():
                    self.show_config_summary()
                input("\nНажмите Enter чтобы продолжить...")
            
            elif choice == "3":
                if not self.api_key:
                    print("❌ Сначала установите API ключ!")
                    input("\nНажмите Enter чтобы продолжить...")
                    continue
                
                if self.quick_search_menu():
                    self.show_config_summary()
                input("\nНажмите Enter чтобы продолжить...")
            
            elif choice == "4":
                if self.config:
                    self.show_config_summary()
                else:
                    print("❌ Настройки не заданы. Сначала настройте параметры.")
                input("\nНажмите Enter чтобы продолжить...")
            
            elif choice == "5":
                if not self.api_key:
                    print("❌ Сначала установите API ключ!")
                elif not self.config:
                    print("❌ Сначала настройте параметры поиска!")
                else:
                    stats = self.start_search()
                    if stats:
                        print(f"\n✅ Поиск завершен! Найдено {stats.get('total', 0)} панорам.")
                        print(f"📁 Результаты сохранены в:")
                        print(f"   • {self.config['output']['filename']}")
                        if stats.get('csv_file'):
                            print(f"   • {stats['csv_file']}")
                
                input("\nНажмите Enter чтобы продолжить...")
            
            elif choice == "6":
                if self.config:
                    self.save_config_to_file(None)
                else:
                    print("❌ Нет настроек для сохранения.")
                input("\nНажмите Enter чтобы продолжить...")
            
            elif choice == "7":
                self.show_help()
                input("\nНажмите Enter чтобы продолжить...")
            
            elif choice == "0":
                print("\n👋 До свидания! Спасибо за использование StreetViewHunter!")
                break
            
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                input("\nНажмите Enter чтобы продолжить...")
    
    def show_help(self):
        """Показывает справку."""
        self.print_header("ПОМОЩЬ И ДОКУМЕНТАЦИЯ")
        
        print("\n📚 КАК ПОЛЬЗОВАТЬСЯ:")
        print("1. 🔑 Получите API ключ на https://console.cloud.google.com/")
        print("2. 📍 Укажите координаты области поиска")
        print("3. ⚙️  Настройте параметры (или используйте быстрый поиск)")
        print("4. 🚀 Запустите поиск")
        print("5. 💾 Получите файлы со ссылками на панорамы")
        
        print("\n⚙️  РЕКОМЕНДАЦИИ ПО ПАРАМЕТРАМ:")
        print("• Шаг сетки: 0.08-0.25 км (чем мельче шаг, тем больше точек)")
        print("• Радиус поиска: 30-100 м (чем больше радиус, тем больше шансов найти панорамы)")
        print("• Макс. точек: зависит от размера города")
        print("• Задержка: 0.03-0.05 сек (чтобы не превысить лимиты API)")
        
        print("\n⚠️  ВАЖНО:")
        print("• Бесплатный лимит Google: 28,000 запросов в месяц")
        print("• Street View есть не во всех городах")
        print("• Для коммерческого использования нужен платный тариф")
        
        print("\n📞 ПОДДЕРЖКА:")
        print("• GitHub: https://github.com/IvanZasukhin/google-streetview-hunter")
        print("• Email: ivanzasukhin11@gmail.com")


def main():
    """Основная функция."""
    app = StreetViewHunterConsole()
    app.main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
