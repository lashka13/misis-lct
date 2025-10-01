import os
from pathlib import Path


def load_categories_from_file() -> list[str]:
    """Загрузить категории из файла

    Args:
        file_path (str, optional): Путь к файлу с категориями (по умолчанию "data/categories.txt")

    Returns:
        list[str]: Список категорий
    """
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    file_path = str(project_root / "data" / "categories.txt")

    if not os.path.exists(file_path):
        categories = [
            "Дебетовые карты",
            "Кредитные карты",
            "Ипотека",
            "Автокредиты",
            "Кредиты",
            "Реструктуризация",
            "Вклады",
            "Переводы",
            "Дистанционное обслуживание",
            "Мобильное приложение",
            "Обслуживание",
            "Прочее",
        ]

    try:
        with open(file_path, encoding="utf-8") as f:
            categories = [line.strip() for line in f if line.strip()]

        return categories

    except Exception as e:
        raise Exception(f"Ошибка при чтении {file_path}: {e}") from e
