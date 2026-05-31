"""
htmlTemplates.py — DocMind AI
Modern dark theme with professional SaaS aesthetics.
Improvement #2: Complete UI / UX overhaul.
"""

# ─── Global CSS ───────────────────────────────────────────────────────────────

css = """
<style>
/* ── Import fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── CSS Variables ── */
:root {
  --bg-primary:    #0d0f14;
  --bg-secondary:  #13161e;
  --bg-card:       #1a1e2a;
  --bg-card-hover: #1f2436;
  --border:        #252a3a;
  --accent-1:      #6c63ff;
  --accent-2:      #00d4aa;
  --accent-3:      #ff6b6b;
  --text-primary:  #e8eaf0;
  --text-secondary:#8b90a8;
  --text-muted:    #555b74;
  --user-bubble:   #1e2540;
  --bot-bubble:    #141824;
  --radius-lg:     16px;
  --radius-md:     10px;
  --radius-sm:     6px;
  --shadow-glow:   0 0 24px rgba(108,99,255,0.15);
  --font-display:  'Syne', sans-serif;
  --font-body:     'DM Sans', sans-serif;
}

/* ── Base overrides ── */
html, body, [class*="css"] {
  font-family: var(--font-body) !important;
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
}

.stApp {
  background: var(--bg-primary) !important;
}

/* Animated gradient background strip */
.stApp::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-1), var(--accent-2), var(--accent-3), var(--accent-1));
  background-size: 200% 100%;
  animation: shimmer 4s linear infinite;
  z-index: 999;
}
@keyframes shimmer {
  0%   { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
  padding-top: 1rem !important;
}
[data-testid="stSidebar"] * {
  color: var(--text-primary) !important;
}

.sidebar-header {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.25rem;
  padding: 0 1rem;
}

.sidebar-sub {
  font-size: 0.8rem;
  color: var(--text-muted) !important;
  padding: 0 1rem;
  margin-bottom: 1.5rem;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--bg-card) !important;
  border: 2px dashed var(--border) !important;
  border-radius: var(--radius-lg) !important;
  transition: border-color 0.2s ease;
  padding: 1rem;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent-1) !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--accent-1), #8a84ff) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-display) !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 0.55rem 1.2rem !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 14px rgba(108,99,255,0.3) !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(108,99,255,0.45) !important;
  background: linear-gradient(135deg, #7a71ff, #9990ff) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
}

/* Secondary / clear button */
.stButton:last-child > button {
  background: var(--bg-card) !important;
  color: var(--text-secondary) !important;
  box-shadow: none !important;
  border: 1px solid var(--border) !important;
}
.stButton:last-child > button:hover {
  border-color: var(--accent-3) !important;
  color: var(--accent-3) !important;
  background: var(--bg-card) !important;
}

/* ── Text input / chat input ── */
[data-testid="stChatInput"] textarea,
.stTextInput input {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-body) !important;
  transition: border-color 0.2s;
}
[data-testid="stChatInput"] textarea:focus,
.stTextInput input:focus {
  border-color: var(--accent-1) !important;
  box-shadow: 0 0 0 2px rgba(108,99,255,0.15) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-secondary) !important;
  font-size: 0.85rem !important;
}
.streamlit-expanderContent {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
}

/* ── Spinner ── */
.stSpinner > div {
  border-top-color: var(--accent-1) !important;
}

/* ── Alert / info boxes ── */
.stAlert {
  background: var(--bg-card) !important;
  border-radius: var(--radius-md) !important;
}

/* ── Section title ── */
.section-title {
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--text-primary);
  margin: 1.5rem 0 0.75rem;
}

/* ─────────────── Welcome Screen ─────────────────────────────── */
.welcome-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 2rem;
  text-align: center;
  animation: fadeInUp 0.7s ease both;
}
@keyframes fadeInUp {
  from { opacity:0; transform:translateY(20px); }
  to   { opacity:1; transform:translateY(0);    }
}
.welcome-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 0 20px rgba(108,99,255,0.5));
}
.welcome-title {
  font-family: var(--font-display);
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent-1) 30%, var(--accent-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.75rem;
}
.welcome-sub {
  font-size: 1.1rem;
  color: var(--text-secondary);
  line-height: 1.7;
  max-width: 480px;
  margin-bottom: 2.5rem;
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  max-width: 520px;
  width: 100%;
}
.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 0.75rem 0.9rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s;
}
.feature-card:hover {
  border-color: var(--accent-1);
  color: var(--text-primary);
  background: var(--bg-card-hover);
}

/* ─────────────── Chat Bubbles ─────────────────────────────────── */
.chat-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin: 1rem 0;
  animation: fadeInUp 0.3s ease both;
}
.chat-row.user-row {
  flex-direction: row-reverse;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}
.user-avatar {
  background: linear-gradient(135deg, var(--accent-1), #8a84ff);
  box-shadow: 0 0 12px rgba(108,99,255,0.4);
}
.bot-avatar {
  background: linear-gradient(135deg, var(--accent-2), #00a884);
  box-shadow: 0 0 12px rgba(0,212,170,0.3);
}
.bubble {
  max-width: 78%;
  padding: 0.9rem 1.1rem;
  border-radius: var(--radius-lg);
  font-size: 0.9rem;
  line-height: 1.65;
  word-break: break-word;
}
.user-bubble {
  background: var(--user-bubble);
  border: 1px solid rgba(108,99,255,0.2);
  color: var(--text-primary);
  border-top-right-radius: 4px;
}
.bot-bubble {
  background: var(--bot-bubble);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-top-left-radius: 4px;
}

/* ─────────────── Source Citation Cards ─────────────────────────── */
.source-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent-2);
  border-radius: var(--radius-md);
  padding: 0.8rem 1rem;
  margin-bottom: 0.6rem;
  font-size: 0.82rem;
}
.source-label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.78rem;
  color: var(--accent-2);
  margin-bottom: 0.35rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.source-snippet {
  color: var(--text-secondary);
  line-height: 1.55;
}

/* ─────────────── Summary Cards ─────────────────────────────────── */
.summary-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.3rem;
  margin-bottom: 0.75rem;
  animation: fadeInUp 0.4s ease both;
}
.summary-label {
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent-1);
  margin-bottom: 0.5rem;
}
.summary-card p {
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.65;
  margin: 0;
}
.topic-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.25rem;
}
.topic-tag {
  background: rgba(108,99,255,0.15);
  border: 1px solid rgba(108,99,255,0.3);
  color: #a09cff;
  font-size: 0.77rem;
  font-weight: 500;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
}
.concept-tag {
  background: rgba(0,212,170,0.12);
  border: 1px solid rgba(0,212,170,0.3);
  color: var(--accent-2);
  font-size: 0.77rem;
  font-weight: 500;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
}

/* ── Hide default streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
"""

