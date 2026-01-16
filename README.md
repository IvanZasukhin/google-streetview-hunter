# 🗺️ Google Street View Hunter

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Автоматический сборщик панорам Google Street View. Ищет все доступные панорамы в заданной области и сохраняет ссылки в нужном формате.

## ✨ Особенности

- 🔍 **Умный поиск по сетке** — находит панорамы даже во дворах
- 📍 **Точные координаты** — использует данные Google, а не приближения
- 🏙️ **Универсальность** — работает для любого города мира
- 🚀 **Быстрая обработка** — многопоточность и кэширование
- 📊 **Детальная статистика** — CSV с метаданными

## 🚀 Быстрый старт

### Установка

```bash
git clone https://github.com/ваш-username/google-streetview-hunter.git
cd google-streetview-hunter
pip install -r requirements.txt
```
## Получение API ключа Google:
1. Перейдите в Google Cloud Console

2. Создайте новый проект

3. Активируйте Street View Static API

4. Создайте API ключ в разделе "Credentials"

## Базовое использование
```python
from streetview_hunter import StreetViewHunter

# Инициализация
hunter = StreetViewHunter(api_key="ВАШ_API_КЛЮЧ")

# Поиск в области
stats = hunter.search_area(
    lat_min=61.66, lat_max=61.69,
    lon_min=50.81, lon_max=50.86,
    step_km=0.12,      # шаг сетки ~130 метров
    search_radius=50,  # радиус поиска в метрах
    output_file="сыктывкар_панорамы.txt"
)

print(f"✅ Найдено {stats['total']} панорам")
```
## Командная строка
```bash
# Простой запуск
python -m streetview_hunter.cli --api-key=ВАШ_КЛЮЧ

# С конфигурационным файлом
python -m streetview_hunter.cli --api-key=ВАШ_КЛЮЧ --config=configs/syktyvkar.yaml

# Свои параметры
python -m streetview_hunter.cli \
    --api-key=ВАШ_КЛЮЧ \
    --lat-min=61.66 --lat-max=61.69 \
    --lon-min=50.81 --lon-max=50.86 \
    --step-km=0.15 \
    --output="мой_город.txt"
```
## 📁 Выходные файлы
Скрипт создаёт два файла:

### 1. Текстовый файл с ссылками (сыктывкар_панорамы.txt)
```text
https://www.google.de/maps/@61.668742,50.835369,3a,75y,2.85h,90t/data=!3m6!1e1!3m4!1sCAoSLEFGMVFpcE5...!2e0!7i13312!8i6656
https://www.google.de/maps/@61.667812,50.836501,3a,75y,2.85h,90t/data=!3m6!1e1!3m4!1sCAoSLEFGMVFpcE5...!2e0!7i13312!8i6656
```
### 2. CSV с метаданными (сыктывкар_панорамы_details.csv)
```csv
pano_id,latitude,longitude,date,distance_m,searched_from,link
CAoSLEFGMVFpcE5...,61.668742,50.835369,2023-07,12.3,61.66800,50.83500,https://...
```
## ⚙️ Конфигурация городов
Создайте YAML-файл в папке configs/:

```yaml
# configs/moscow.yaml
name: "Москва (центр)"
bounds:
  lat_min: 55.75
  lat_max: 55.78
  lon_min: 37.60
  lon_max: 37.65
search_params:
  step_km: 0.15
  search_radius: 80
  max_points: 1500
output:
  filename: "москва_центр_панорамы.txt"
  format: "google.de"
```
### Использование:

```bash
python -m streetview_hunter.cli --api-key=ВАШ_КЛЮЧ --config=configs/moscow.yaml
```
## 📊 Примеры
### Пример 1: Поиск в конкретном районе
```python
from streetview_hunter import StreetViewHunter

hunter = StreetViewHunter(api_key="ВАШ_КЛЮЧ")

# Только центр города
stats = hunter.search_area(
    lat_min=61.667, lat_max=61.671,
    lon_min=50.832, lon_max=50.838,
    step_km=0.08,      # плотная сетка (~90м)
    search_radius=30,  # точный поиск
    max_points=300,
    output_file="центр_сыктывкара.txt"
)
```
### Пример 2: Пакетная обработка
```python
# examples/batch_processing.py
from streetview_hunter import StreetViewHunter
import yaml

hunter = StreetViewHunter(api_key="ВАШ_КЛЮЧ")

# Загружаем конфиги для нескольких городов
cities = ['syktyvkar', 'moscow', 'spb']

for city in cities:
    with open(f'configs/{city}.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"🔍 Ищем панорамы в {config['name']}...")
    stats = hunter.search_from_config(config)
    print(f"   Найдено: {stats['total']} панорам")
```
## 🏗️ Архитектура
```text
Пользователь
    │
    ├───► CLI (cli.py)           # Интерфейс командной строки
    │
    ├───► StreetViewHunter       # Основной класс (core.py)
    │       ├───► Генератор сетки
    │       ├───► API клиент
    │       └───► Обработчик результатов
    │
    └───► Google Street View API # Внешний сервис
```
## ⚠️ Ограничения и рекомендации
Лимиты API: Бесплатно 28,000 запросов в месяц

Скорость: Не более 1 запроса в 0.03 секунды

Для больших городов: Используйте step_km=0.20-0.30 и search_radius=80-100

Для точного поиска: step_km=0.08-0.12 и search_radius=30-50

## 📞 Контакты

Иван Засухин - ivanzasukhin11@gmail.com

Ссылка на проект: [https://github.com/IvanZasukhin/google-streetview-hunter](https://github.com/IvanZasukhin/google-streetview-hunter)
