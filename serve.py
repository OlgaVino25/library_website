from livereload import Server
from render_website import render_website


render_website()

server = Server()
server.watch("template.html", render_website)
server.watch("meta_data.json", render_website)
server.serve(port=5500, host="127.0.0.1")
