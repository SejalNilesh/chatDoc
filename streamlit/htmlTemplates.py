"""
htmlTemplates.py — DocMind AI
Light theme, minimal SaaS aesthetic.
Inspired by: Notion, Linear, Perplexity, Vercel, ChatGPT.
"""

# =============================================================================
# GLOBAL CSS
# =============================================================================

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* ── Design tokens ── */
:root {
  --font-sans:      'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-display:   'Plus Jakarta Sans', -apple-system, sans-serif;

  --bg-page:        #f7f7f5;
  --bg-surface:     #ffffff;
  --bg-muted:       #f3f3f1;
  --bg-hover:       #efefed;

  --border-subtle:  #e8e8e5;
  --border-default: #d8d8d5;

  --text-primary:   #1a1a18;
  --text-secondary: #6b6b68;
  --text-muted:     #a0a09d;
  --text-on-accent: #ffffff;

  --accent:         #4f46e5;
  --accent-light:   #eef2ff;
  --accent-border:  #c7d2fe;
  --accent-hover:   #4338ca;

  --success:        #16a34a;
  --success-bg:     #f0fdf4;
  --success-border: #bbf7d0;

  --shadow-xs:      0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm:      0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md:      0 4px 12px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04);

  --radius-sm:      6px;
  --radius-md:      10px;
  --radius-lg:      14px;
  --radius-xl:      18px;
}

/* ── Base ── */
html, body, [class*="css"] {
  font-family: var(--font-sans) !important;
  background-color: var(--bg-page) !important;
  color: var(--text-primary) !important;
  -webkit-font-smoothing: antialiased !important;
}

.stApp {
  background: var(--bg-page) !important;
}

/* Thin top accent line */
.stApp::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: var(--border-default);
  z-index: 999;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-surface) !important;
  border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] * {
  color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stMarkdown p {
  color: var(--text-secondary) !important;
  font-size: 0.82rem !important;
  line-height: 1.6 !important;
}
[data-testid="stSidebarContent"] {
  padding: 1.5rem 1.25rem !important;
}

/* ── Sidebar typography ── */
.sidebar-wordmark {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  margin-bottom: 0.2rem;
}
.sidebar-wordmark span {
  color: var(--accent);
}
.sidebar-tagline {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
  display: block;
}
.sidebar-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 1.25rem 0;
}
.sidebar-section-label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.6rem;
  display: block;
}
.file-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.7rem;
  border-radius: var(--radius-sm);
  background: var(--bg-muted);
  border: 1px solid var(--border-subtle);
  margin-bottom: 0.4rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
}
.file-pill-icon {
  width: 18px;
  height: 18px;
  background: var(--accent-light);
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.file-pill-icon svg {
  width: 10px;
  height: 10px;
  fill: var(--accent);
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--bg-surface) !important;
  border: 1.5px dashed var(--border-default) !important;
  border-radius: var(--radius-lg) !important;
  padding: 0.75rem !important;
  transition: border-color 0.15s ease, background 0.15s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important;
  background: var(--accent-light) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
  font-size: 0.82rem !important;
  color: var(--text-secondary) !important;
}

/* ── Buttons ── */
.stButton > button {
  font-family: var(--font-sans) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  border-radius: var(--radius-md) !important;
  padding: 0.45rem 1rem !important;
  transition: all 0.15s ease !important;
  letter-spacing: 0.01em !important;
  cursor: pointer !important;
}

/* Primary button */
.stButton:first-child > button {
  background: var(--accent) !important;
  color: var(--text-on-accent) !important;
  border: 1px solid var(--accent) !important;
  box-shadow: var(--shadow-xs) !important;
}
.stButton:first-child > button:hover {
  background: var(--accent-hover) !important;
  border-color: var(--accent-hover) !important;
  box-shadow: var(--shadow-sm) !important;
  transform: translateY(-1px) !important;
}
.stButton:first-child > button:active {
  transform: translateY(0) !important;
  box-shadow: none !important;
}

