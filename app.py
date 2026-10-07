"""
Air2Stay — DCT Abu Dhabi · NSTI 2026
Serves the self-contained standalone prototype.
Run locally:  streamlit run app.py
"""
import pathlib
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Air2Stay · DCT Abu Dhabi",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome so only the dashboard shows
st.markdown("""
<style>
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; margin: 0 !important;
                   max-width: 100% !important; }
.stApp { overflow: hidden; }
iframe { border: none !important; display: block !important; }
</style>
""", unsafe_allow_html=True)

# Path to the self-contained HTML file
HTML_FILE = pathlib.Path(__file__).parent / "prototype" / "standalone.html"

try:
    html = HTML_FILE.read_text(encoding="utf-8")
    components.html(html, height=960, scrolling=True)
except FileNotFoundError:
    st.error(
        "prototype/standalone.html not found. "
        "Make sure standalone.html is inside the prototype/ folder next to app.py."
    )
    st.markdown("""
    **Expected folder structure:**
    ```
    Air2Stay/
    ├── app.py
    └── prototype/
        └── standalone.html
    ```
    """)
