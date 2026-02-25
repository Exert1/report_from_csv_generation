import csv
from pathlib import Path
from typing import List
from tabulate import tabulate
from collections import defaultdict
import argparse


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        type=str,
        help="Список файлов"
    )
    arg_parser.add_argument(
        "--report",
        required=True,
        type=str,
        help="Название отчёта"
    )
    return arg_parser.parse_args()


def get_files(file_paths: List[str]):
    files = []
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError("Путь не существует")
        if not path.is_file():
            raise FileNotFoundError("Это не файл (возможно, директория)")
        files.append(path)

    return files


def average_gdp(files: List[str]) -> None:
    country_data: dict = defaultdict(lambda: {"sum_gdp": 0, "count": 0})
    average_gdp_report = []
    csv_files = get_files(files)

    for csv_fl in csv_files:
        with open(csv_fl, newline="") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                country = row.get("country")
                gdp = int(row.get("gdp"))

                if not country or not gdp:
                    continue

                country_data[country]["sum_gdp"] += gdp
                country_data[country]["count"] += 1

    for country, data in country_data.items():
        average_gdp_report.append({
            "country": country, "gdp": data["sum_gdp"] / data["count"]
        })

    average_gdp_report.sort(key=lambda x: x["gdp"], reverse=True)
    print(tabulate(
        average_gdp_report,
        headers="keys",
        tablefmt="psql",
        showindex=range(1, len(average_gdp_report) + 1),
        floatfmt=(".2f")
    ))


def main():
    args = parse_arguments()
    match args.report:
        case "average_gdp":
            average_gdp(args.files)


if __name__ == "__main__":
    main()