/* Secondary / ghost button */
.stButton:last-child > button {
  background: var(--bg-surface) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border-default) !important;
  box-shadow: var(--shadow-xs) !important;
}
.stButton:last-child > button:hover {
  background: var(--bg-hover) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-default) !important;
}

/* ── Inputs ── */
[data-testid="stChatInput"] textarea,
.stTextInput input {
  font-family: var(--font-sans) !important;
  font-size: 0.88rem !important;
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-default) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-lg) !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stChatInput"] textarea:focus,
.stTextInput input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
  outline: none !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  font-family: var(--font-sans) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  color: var(--text-secondary) !important;
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-md) !important;
}
.streamlit-expanderContent {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-subtle) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
  padding: 0.75rem !important;
}

/* ── Spinner ── */
.stSpinner > div {
  border-top-color: var(--accent) !important;
}

/* ── Alerts ── */
.stAlert {
  background: var(--bg-surface) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border-subtle) !important;
  font-size: 0.84rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 10px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }

/* Keep header visible so sidebar reopen button remains accessible */
header {
  visibility: visible !important;
  background: transparent !important;
  z-index: 1000 !important;
}

/* Sidebar reopen / collapse control */
[data-testid="collapsedControl"] {
  display: flex !important;
  position: fixed !important;
  top: 14px !important;
  left: 14px !important;
  width: 38px !important;
  height: 38px !important;
  align-items: center !important;
  justify-content: center !important;
  border-radius: 10px !important;
  border: 1px solid var(--border-subtle) !important;
  background: var(--bg-surface) !important;
  box-shadow: var(--shadow-sm) !important;
  z-index: 99999 !important;
}

[data-testid="collapsedControl"]:hover {
  background: var(--bg-hover) !important;
  border-color: var(--border-default) !important;
  transform: translateY(-1px) !important;
}

[data-testid="collapsedControl"] svg {
  width: 18px !important;
  height: 18px !important;
  color: var(--text-primary) !important;
}

[data-testid="stDecoration"] { display: none; }

/* =====================================================================
   WELCOME SCREEN
   ===================================================================== */
.welcome-wrap {
  max-width: 560px;
  margin: 6rem auto 0;
  padding: 0 1.5rem;
}
.welcome-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--accent-light);
  border: 1px solid var(--accent-border);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 1.5rem;
}
.welcome-title {
  font-family: var(--font-display);
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.03em;
  line-height: 1.2;
  margin: 0 0 0.75rem;
}
.welcome-title em {
  color: var(--accent);
  font-style: normal;
}
.welcome-desc {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 2.5rem;
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.feature-item {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.75rem 0.9rem;
  box-shadow: var(--shadow-xs);
}
.feature-item-label {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-primary);
}
.feature-item-desc {
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 2px;
}

/* =====================================================================
   CHAT BUBBLES
   ===================================================================== */
.chat-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 1.25rem 0;
}
.chat-row.user-row {
  flex-direction: row-reverse;
}
.chat-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 2px;
}
.user-avatar {
  background: var(--accent);
  color: var(--text-on-accent);
  letter-spacing: 0.02em;
}
.bot-avatar {
  background: var(--bg-muted);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}
.bubble {
  max-width: 76%;
  padding: 0.7rem 1rem;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  line-height: 1.65;
  word-break: break-word;
}
.user-bubble {
  background: var(--accent);
  color: var(--text-on-accent);
  border-bottom-right-radius: var(--radius-sm);
  box-shadow: var(--shadow-xs);
}
.bot-bubble {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-bottom-left-radius: var(--radius-sm);
  box-shadow: var(--shadow-xs);
}

/* =====================================================================
   SOURCE CITATION CARDS
   ===================================================================== */
