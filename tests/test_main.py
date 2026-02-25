import pytest
from contextlib import nullcontext as does_not_raise
from pathlib import Path
import report_generator

from unittest.mock import patch, mock_open
from io import StringIO
import csv


@pytest.mark.parametrize(
    "file_path, result, expectation",
    [
        (
            ["economics/economic1.csv"],
            [Path("economics/economic1.csv")],
            does_not_raise(),
        ),
        (
            ["economics/economic1.csv", "economics/economic2.csv"],
            [Path("economics/economic1.csv"), Path("economics/economic2.csv")],
            does_not_raise(),
        ),
        (["economic1.csv"], None, pytest.raises(FileNotFoundError)),
    ],
)
def test_get_files(file_path, result, expectation):
    with expectation:
        assert report_generator.get_files(file_path) == result


@pytest.fixture
def mock_csv_files():
    """Фикстура для создания тестовых CSV‑данных в памяти."""
    csv_data_1 = StringIO()
    writer = csv.DictWriter(csv_data_1, fieldnames=['country', 'gdp'])
    writer.writeheader()
    writer.writerows([
        {'country': 'Russia', 'gdp': '1000'},
        {'country': 'USA', 'gdp': '2000'},
        {'country': 'Germany', 'gdp': '1500'}
    ])
    csv_data_1.seek(0)

    csv_data_2 = StringIO()
    writer = csv.DictWriter(csv_data_2, fieldnames=['country', 'gdp'])
    writer.writeheader()
    writer.writerows([
        {'country': 'Russia', 'gdp': '1200'},
        {'country': 'USA', 'gdp': '2200'},
        {'country': 'France', 'gdp': '1800'}
    ])
    csv_data_2.seek(0)

    return [csv_data_1, csv_data_2]


@patch('report_generator.get_files')
@patch('builtins.open', mock_open())
@patch('report_generator.tabulate')
def test_average_gdp_simple(mock_tabulate, mock_get_files, mock_csv_files):
    """Тест базового сценария: расчёт среднего ВВП из нескольких CSV‑файлов."""
    # Настраиваем моки
    mock_get_files.return_value = ['file1.csv', 'file2.csv']

    # Мокируем open так, чтобы он возвращал наши CSV‑данные
    open_mock = mock_open()
    open_mock.side_effect = [
        mock_open(read_data=mock_csv_files[0].getvalue()).return_value,
        mock_open(read_data=mock_csv_files[1].getvalue()).return_value
    ]

    with patch('builtins.open', open_mock):
        # Вызываем тестируемую функцию
        report_generator.average_gdp(['test_file1.csv', 'test_file2.csv'])

    # Проверяем, что tabulate был вызван один раз
    mock_tabulate.assert_called_once()

    # Извлекаем данные, переданные в tabulate
    actual_report = mock_tabulate.call_args[0][0]

    # Ожидаемый результат (отсортированный по убыванию GDP)
    expected_report = [
        {'country': 'USA', 'gdp': 2100.0},
        {'country': 'France', 'gdp': 1800.0},
        {'country': 'Germany', 'gdp': 1500.0},
        {'country': 'Russia', 'gdp': 1100.0}
    ]

    # Сортируем оба списка по убыванию GDP для надёжного сравнения
    actual_report.sort(key=lambda x: x['gdp'], reverse=True)
    expected_report.sort(key=lambda x: x['gdp'], reverse=True)

    # Сравниваем результаты
    assert actual_report == expected_report
