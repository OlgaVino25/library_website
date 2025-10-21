import json
import os
import math
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def sanitize_filename(filename):
    """Очищает имя файла от недопустимых символов"""
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, " ", filename)


def render_website():
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )

    template = env.get_template("template.html")
    book_template = env.get_template("book_template.html")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    meta_data_path = os.path.join(script_dir, "meta_data.json")

    with open(meta_data_path, "r", encoding="utf-8") as my_file:
        books = json.load(my_file)

    for book in books:
        book["img_src"] = book["img_src"].replace("\\", "/")

    os.makedirs("book_pages", exist_ok=True)

    # Генерируем HTML страницы для книг
    for book in books:
        book_path = book["book_path"]
        try:
            with open(book_path, "r", encoding="utf-8") as f:
                book_content = f.read()

            safe_title = sanitize_filename(book["title"])

            rendered_book = book_template.render(
                title=book["title"], author=book["author"], book_content=book_content
            )

            # Сохраняем книгу как HTML
            book_html_path = f"book_pages/{safe_title}.html"
            with open(book_html_path, "w", encoding="utf8") as f:
                f.write(rendered_book)

            # Обновляем путь к книге в метаданных
            book["book_path"] = book_html_path

        except Exception as e:
            print(f"Ошибка при обработке книги {book['title']}: {e}")
            # Оставляем оригинальный путь как запасной вариант
            continue

    books_per_page = 10

    total_pages = math.ceil(len(books) / books_per_page)
    book_pages = list(chunked(books, books_per_page))

    os.makedirs("pages", exist_ok=True)

    for page_num, books_on_page in enumerate(book_pages, 1):
        books_chunks = list(chunked(books_on_page, 2))

        rendered_page = template.render(
            books_chunks=books_chunks,
            current_page=page_num,
            total_pages=total_pages,
        )

        file_path = f"pages/index{page_num}.html"

        with open(file_path, "w", encoding="utf8") as file:
            file.write(rendered_page)

    with open("index.html", "w", encoding="utf8") as file:
        file.write('<meta http-equiv="refresh" content="0; url=pages/index1.html">')


if __name__ == "__main__":
    render_website()
