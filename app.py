"""
Air2Stay — DCT Abu Dhabi · NSTI 2026
Streamlit wrapper that serves the standalone HTML prototype.
Run locally:  streamlit run app.py
"""

import base64
import pathlib
import re
import streamlit as st

st.set_page_config(
    page_title="Air2Stay · DCT Abu Dhabi",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Hide all Streamlit chrome ──────────────────────────────────────
st.markdown("""
<style>
#MainMenu, header, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; margin: 0 !important;
                   max-width: 100% !important; }
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main { overflow: visible !important; }
iframe { border: none; display: block; width: 100%;
         height: 100vh !important; min-height: 100vh; }
</style>
""", unsafe_allow_html=True)

# ── Load the prototype folder ──────────────────────────────────────
PROTOTYPE_DIR = pathlib.Path(__file__).parent / "prototype"
HTML_FILE     = PROTOTYPE_DIR / "index.html"

def load_prototype_html() -> str:
    """
    Read index.html and inline every local asset it references
    (styles.css, app.mjs, engine.mjs, scenario_data.json,
    admin0-countries.svg) so the page is self-contained inside
    the iframe Streamlit renders.
    """
    html = HTML_FILE.read_text(encoding="utf-8")

    # ── Inline styles.css ──────────────────────────────────────────
    css_path = PROTOTYPE_DIR / "styles.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        html = re.sub(
            r'<link\s+rel="stylesheet"\s+href="\.\/styles\.css[^"]*"\s*/?>',
            f"<style>\n{css}\n</style>",
            html,
            count=1,
        )

    # ── Inline scenario_data.json as a global variable ────────────
    json_path = PROTOTYPE_DIR / "data" / "scenario_data.json"
    if json_path.exists():
        json_text = json_path.read_text(encoding="utf-8")
        injection = (
            f"<script>\n"
            f"window.__AIR2STAY_SCENARIO_DATA__ = {json_text};\n"
            f"</script>\n"
        )
        html = html.replace("<head>", f"<head>\n{injection}", 1)

    # ── Inline admin0-countries.svg as a data URI ─────────────────
    svg_path = PROTOTYPE_DIR / "data" / "admin0-countries.svg"
    if svg_path.exists():
        svg_b64 = base64.b64encode(svg_path.read_bytes()).decode()
        svg_uri = f"data:image/svg+xml;base64,{svg_b64}"
        # Replace any versioned reference to admin0-countries.svg
        html = re.sub(
            r'href="\.\/data\/admin0-countries\.svg[^"]*"',
            f'href="{svg_uri}"',
            html,
        )

    # ── Inline engine.mjs into app.mjs call ───────────────────────
    engine_path = PROTOTYPE_DIR / "engine.mjs"
    app_path    = PROTOTYPE_DIR / "app.mjs"
    if engine_path.exists() and app_path.exists():
        engine_src = engine_path.read_text(encoding="utf-8")
        app_src    = app_path.read_text(encoding="utf-8")

        # Remove the import line that pulls from engine.mjs
        app_src = re.sub(
            r'import\s*\{[^}]+\}\s*from\s*["\']\.\/engine\.mjs[^"\']*["\'];?\n?',
            "",
            app_src,
        )

        # The map is created dynamically inside app.mjs, so the HTML asset
        # replacement above cannot rewrite its SVG URL. Embed the SVG in the
        # generated module as well.
        if svg_path.exists():
            app_src = app_src.replace(
                "./data/admin0-countries.svg?v=20260922-admin0",
                svg_uri,
            )

        combined = (
            "// engine.mjs — inlined\n"
            + engine_src
            + "\n\n// app.mjs — inlined\n"
            + app_src
        )
        combined_b64 = base64.b64encode(combined.encode()).decode()
        combined_uri = f"data:text/javascript;base64,{combined_b64}"

        html = re.sub(
            r'<script type="module" src="\.\/app\.mjs[^"]*">',
            f'<script type="module" src="{combined_uri}">',
            html,
        )

    return html


# ── Render ─────────────────────────────────────────────────────────
try:
    page_html = load_prototype_html()
    # The iframe fills the browser viewport through the CSS above. Its
    # internal document remains scrollable when dashboard content exceeds it.
    viewport_h = 900
    st.components.v1.html(page_html, height=viewport_h, scrolling=True)
except FileNotFoundError:
    st.error(
        "prototype/index.html not found. "
        "Make sure the prototype folder sits next to app.py."
    )
    st.code("Air2Stay/\n├── app.py          ← this file\n└── prototype/\n    ├── index.html\n    ├── app.mjs\n    ├── engine.mjs\n    ├── styles.css\n    └── data/\n        ├── scenario_data.json\n        └── admin0-countries.svg")
