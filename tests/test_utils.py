"""
Тесты для модуля utils.py
"""

import pytest
import tempfile
import yaml
from streetview_hunter.utils import (
    load_config,
    save_config,
    validate_coordinates,
    calculate_area_size,
    estimate_points_count
)


class TestUtils:
    """Тесты вспомогательных функций."""
    
    def test_validate_coordinates_valid(self):
        """Тест валидации корректных координат."""
        # Корректные координаты
        assert validate_coordinates(
            lat_min=61.66, lat_max=61.69,
            lon_min=50.81, lon_max=50.86
        ) is True
    
    def test_validate_coordinates_invalid_range(self):
        """Тест валидации координат вне диапазона."""
        with pytest.raises(ValueError):
            validate_coordinates(
                lat_min=91.0, lat_max=61.69,  # lat_min > 90
                lon_min=50.81, lon_max=50.86
            )
    
    def test_validate_coordinates_invalid_order(self):
        """Тест валидации координат в неправильном порядке."""
        with pytest.raises(ValueError):
            validate_coordinates(
                lat_min=61.69, lat_max=61.66,  # min > max
                lon_min=50.86, lon_max=50.81   # min > max
            )
    
    def test_validate_coordinates_too_large(self):
        """Тест валидации слишком большой области."""
        with pytest.raises(ValueError):
            validate_coordinates(
                lat_min=40.0, lat_max=60.0,    # 20 градусов
                lon_min=30.0, lon_max=60.0     # 30 градусов
            )
    
    def test_calculate_area_size(self):
        """Тест расчёта размера области."""
        width_km, height_km = calculate_area_size(
            lat_min=61.66, lat_max=61.67,
            lon_min=50.83, lon_max=50.84
        )
        
        # Размеры должны быть положительными и небольшими
        assert width_km > 0
        assert height_km > 0
        assert width_km < 10
        assert height_km < 10
    
    def test_estimate_points_count(self):
        """Тест оценки количества точек."""
        points_count = estimate_points_count(
            lat_min=61.66, lat_max=61.67,
            lon_min=50.83, lon_max=50.84,
            step_km=0.1  # 100 метров
        )
        
        assert points_count > 0
        assert isinstance(points_count, int)
    
    def test_load_and_save_config(self):
        """Тест загрузки и сохранения конфигурации."""
        test_config = {
            "name": "Тестовый город",
            "bounds": {
                "lat_min": 61.66,
                "lat_max": 61.69,
                "lon_min": 50.81,
                "lon_max": 50.86
            },
            "search_params": {
                "step_km": 0.12,
                "search_radius": 50
            },
            "output": {
                "filename": "test.txt"
            }
        }
        
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
            yaml.dump(test_config, f, default_flow_style=False)
        
        try:
            # Загружаем обратно
            loaded_config = load_config(temp_file)
            
            # Проверяем, что конфигурация загрузилась корректно
            assert loaded_config["name"] == test_config["name"]
            assert loaded_config["bounds"]["lat_min"] == test_config["bounds"]["lat_min"]
            assert loaded_config["search_params"]["step_km"] == test_config["search_params"]["step_km"]
            
        finally:
            # Удаляем временный файл
            import os
            os.unlink(temp_file)
    
    def test_load_config_missing_file(self):
        """Тест загрузки несуществующего файла конфигурации."""
        with pytest.raises(FileNotFoundError):
            load_config("non_existent_file.yaml")
    
    def test_load_config_invalid_yaml(self):
        """Тест загрузки некорректного YAML файла."""
        # Создаём файл с некорректным YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
            f.write("invalid: yaml: content: [")
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_config(temp_file)
        finally:
            import os
            os.unlink(temp_file)
    
    def test_load_config_missing_keys(self):
        """Тест загрузки конфигурации с отсутствующими ключами."""
        incomplete_config = {
            "name": "Неполная конфигурация"
            # Нет обязательных ключей bounds, search_params, output
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
            yaml.dump(incomplete_config, f, default_flow_style=False)
        
        try:
            with pytest.raises(ValueError):
                load_config(temp_file)
        finally:
            import os
            os.unlink(temp_file)


def test_format_link():
    """Тест форматирования ссылки."""
    from streetview_hunter.utils import format_link
    
    template = "https://www.{domain}/maps/@{lat},{lng}"
    result = format_link(template, "test_id", 61.668742, 50.835369, "google.de")
    
    assert "google.de" in result
    assert "61.668742" in result
    assert "50.835369" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
