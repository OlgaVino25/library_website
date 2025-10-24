import json
import os
import math
import re
import shutil
import argparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

# Константы с путями по умолчанию
DEFAULT_META_DATA_PATH = "src/meta_data.json"
DEFAULT_TEMPLATES_DIR = "templates"
DEFAULT_STATIC_DIR = "static"
DEFAULT_SRC_DIR = "src"
DEFAULT_OUTPUT_DIR = "docs"


def sanitize_filename(filename):
    """Очищает имя файла от недопустимых символов"""
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, " ", filename)


def get_config():
    """Получает конфигурацию из аргументов командной строки и переменных окружения"""
    parser = argparse.ArgumentParser(description="Генератор сайта библиотеки")

    parser.add_argument(
        "--data-path",
        default=os.getenv("LIBRARY_DATA_PATH", DEFAULT_META_DATA_PATH),
        help=f"Путь к файлу meta_data.json (по умолчанию: {DEFAULT_META_DATA_PATH})",
    )
    parser.add_argument(
        "--templates-dir",
        default=os.getenv("LIBRARY_TEMPLATES_DIR", DEFAULT_TEMPLATES_DIR),
        help=f"Папка с шаблонами (по умолчанию: {DEFAULT_TEMPLATES_DIR})",
    )
    parser.add_argument(
        "--static-dir",
        default=os.getenv("LIBRARY_STATIC_DIR", DEFAULT_STATIC_DIR),
        help=f"Папка со статическими файлами (по умолчанию: {DEFAULT_STATIC_DIR})",
    )
    parser.add_argument(
        "--src-dir",
        default=os.getenv("LIBRARY_SRC_DIR", DEFAULT_SRC_DIR),
        help=f"Папка с исходными файлами (по умолчанию: {DEFAULT_SRC_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("LIBRARY_OUTPUT_DIR", DEFAULT_OUTPUT_DIR),
        help=f"Папка для сгенерированного сайта (по умолчанию: {DEFAULT_OUTPUT_DIR})",
    )

    return parser.parse_args()


def render_website(config):
    # Получаем абсолютный путь к директории скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Создаем папку для вывода если её нет
    docs_dir = os.path.join(script_dir, config.output_dir)

    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    os.makedirs(docs_dir)

    # Копируем статические файлы
    static_src = os.path.join(script_dir, config.static_dir)
    static_dest = os.path.join(docs_dir, "static")
    if os.path.exists(static_src):
        shutil.copytree(static_src, static_dest)

    # Копируем медиафайлы
    src_dir = os.path.join(script_dir, config.src_dir)
    media_dest = os.path.join(docs_dir, "media")
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, media_dest)

    # Загружаем шаблоны
    templates_dir = os.path.join(script_dir, config.templates_dir)
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("template.html")
    book_template = env.get_template("book_template.html")

    # Загружаем meta_data.json
    if os.path.isabs(config.data_path):
        meta_data_path = config.data_path
    else:
        meta_data_path = os.path.join(script_dir, config.data_path)

    print(f"Загрузка данных из: {meta_data_path}")

    try:
        with open(meta_data_path, "r", encoding="utf-8") as my_file:
            books = json.load(my_file)
    except FileNotFoundError:
        print(f"Ошибка: Файл {meta_data_path} не найден!")
        print(
            "Укажите правильный путь через --data-path или переменную окружения LIBRARY_DATA_PATH"
        )
        return

    # Обновляем пути в метаданных
    for book in books:
        book["img_src"] = book["img_src"].replace("\\", "/")
        if not book["img_src"].startswith("media/"):
            book["img_src"] = "media/" + book["img_src"]

        book["book_path"] = book["book_path"].replace("\\", "/")
        if not book["book_path"].startswith("media/"):
            book["book_path"] = "media/" + book["book_path"]

    # Создаем папки в docs
    os.makedirs(os.path.join(docs_dir, "book_pages"), exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "pages"), exist_ok=True)

    # Генерируем HTML страницы для книг
    for book in books:
        book_path = book["book_path"]
        try:
            # Читаем исходный текст книги
            book_file_path = os.path.join(docs_dir, book_path)
            with open(book_file_path, "r", encoding="utf-8") as f:
                book_content = f.read()

            safe_title = sanitize_filename(book["title"])

            rendered_book = book_template.render(
                title=book["title"], author=book["author"], book_content=book_content
            )

            # Сохраняем книгу как HTML в docs/book_pages
            book_html_path = os.path.join(docs_dir, "book_pages", f"{safe_title}.html")
            with open(book_html_path, "w", encoding="utf8") as f:
                f.write(rendered_book)

            # Обновляем путь к книге в метаданных
            book["book_path"] = f"book_pages/{safe_title}.html"

        except Exception as e:
            print(f"Ошибка при обработке книги {book['title']}: {e}")
            continue

    # Сохраняем обновленный meta_data.json в docs
    meta_data_dest = os.path.join(docs_dir, "meta_data.json")
    with open(meta_data_dest, "w", encoding="utf8") as f:
        json.dump(books, f, ensure_ascii=False, indent=4)

    # Генерируем страницы каталога
    books_per_page = 10
    total_pages = math.ceil(len(books) / books_per_page)
    book_pages = list(chunked(books, books_per_page))

    for page_num, books_on_page in enumerate(book_pages, 1):
        books_chunks = list(chunked(books_on_page, 2))

        rendered_page = template.render(
            books_chunks=books_chunks,
            current_page=page_num,
            total_pages=total_pages,
        )

        file_path = os.path.join(docs_dir, "pages", f"index{page_num}.html")
        with open(file_path, "w", encoding="utf8") as file:
            file.write(rendered_page)

    # Создаем главный index.html с редиректом
    index_path = os.path.join(docs_dir, "index.html")
    with open(index_path, "w", encoding="utf8") as file:
        file.write('<meta http-equiv="refresh" content="0; url=pages/index1.html">')

    print(f"Сайт успешно сгенерирован в папке: {docs_dir}")


if __name__ == "__main__":
    config = get_config()
    render_website(config)
