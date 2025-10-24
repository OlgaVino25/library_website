import os
from livereload import Server
from render_website import render_website

render_website()

# Получаем абсолютный путь к директории site
script_dir = os.path.dirname(os.path.abspath(__file__))
site_dir = os.path.join(script_dir, "site")

server = Server()
server.watch("templates/*.html", render_website)
server.watch("src/meta_data.json", render_website)
server.watch("src/books/*.txt", render_website)
server.serve(root=site_dir, port=5500, host="127.0.0.1")
