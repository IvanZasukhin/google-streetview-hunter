"""
Тесты для модуля core.py
"""

import pytest
from unittest.mock import Mock, patch
from streetview_hunter.core import StreetViewHunter


class TestStreetViewHunter:
    """Тесты класса StreetViewHunter."""
    
    def test_init(self):
        """Тест инициализации класса."""
        hunter = StreetViewHunter(api_key="test_key")
        assert hunter.api_key == "test_key"
        assert hunter.request_count == 0
        assert len(hunter.found_panos) == 0
    
    def test_generate_grid(self):
        """Тест генерации сетки точек."""
        hunter = StreetViewHunter(api_key="test_key")
        
        # Маленькая область для теста
        points = hunter._generate_grid(
            lat_min=61.66, lat_max=61.67,
            lon_min=50.83, lon_max=50.84,
            step_km=0.5  # Крупный шаг
        )
        
        # Должна быть хотя бы одна точка
        assert len(points) > 0
        
        # Проверяем формат точек
        for lat, lon in points:
            assert isinstance(lat, float)
            assert isinstance(lon, float)
            assert 61.66 <= lat <= 61.67
            assert 50.83 <= lon <= 50.84
    
    def test_calculate_distance(self):
        """Тест расчёта расстояния."""
        hunter = StreetViewHunter(api_key="test_key")
        
        # Одна и та же точка
        distance = hunter._calculate_distance(
            61.668742, 50.835369,
            61.668742, 50.835369
        )
        assert abs(distance) < 0.1  # Практически 0
        
        # Разные точки
        distance = hunter._calculate_distance(
            61.66, 50.83,
            61.67, 50.84
        )
        assert distance > 0
    
    def test_create_panorama_link(self):
        """Тест создания ссылки на панораму."""
        hunter = StreetViewHunter(api_key="test_key")
        
        test_pano_id = "CAoSLEFGMVFpcE5fTVhFNmhJQWtTb0J2SXc"
        test_lat = 61.668742
        test_lng = 50.835369
        
        link = hunter._create_panorama_link(test_pano_id, test_lat, test_lng)
        
        # Проверяем, что ссылка содержит необходимые элементы
        assert "google.de/maps/@" in link
        assert str(test_lat) in link
        assert str(test_lng) in link
        assert test_pano_id in link
        assert "data=!3m6!1e1!3m4" in link
    
    @patch('streetview_hunter.core.requests.Session')
    def test_find_nearest_panorama_success(self, mock_session):
        """Тест успешного поиска панорамы."""
        # Мокаем ответ API
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "pano_id": "test_pano_id_123",
            "location": {
                "lat": 61.668742,
                "lng": 50.835369
            },
            "date": "2023-07",
            "copyright": "© Google"
        }
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        hunter = StreetViewHunter(api_key="test_key")
        hunter.session = mock_session_instance
        
        result = hunter._find_nearest_panorama(
            lat=61.66, lon=50.83, radius=50
        )
        
        assert result is not None
        assert result["pano_id"] == "test_pano_id_123"
        assert result["lat"] == 61.668742
        assert result["lng"] == 50.835369
        assert "link" in result
    
    @patch('streetview_hunter.core.requests.Session')
    def test_find_nearest_panorama_no_results(self, mock_session):
        """Тест поиска, когда панорамы не найдены."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ZERO_RESULTS"
        }
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        hunter = StreetViewHunter(api_key="test_key")
        hunter.session = mock_session_instance
        
        result = hunter._find_nearest_panorama(
            lat=61.66, lon=50.83, radius=50
        )
        
        assert result is None
    
    def test_save_results_empty(self, tmp_path):
        """Тест сохранения пустых результатов."""
        hunter = StreetViewHunter(api_key="test_key")
        
        output_file = tmp_path / "test_empty.txt"
        
        stats = hunter._save_results([], str(output_file))
        
        assert stats["total"] == 0
        assert not output_file.exists()  # Файл не должен быть создан
    
    def test_save_results_with_data(self, tmp_path):
        """Тест сохранения результатов с данными."""
        hunter = StreetViewHunter(api_key="test_key")
        
        test_data = [{
            "pano_id": "test_id_1",
            "lat": 61.668742,
            "lng": 50.835369,
            "date": "2023-07",
            "copyright": "© Google",
            "link": "https://example.com/test1",
            "searched_from": "61.66,50.83",
            "distance_m": 10.5,
            "found_at": "2024-01-01T12:00:00"
        }]
        
        output_file = tmp_path / "test_results.txt"
        
        stats = hunter._save_results(test_data, str(output_file))
        
        assert stats["total"] == 1
        assert output_file.exists()
        
        # Проверяем, что CSV файл тоже создан
        csv_file = tmp_path / "test_results_details.csv"
        assert csv_file.exists()
        
        # Читаем и проверяем содержимое TXT файла
        with open(output_file, 'r') as f:
            content = f.read()
            assert "https://example.com/test1" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
