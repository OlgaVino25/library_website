import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def render_website():
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )

    template = env.get_template("template.html")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    meta_data_path = os.path.join(script_dir, "meta_data.json")

    with open(meta_data_path, "r", encoding="utf-8") as my_file:
        books = json.load(my_file)

    for book in books:
        book["img_src"] = book["img_src"].replace("\\", "/")

    books_per_page = 10
    book_pages = list(chunked(books, books_per_page))

    os.makedirs("pages", exist_ok=True)

    for page_num, books_on_page in enumerate(book_pages, 1):
        books_chunks = list(chunked(books_on_page, 2))

        rendered_page = template.render(
            books_chunks=books_chunks,
            current_page=page_num,
            total_pages=len(book_pages),
        )

        file_path = f"pages/index{page_num}.html"

        with open(file_path, "w", encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == "__main__":
    render_website()
