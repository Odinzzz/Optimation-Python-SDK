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


def create_fastapi_template(root: Path, project: str) -> None:
    package_root = root / "src" / project

    templates_dir, static_css_dir, static_js_dir = create_web_dirs(package_root)

    (package_root / "app.py").write_text(
        "from fastapi import FastAPI, Request\n"
        "from fastapi.responses import HTMLResponse\n"
        "from fastapi.staticfiles import StaticFiles\n"
        "from fastapi.templating import Jinja2Templates\n\n"
        "def create_app() -> FastAPI:\n"
        "    app = FastAPI(title='Optimation FastAPI App')\n\n"
        f"    app.mount('/static', StaticFiles(directory='src/{project}/static'), name='static')\n"
        f"    templates = Jinja2Templates(directory='src/{project}/templates')\n\n"
        "    @app.get('/', response_class=HTMLResponse)\n"
        "    def index(request: Request):\n"
        "        return templates.TemplateResponse(\n"
        "            request=request,\n"
        "            name='index.html',\n"
        "            context={'app_name': 'Optimation FastAPI App'}\n"
        "        )\n\n"
        "    return app\n",
        encoding="utf-8",
    )

    (package_root / "main.py").write_text(
        "try:\n"
        "    from .app import create_app\n"
        "except ImportError:\n"
        "    from app import create_app\n\n"
        "app = create_app()\n",
        encoding="utf-8",
    )

    (templates_dir / "base.html").write_text(
        build_base_html(css_href="/static/css/style.css", js_src="/static/js/app.js"),
        encoding="utf-8",
    )

    (templates_dir / "index.html").write_text(
        build_index_html(
            description=(
                "FastAPI project scaffolded with Bootstrap, templates, static assets, "
                "and a ready-to-run app."
            ),
            cta_href="/docs",
            cta_label="Open API docs",
            app_card_title="FastAPI App",
        ),
        encoding="utf-8",
    )

    (static_css_dir / "style.css").write_text(COMMON_CSS, encoding="utf-8")

    (static_js_dir / "app.js").write_text(
        build_common_js("Optimation FastAPI Bootstrap template ready."),
        encoding="utf-8",
    )

    (root / "requirements.txt").write_text(
        "fastapi>=0.116.0,<1.0.0\n"
        "uvicorn[standard]>=0.35.0,<1.0.0\n"
        "jinja2>=3.1.0,<4.0.0\n",
        encoding="utf-8",
    )

    (root / "README.md").write_text(
        build_readme(
            project=project,
            framework_name="FastAPI",
            run_command=f"uvicorn src.{project}.main:app --reload",
            open_url="http://127.0.0.1:8000",
            docs_url="http://127.0.0.1:8000/docs",
        ),
        encoding="utf-8",
    )

    (root / "tests" / "test_app.py").write_text(
        "from fastapi.testclient import TestClient\n"
        "from src.{project}.app import create_app\n\n"
        "def test_homepage_returns_200():\n"
        "    app = create_app()\n"
        "    client = TestClient(app)\n\n"
        "    response = client.get('/')\n\n"
        "    assert response.status_code == 200\n".format(project=project),
        encoding="utf-8",
    )
