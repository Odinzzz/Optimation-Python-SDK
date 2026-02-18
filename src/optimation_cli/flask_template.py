from __future__ import annotations

from pathlib import Path

from .template_shared import (
    COMMON_CSS,
    build_base_html,
    build_common_js,
    build_index_html,
    build_readme,
    create_web_dirs,
)


def create_flask_template(root: Path, project: str) -> None:
    package_root = root / "src" / project

    templates_dir, static_css_dir, static_js_dir = create_web_dirs(package_root)

    (package_root / "app.py").write_text(
        "from flask import Flask, render_template\n\n"
        "def create_app() -> Flask:\n"
        "    app = Flask(__name__)\n\n"
        "    @app.get('/')\n"
        "    def index():\n"
        "        return render_template('index.html', app_name='Optimation Flask App')\n\n"
        "    return app\n",
        encoding="utf-8",
    )

    (package_root / "main.py").write_text(
        "try:\n"
        "    from .app import create_app\n"
        "except ImportError:\n"
        "    from app import create_app\n\n"
        "app = create_app()\n\n"
        "if __name__ == '__main__':\n"
        "    app.run(debug=True)\n",
        encoding="utf-8",
    )

    (templates_dir / "base.html").write_text(
        build_base_html(
            css_href="{{ url_for('static', filename='css/style.css') }}",
            js_src="{{ url_for('static', filename='js/app.js') }}",
        ),
        encoding="utf-8",
    )

    (templates_dir / "index.html").write_text(
        build_index_html(
            description=(
                "Flask project scaffolded with Bootstrap, templates, static assets, "
                "and a ready-to-run app."
            ),
            cta_href="#",
            cta_label="Start building",
            app_card_title="Flask App",
        ),
        encoding="utf-8",
    )

    (static_css_dir / "style.css").write_text(COMMON_CSS, encoding="utf-8")

    (static_js_dir / "app.js").write_text(
        build_common_js("Optimation Flask Bootstrap template ready."),
        encoding="utf-8",
    )

    (root / "requirements.txt").write_text(
        "Flask>=3.0.0,<4.0.0\n",
        encoding="utf-8",
    )

    (root / "README.md").write_text(
        build_readme(
            project=project,
            framework_name="Flask",
            run_command=f"python src/{project}/main.py",
            open_url="http://127.0.0.1:5000",
        ),
        encoding="utf-8",
    )

    (root / "tests" / "test_app.py").write_text(
        "from src.{project}.app import create_app\n\n"
        "def test_homepage_returns_200():\n"
        "    app = create_app()\n"
        "    client = app.test_client()\n\n"
        "    response = client.get('/')\n\n"
        "    assert response.status_code == 200\n".format(project=project),
        encoding="utf-8",
    )