# ─── Template helpers ──────────────────────────────────────────────────────────

def get_user_message_html(message: str) -> str:
    """Render a user chat bubble."""
    safe_msg = message.replace("<", "&lt;").replace(">", "&gt;")
    return f"""
    <div class="chat-row user-row">
        <div class="avatar user-avatar">👤</div>
        <div class="bubble user-bubble">{safe_msg}</div>
    </div>
    """


def get_bot_message_html(message: str) -> str:
    """Render a bot chat bubble."""
    # Allow basic markdown-like line breaks but escape HTML
    safe_msg = message.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    return f"""
    <div class="chat-row bot-row">
        <div class="avatar bot-avatar">🤖</div>
        <div class="bubble bot-bubble">{safe_msg}</div>
    </div>
    """


def get_source_card_html(filename: str, page, snippet: str) -> str:
    """Render a source citation card."""
    safe_snippet = snippet.replace("<", "&lt;").replace(">", "&gt;")
    return f"""
    <div class="source-card">
        <div class="source-label">📄 {filename} &nbsp;|&nbsp; Page {page}</div>
        <div class="source-snippet">{safe_snippet}</div>
    </div>
    """


# ── Legacy exports for backward compatibility ──────────────────────────────────
# (These match the original variable names so nothing breaks if referenced elsewhere)

bot_template = """
<div class="chat-row bot-row">
    <div class="avatar bot-avatar">🤖</div>
    <div class="bubble bot-bubble">{{MSG}}</div>
</div>
"""

user_template = """
<div class="chat-row user-row">
    <div class="avatar user-avatar">👤</div>
    <div class="bubble user-bubble">{{MSG}}</div>
</div>
"""
