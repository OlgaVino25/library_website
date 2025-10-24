import os
from livereload import Server
from render_website import render_website, get_config


def main():
    config = get_config()
    render_website(config)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    root_dir = script_dir

    server = Server()

    server.watch(f"{config.templates_dir}/*.html", lambda: render_website(config))
    server.watch(config.data_path, lambda: render_website(config))
    server.watch(f"{config.src_dir}/books/*.txt", lambda: render_website(config))

    server.serve(root=root_dir, port=5500, host="127.0.0.1")


if __name__ == "__main__":
    main()