.source-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius-md);
  padding: 0.7rem 0.9rem;
  margin-bottom: 0.5rem;
  box-shadow: var(--shadow-xs);
}
.source-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 0.35rem;
}
.source-filename {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-sans);
}
.source-page-badge {
  font-size: 0.68rem;
  font-weight: 500;
  background: var(--accent-light);
  color: var(--accent);
  border: 1px solid var(--accent-border);
  padding: 1px 7px;
  border-radius: 999px;
  white-space: nowrap;
}
.source-snippet {
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.55;
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.35rem;
  margin-top: 0.35rem;
}

/* =====================================================================
   SUMMARY CARDS
   ===================================================================== */
.section-heading {
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin: 1.5rem 0 0.75rem;
}
.summary-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1rem 1.2rem;
  margin-bottom: 0.75rem;
  box-shadow: var(--shadow-xs);
}
.summary-card-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.5rem;
}
.summary-card p {
  font-size: 0.87rem;
  color: var(--text-secondary);
  line-height: 1.65;
  margin: 0;
}
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 0.25rem;
}
.tag {
  font-size: 0.73rem;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 999px;
}
.tag-topic {
  background: var(--accent-light);
  color: var(--accent);
  border: 1px solid var(--accent-border);
}
.tag-concept {
  background: var(--success-bg);
  color: var(--success);
  border: 1px solid var(--success-border);
}
</style>
"""


# =============================================================================
# TEMPLATE HELPERS
# =============================================================================

def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def get_user_message_html(message: str) -> str:
    """Render a right-aligned user chat bubble."""
    return f"""
<div class="chat-row user-row">
  <div class="chat-avatar user-avatar">You</div>
  <div class="bubble user-bubble">{_esc(message)}</div>
</div>"""


def get_bot_message_html(message: str) -> str:
    """Render a left-aligned assistant chat bubble."""
    safe = _esc(message).replace("\n", "<br>")
    return f"""
<div class="chat-row">
  <div class="chat-avatar bot-avatar">AI</div>
  <div class="bubble bot-bubble">{safe}</div>
</div>"""


def get_source_card_html(filename: str, page, snippet: str) -> str:
    """Render a source citation card with filename, page badge, and snippet."""
    return f"""
<div class="source-card">
  <div class="source-card-header">
    <span class="source-filename">{_esc(str(filename))}</span>
    <span class="source-page-badge">Page {page}</span>
  </div>
  <div class="source-snippet">{_esc(snippet)}</div>
</div>"""


def get_welcome_html() -> str:
    """Render the welcome / empty-state screen."""
    features = [
        ("Multi-PDF chat",     "Ask across all documents"),
        ("Source citations",   "Every answer is grounded"),
        ("Streaming answers",  "Responses appear live"),
        ("Persistent index",   "No re-embedding on reload"),
        ("Auto summaries",     "One-click overview"),
        ("MMR retrieval",      "Diverse, accurate results"),
    ]
    cards = "".join(
        f'<div class="feature-item">'
        f'<div class="feature-item-label">{label}</div>'
        f'<div class="feature-item-desc">{desc}</div>'
        f'</div>'
        for label, desc in features
    )
    return f"""
<div class="welcome-wrap">
  <div class="welcome-badge">Beta</div>
  <h1 class="welcome-title">Chat with your <em>documents</em></h1>
  <p class="welcome-desc">
    Upload one or more PDFs in the sidebar, click Process, then ask anything.
    Every answer includes source references so you can verify exactly where
    information came from.
  </p>
  <div class="feature-grid">{cards}</div>
</div>"""


# =============================================================================
# LEGACY COMPATIBILITY
# Keep these so any code still referencing the old names doesn't break.
# =============================================================================

bot_template = """
<div class="chat-row">
  <div class="chat-avatar bot-avatar">AI</div>
  <div class="bubble bot-bubble">{{MSG}}</div>
</div>"""

user_template = """
<div class="chat-row user-row">
  <div class="chat-avatar user-avatar">You</div>
  <div class="bubble user-bubble">{{MSG}}</div>
</div>"""


