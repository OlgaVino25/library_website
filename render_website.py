import json
import os
import math
import re
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def sanitize_filename(filename):
    """Очищает имя файла от недопустимых символов"""
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, " ", filename)


def render_website():
    # Получаем абсолютный путь к директории скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Создаем папку site если её нет
    site_dir = os.path.join(script_dir, "site")

    # Удаляем старую папку site и создаем заново
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)
    os.makedirs(site_dir)

    # Копируем статические файлы в site/static
    static_src = os.path.join(script_dir, "static")
    static_dest = os.path.join(site_dir, "static")
    if os.path.exists(static_src):
        shutil.copytree(static_src, static_dest)

    # Копируем медиафайлы в site/media
    src_dir = os.path.join(script_dir, "src")
    media_dest = os.path.join(site_dir, "media")
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, media_dest)

    # Загружаем шаблоны из папки templates
    templates_dir = os.path.join(script_dir, "templates")
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("template.html")
    book_template = env.get_template("book_template.html")

    # Загружаем meta_data.json из src
    meta_data_path = os.path.join(script_dir, "src", "meta_data.json")
    with open(meta_data_path, "r", encoding="utf-8") as my_file:
        books = json.load(my_file)

    # Обновляем пути в метаданных
    for book in books:
        # Исправляем пути к изображениям
        book["img_src"] = book["img_src"].replace("\\", "/")
        if not book["img_src"].startswith("media/"):
            book["img_src"] = "media/" + book["img_src"]

        # Исправляем пути к книгам
        book["book_path"] = book["book_path"].replace("\\", "/")
        if not book["book_path"].startswith("media/"):
            book["book_path"] = "media/" + book["book_path"]

    # Создаем папки в site
    os.makedirs(os.path.join(site_dir, "book_pages"), exist_ok=True)
    os.makedirs(os.path.join(site_dir, "pages"), exist_ok=True)

    # Генерируем HTML страницы для книг
    for book in books:
        book_path = book["book_path"]
        try:
            # Читаем исходный текст книги
            book_file_path = os.path.join(site_dir, book_path)
            with open(book_file_path, "r", encoding="utf-8") as f:
                book_content = f.read()

            safe_title = sanitize_filename(book["title"])

            rendered_book = book_template.render(
                title=book["title"], author=book["author"], book_content=book_content
            )

            # Сохраняем книгу как HTML в site/book_pages
            book_html_path = os.path.join(site_dir, "book_pages", f"{safe_title}.html")
            with open(book_html_path, "w", encoding="utf8") as f:
                f.write(rendered_book)

            # Обновляем путь к книге в метаданных
            book["book_path"] = f"book_pages/{safe_title}.html"

        except Exception as e:
            print(f"Ошибка при обработке книги {book['title']}: {e}")
            continue

    # Сохраняем обновленный meta_data.json в site
    meta_data_dest = os.path.join(site_dir, "meta_data.json")
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

        file_path = os.path.join(site_dir, "pages", f"index{page_num}.html")
        with open(file_path, "w", encoding="utf8") as file:
            file.write(rendered_page)

    # Создаем главный index.html с редиректом
    index_path = os.path.join(site_dir, "index.html")
    with open(index_path, "w", encoding="utf8") as file:
        file.write('<meta http-equiv="refresh" content="0; url=pages/index1.html">')


if __name__ == "__main__":
    render_website()
