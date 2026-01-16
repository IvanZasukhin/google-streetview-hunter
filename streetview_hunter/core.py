"""
Основной модуль StreetViewHunter.
Содержит класс для поиска панорам Google Street View.
"""

import requests
import csv
import time
import math
from typing import List, Tuple, Dict, Optional, Any
from datetime import datetime


class StreetViewHunter:
    """
    Основной класс для поиска панорам Google Street View.
    
    Пример использования:
    >>> hunter = StreetViewHunter(api_key="ВАШ_КЛЮЧ")
    >>> stats = hunter.search_area(
    ...     lat_min=61.66, lat_max=61.69,
    ...     lon_min=50.81, lon_max=50.86,
    ...     step_km=0.12,
    ...     search_radius=50,
    ...     output_file="панорамы.txt"
    ... )
    """
    
    def __init__(self, api_key: str):
        """
        Инициализация охотника за панорамами.
        
        Args:
            api_key: Ключ Google Cloud API с доступом к Street View Static API
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.found_panos = {}  # pano_id -> данные панорамы
        self.request_count = 0
        self.start_time = None
        
    def search_area(self, 
                   lat_min: float, lat_max: float,
                   lon_min: float, lon_max: float,
                   step_km: float = 0.15,
                   search_radius: int = 50,
                   max_points: int = 1000,
                   output_file: str = "panoramas.txt",
                   delay: float = 0.03) -> Dict[str, Any]:
        """
        Поиск панорам в указанной области.
        
        Args:
            lat_min: Минимальная широта
            lat_max: Максимальная широта
            lon_min: Минимальная долгота
            lon_max: Максимальная долгота
            step_km: Шаг сетки в километрах (рекомендуется 0.1-0.3)
            search_radius: Радиус поиска в метрах (рекомендуется 30-100)
            max_points: Максимальное количество точек для проверки
            output_file: Имя выходного файла
            delay: Задержка между запросами в секундах
            
        Returns:
            Словарь со статистикой поиска
        """
        # Начало работы
        self.start_time = time.time()
        print(f"\n{'='*60}")
        print(f"🔍 GOOGLE STREET VIEW HUNTER v1.0")
        print(f"{'='*60}")
        print(f"Область поиска:")
        print(f"  Широта:  {lat_min:.5f} → {lat_max:.5f}")
        print(f"  Долгота: {lon_min:.5f} → {lon_max:.5f}")
        print(f"  Размер:  {lat_max-lat_min:.3f}° × {lon_max-lon_min:.3f}°")
        print(f"Параметры:")
        print(f"  Шаг сетки:     {step_km} км (~{step_km*1000:.0f} м)")
        print(f"  Радиус поиска: {search_radius} м")
        print(f"  Макс. точек:   {max_points}")
        print(f"{'='*60}")
        
        # Генерация точек сетки
        points = self._generate_grid(
            lat_min, lat_max, lon_min, lon_max, step_km
        )
        
        # Ограничение количества точек
        if len(points) > max_points:
            print(f"⚠️  Ограничение: будет проверено {max_points} из {len(points)} точек")
            points = points[:max_points]
        
        print(f"📊 Точек для проверки: {len(points)}")
        print(f"⏱️  Ориентировочное время: {len(points)*delay/60:.1f} минут")
        print(f"{'-'*60}")
        
        # Поиск панорам
        results = []
        found_count = 0
        
        for i, (lat, lon) in enumerate(points):
            # Прогресс
            if i % 50 == 0 and i > 0:
                elapsed = time.time() - self.start_time
                speed = i / elapsed if elapsed > 0 else 0
                remaining = (len(points) - i) / speed if speed > 0 else 0
                print(f"  {i}/{len(points)} точек | "
                      f"Найдено: {found_count} | "
                      f"Скорость: {speed:.1f} точек/сек | "
                      f"Осталось: {remaining/60:.1f} мин")
            
            # Поиск панорамы
            panorama = self._find_nearest_panorama(lat, lon, search_radius)
            
            if panorama:
                results.append(panorama)
                found_count += 1
            
            # Задержка для соблюдения лимитов
            time.sleep(delay)
        
        # Сохранение результатов
        stats = self._save_results(results, output_file)
        
        # Вывод итогов
        elapsed_total = time.time() - self.start_time
        efficiency = (found_count / len(points) * 100) if points else 0
        
        print(f"\n{'='*60}")
        print(f"✅ ПОИСК ЗАВЕРШЕН!")
        print(f"{'='*60}")
        print(f"📊 РЕЗУЛЬТАТЫ:")
        print(f"  Проверено точек:    {len(points)}")
        print(f"  Найдено панорам:    {found_count}")
        print(f"  Эффективность:      {efficiency:.1f}%")
        print(f"  Запросов к API:     {self.request_count}")
        print(f"  Время выполнения:   {elapsed_total:.1f} сек")
        print(f"  Средняя скорость:   {len(points)/elapsed_total:.1f} точек/сек")
        print(f"\n💾 ФАЙЛЫ:")
        print(f"  Ссылки:             {output_file}")
        print(f"  Детальный отчёт:    {stats['csv_file']}")
        
        if found_count == 0:
            print(f"\n⚠️  ПАНОРАМЫ НЕ НАЙДЕНЫ!")
            print(f"   Возможные причины:")
            print(f"   1. Неверный API ключ")
            print(f"   2. Street View Static API не активирован")
            print(f"   3. В указанной области нет панорам Google")
            print(f"   4. Исчерпан дневной лимит запросов")
        
        return stats
    
    def search_from_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Поиск панорам на основе конфигурационного словаря.
        
        Args:
            config: Словарь с конфигурацией
            
        Returns:
            Словарь со статистикой
        """
        return self.search_area(
            lat_min=config['bounds']['lat_min'],
            lat_max=config['bounds']['lat_max'],
            lon_min=config['bounds']['lon_min'],
            lon_max=config['bounds']['lon_max'],
            step_km=config['search_params'].get('step_km', 0.15),
            search_radius=config['search_params'].get('search_radius', 50),
            max_points=config['search_params'].get('max_points', 1000),
            output_file=config['output'].get('filename', 'panoramas.txt'),
            delay=config['search_params'].get('delay', 0.03)
        )
    
    def _generate_grid(self,
                      lat_min: float, lat_max: float,
                      lon_min: float, lon_max: float,
                      step_km: float) -> List[Tuple[float, float]]:
        """
        Генерирует равномерную сетку точек.
        
        Args:
            lat_min: Минимальная широта
            lat_max: Максимальная широта
            lon_min: Минимальная долгота
            lon_max: Максимальная долгота
            step_km: Шаг в километрах
            
        Returns:
            Список кортежей (широта, долгота)
        """
        # Средняя широта для расчёта коэффициента
        avg_lat = (lat_min + lat_max) / 2
        
        # Коэффициенты преобразования
        km_per_degree_lat = 111.0
        km_per_degree_lon = 111.0 * math.cos(math.radians(avg_lat))
        
        # Шаг в градусах
        step_lat = step_km / km_per_degree_lat
        step_lon = step_km / km_per_degree_lon
        
        points = []
        lat = lat_min
        
        while lat <= lat_max:
            lon = lon_min
            while lon <= lon_max:
                points.append((lat, lon))
                lon += step_lon
            lat += step_lat
        
        return points
    
    def _find_nearest_panorama(self,
                              lat: float, lon: float,
                              radius: int) -> Optional[Dict[str, Any]]:
        """
        Ищет ближайшую панораму к заданной точке.
        
        Args:
            lat: Широта
            lon: Долгота
            radius: Радиус поиска в метрах
            
        Returns:
            Словарь с данными панорамы или None
        """
        url = "https://maps.googleapis.com/maps/api/streetview/metadata"
        params = {
            "location": f"{lat},{lon}",
            "radius": radius,
            "key": self.api_key
        }
        
        try:
            self.request_count += 1
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "OK":
                pano_id = data["pano_id"]
                
                # Проверка на дубликаты
                if pano_id in self.found_panos:
                    return None
                
                # Точные координаты от Google
                exact_lat = data["location"]["lat"]
                exact_lng = data["location"]["lng"]
                
                # Расстояние от исходной точки
                distance = self._calculate_distance(lat, lon, exact_lat, exact_lng)
                
                # Создание ссылки
                link = self._create_panorama_link(pano_id, exact_lat, exact_lng)
                
                panorama_data = {
                    "pano_id": pano_id,
                    "lat": exact_lat,
                    "lng": exact_lng,
                    "date": data.get("date", ""),
                    "copyright": data.get("copyright", ""),
                    "location": data.get("location", {}),
                    "link": link,
                    "searched_from": f"{lat:.5f},{lon:.5f}",
                    "distance_m": distance,
                    "found_at": datetime.now().isoformat()
                }
                
                # Сохраняем в кэш
                self.found_panos[pano_id] = panorama_data
                return panorama_data
            
            elif data.get("status") == "OVER_QUERY_LIMIT":
                print(f"\n⚠️  ПРЕВЫШЕН ЛИМИТ ЗАПРОСОВ!")
                print(f"   Подождите 24 часа или увеличьте квоту в Google Cloud")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"    Ошибка сети: {e}")
        except Exception as e:
            print(f"    Ошибка обработки: {e}")
        
        return None
    
    def _create_panorama_link(self, pano_id: str, lat: float, lng: float) -> str:
        """
        Создаёт ссылку на панораму Google Street View.
        
        Args:
            pano_id: ID панорамы
            lat: Широта
            lng: Долгота
            
        Returns:
            Полная ссылка на панораму
        """
        return (f"https://www.google.de/maps/@{lat:.10f},"
                f"{lng:.10f},3a,75y,2.85h,90t/"
                f"data=!3m6!1e1!3m4!1s{pano_id}!2e0!"
                f"7i13312!8i6656")
    
    def _calculate_distance(self,
                           lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """
        Рассчитывает расстояние между двумя точками в метрах.
        
        Args:
            lat1, lon1: Первая точка
            lat2, lon2: Вторая точка
            
        Returns:
            Расстояние в метрах
        """
        # Упрощённый расчёт (достаточно точный для небольших расстояний)
        dlat = (lat2 - lat1) * 111000  # метров в градусе широты
        dlon = (lon2 - lon1) * 111000 * math.cos(math.radians((lat1 + lat2) / 2))
        return math.sqrt(dlat**2 + dlon**2)
    
    def _save_results(self,
                     results: List[Dict[str, Any]],
                     output_file: str) -> Dict[str, Any]:
        """
        Сохраняет результаты поиска в файлы.
        
        Args:
            results: Список найденных панорам
            output_file: Имя основного файла
            
        Returns:
            Словарь с информацией о созданных файлах
        """
        if not results:
            return {
                "total": 0,
                "txt_file": "",
                "csv_file": "",
                "stats": {}
            }
        
        # 1. Сохраняем ссылки в TXT
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in results:
                f.write(item["link"] + '\n')
        
        # 2. Сохраняем детальный отчёт в CSV
        csv_file = output_file.replace('.txt', '_details.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "pano_id", "latitude", "longitude", "date",
                "distance_m", "searched_from", "found_at", "link"
            ])
            
            for item in results:
                writer.writerow([
                    item["pano_id"],
                    f"{item['lat']:.10f}",
                    f"{item['lng']:.10f}",
                    item.get("date", ""),
                    f"{item.get('distance_m', 0):.1f}",
                    item["searched_from"],
                    item["found_at"],
                    item["link"]
                ])
        
        # 3. Собираем статистику
        stats = {
            "total": len(results),
            "avg_distance": sum(item.get('distance_m', 0) for item in results) / len(results),
            "unique_dates": len(set(item.get('date', '') for item in results if item.get('date'))),
            "search_date": datetime.now().isoformat()
        }
        
        return {
            "total": len(results),
            "txt_file": output_file,
            "csv_file": csv_file,
            "stats": stats
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику текущей сессии.
        
        Returns:
            Словарь со статистикой
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return {
            "requests": self.request_count,
            "found_panos": len(self.found_panos),
            "elapsed_seconds": elapsed,
            "requests_per_second": self.request_count / elapsed if elapsed > 0 else 0
        }
