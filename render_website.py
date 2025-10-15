import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
)

template = env.get_template("template.html")

script_dir = os.path.dirname(os.path.abspath(__file__))
meta_data_path = os.path.join(script_dir, "meta_data.json")

with open(meta_data_path, "r", encoding="utf-8") as my_file:
    books = json.load(my_file)

for book in books:
    if "img_src" in book:
        book["img_src"] = book["img_src"].replace("\\", "/")

books_sorted = sorted(books, key=lambda x: x["title"])

rendered_page = template.render(books=books_sorted)

with open("index.html", "w", encoding="utf8") as file:
    file.write(rendered_page)
