import streamlit as st
import pandas as pd
import io
import altair as alt
from pathlib import Path
import itertools
import math
import tempfile
import os
from collections import Counter
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Corpus Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
button[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important; min-width: 260px !important;
    transform: translateX(0) !important; visibility: visible !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,500;12..96,600;12..96,700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:      #f7f5f0;
  --surf:    #ffffff;
  --surf2:   #f2f0eb;
  --border:  #e4e0d8;
  --border2: #ccc9c0;
  --text:    #18170f;
  --muted:   #6b6758;
  --muted2:  #a39f92;
  --accent:  #2563eb;
  --r:       7px;
  --r2:      11px;
}

html, body, [class*="css"], * {
  font-family: 'Bricolage Grotesque', sans-serif !important;
}

.stApp { background: var(--bg) !important; }
.block-container { padding: 0 2rem 3rem !important; max-width: 100% !important; }
header[data-testid="stHeader"]  { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
footer { display: none !important; }

/* ─ sidebar ─ */
section[data-testid="stSidebar"] {
  background: var(--surf) !important;
  border-right: 1.5px solid var(--border) !important;
  min-width: 260px !important;
  max-width: 260px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

.sb-section {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--muted2);
  padding: 14px 16px 6px;
  border-top: 1px solid var(--border);
  margin-top: 2px;
}
.sb-section:first-child { border-top: none; margin-top: 0; }

section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
  background: var(--surf2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  font-size: 12.5px !important;
}
section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
  background: var(--text) !important;
  color: #fff !important;
  border-radius: 20px !important;
  font-size: 11px !important;
}
section[data-testid="stSidebar"] label {
  font-size: 11px !important;
  color: var(--muted) !important;
  font-weight: 500 !important;
}
section[data-testid="stSidebar"] .stTextInput input {
  font-size: 12.5px !important;
  background: var(--surf2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
}
section[data-testid="stSidebar"] .stSlider { padding: 0 4px !important; }
section[data-testid="stSidebar"] .stCheckbox label { font-size: 12px !important; }
section[data-testid="stSidebar"] .stButton > button {
  font-size: 11.5px !important;
  background: var(--surf2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  color: var(--muted) !important;
  padding: 5px 12px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--bg) !important;
  border-color: var(--border2) !important;
  color: var(--text) !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
  background: var(--surf2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  font-size: 12px !important;
}

/* ─ topbar ─ */
.topbar {
  background: var(--surf);
  border-bottom: 1.5px solid var(--border);
  padding: 0 28px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 -2rem 0;
}
.logo {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -.4px;
}
.logo-dot { color: var(--muted2); margin: 0 6px; font-weight: 300; }
.logo-sub { font-size: 12px; color: var(--muted); font-weight: 400; }
.kpis { display: flex; gap: 28px; }
.kpi { text-align: right; }
.kpi-n {
  font-size: 16px; font-weight: 700; color: var(--text);
  line-height: 1; letter-spacing: -.5px;
}
.kpi-l {
  font-size: 10px; color: var(--muted2);
  font-family: 'JetBrains Mono', monospace; margin-top: 2px;
}

/* ─ result bar ─ */
.rbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.rbar-n {
  font-size: 18px; font-weight: 700; color: var(--text);
  letter-spacing: -.5px; line-height: 1;
}
.rbar-meta {
  font-size: 12px; color: var(--muted);
  font-family: 'JetBrains Mono', monospace;
  margin-left: 12px;
}

/* ─ active filter chips ─ */
.chips { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 14px; min-height: 0; }
.chip {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--text); color: #fff;
  border-radius: 20px; padding: 3px 10px;
  font-size: 11px; font-weight: 500; line-height: 1.4;
}
.chip-cat { opacity: .4; font-size: 10px; }

/* ─ cross-nav banner ─ */
.xbanner {
  background: var(--surf); border: 1.5px solid var(--border2);
  border-radius: var(--r2); padding: 9px 14px;
  margin-bottom: 14px; font-size: 12px; color: var(--muted);
  display: flex; align-items: center; gap: 8px;
  font-family: 'JetBrains Mono', monospace;
}
.xbanner-code {
  background: #eff6ff; border: 1.5px solid #bfdbfe;
  border-radius: var(--r2); padding: 9px 14px;
  margin-bottom: 14px; font-size: 12px; color: #1e40af;
  display: flex; align-items: center; gap: 8px;
  font-family: 'JetBrains Mono', monospace;
}

/* ─ coding card ─ */
.ccard {
  background: var(--surf);
  border: 1.5px solid var(--border);
  border-radius: var(--r2);
  padding: 14px 16px;
  margin-bottom: 4px;
  transition: border-color .12s;
}
.ccard:hover { border-color: var(--border2); }

.cc-top {
  display: flex; justify-content: space-between;
  align-items: flex-start; gap: 12px; margin-bottom: 9px;
}
.cc-code {
  font-size: 13.5px; font-weight: 700; color: var(--text);
  font-family: 'JetBrains Mono', monospace; letter-spacing: -.2px;
}
.cc-meta {
  font-size: 11px; color: var(--muted2);
  font-family: 'JetBrains Mono', monospace; margin-top: 2px;
}
.cc-xlink {
  font-size: 11px; color: var(--muted2);
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap; flex-shrink: 0;
  border: 1px solid var(--border); border-radius: 20px;
  padding: 2px 9px; cursor: pointer;
}
.cc-xlink:hover { color: var(--text); border-color: var(--border2); }
.cc-excerpt {
  font-size: 12.5px; color: #3d3a30; line-height: 1.65;
  border-left: 2.5px solid var(--border2);
  padding-left: 11px; margin: 0 0 8px; font-style: italic;
}
.cc-rat {
  font-size: 11.5px; color: var(--muted); line-height: 1.55;
  margin-bottom: 8px;
}
.cc-def {
  margin: 8px 0 0; padding: 9px 12px;
  background: var(--surf2); border: 1px solid var(--border);
  border-radius: var(--r);
  font-size: 11px; color: var(--muted); line-height: 1.6;
}
.cc-def-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9.5px; opacity: .55;
  display: block; margin-bottom: 3px; text-transform: uppercase;
  letter-spacing: .06em;
}
.cc-foot {
  display: flex; align-items: center;
  justify-content: space-between;
  padding-top: 10px; border-top: 1px solid var(--border);
  margin-top: 10px;
}
.cc-foot-actions {
  display: flex; gap: 6px; align-items: center; flex-wrap: wrap;
}

/* ─ passage card ─ */
.pcard {
  background: var(--surf);
  border: 1.5px solid var(--border);
  border-radius: var(--r2);
  padding: 15px 17px; margin-bottom: 4px;
  transition: border-color .12s;
}
.pcard:hover { border-color: var(--border2); }
.pc-header {
  display: flex; justify-content: space-between;
  align-items: flex-start; margin-bottom: 11px;
}
.pc-id {
  font-size: 13px; font-weight: 700;
  font-family: 'JetBrains Mono', monospace; color: var(--text);
}
.pc-meta {
  font-size: 11px; font-family: 'JetBrains Mono', monospace;
  color: var(--muted2); margin-top: 3px;
}
.pc-grp-stack { display: flex; flex-wrap: wrap; gap: 4px; max-width: 54%; justify-content: flex-end; }
.pc-excerpt {
  font-size: 12.5px; color: #3d3a30; line-height: 1.65;
  border-left: 2.5px solid var(--border2);
  padding-left: 11px; margin: 0 0 10px; font-style: italic;
}
.pc-codes { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 11px; }
.code-chip {
  padding: 2px 7px; border-radius: 5px;
  background: var(--surf2); border: 1px solid var(--border);
  font-size: 10.5px; font-family: 'JetBrains Mono', monospace;
  color: var(--muted); cursor: default;
}
/* tooltip */
.tt-wrap { position: relative; display: inline-block; }
.tt-wrap .tt {
  display: none; position: absolute; bottom: calc(100% + 8px); left: 0;
  z-index: 9999; background: var(--text); color: #fff;
  border-radius: var(--r); padding: 10px 13px; width: 310px;
  font-size: 11px; line-height: 1.55; pointer-events: none;
  box-shadow: 0 6px 24px rgba(0,0,0,.16); white-space: normal;
}
.tt-wrap .tt-head {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  opacity: .6; display: block; margin-bottom: 5px;
}
.tt-wrap:hover .tt { display: block; }
.pc-foot {
  display: flex; align-items: center;
  justify-content: space-between;
  padding-top: 10px; border-top: 1px solid var(--border);
}
.pc-stats { display: flex; gap: 16px; }
.pc-stat {
  font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--muted);
}
.pc-stat b { color: var(--text); font-weight: 600; }

/* ─ badges ─ */
.bdg {
  display: inline-block; padding: 2px 8px; border-radius: 20px;
  font-size: 10.5px; font-weight: 600; white-space: nowrap;
}

/* ─ section title ─ */
.sec-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: var(--muted2); margin: 20px 0 10px;
}

/* ─ codebook ─ */
.cb-grp-hdr {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 0 7px; border-bottom: 1px solid var(--border);
  margin-bottom: 9px;
}
.cb-grp-name { font-size: 14px; font-weight: 700; color: var(--text); }
.cb-grp-meta { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--muted2); }
.cb-card {
  background: var(--surf); border: 1.5px solid var(--border);
  border-radius: var(--r2); padding: 12px 15px; margin-bottom: 4px;
}
.cb-card:hover { border-color: var(--border2); }
.cb-card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; }
.cb-name { font-size: 13px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: var(--text); }
.cb-id   { font-size: 10.5px; font-family: 'JetBrains Mono', monospace; color: var(--muted2); }
.cb-freq {
  margin-left: auto; font-size: 10.5px; font-family: 'JetBrains Mono', monospace;
  color: var(--muted2); background: var(--surf2);
  border: 1px solid var(--border); border-radius: 20px; padding: 1px 9px;
}
.cb-desc { font-size: 12px; color: var(--muted); line-height: 1.65; }

/* ─ interview detail ─ */
.int-stat-box {
  background: var(--surf); border: 1.5px solid var(--border);
  border-radius: var(--r2); padding: 16px 18px; text-align: center;
}
.int-stat-n { font-size: 28px; font-weight: 700; color: var(--text); letter-spacing: -.8px; line-height: 1; }
.int-stat-l { font-size: 10px; color: var(--muted2); font-family: 'JetBrains Mono', monospace; margin-top: 4px; }

/* ─ pagination ─ */
.pgbar {
  text-align: center; font-size: 12px; font-family: 'JetBrains Mono', monospace;
  color: var(--muted2); padding: 8px 0;
}

/* ─ nav action buttons below cards ─ */
div[data-testid="stHorizontalBlock"] > div > div[data-testid="stButton"] > button {
  font-size: 11px !important;
  padding: 3px 10px !important;
  height: auto !important;
  border-radius: 20px !important;
  background: var(--surf2) !important;
  border: 1px solid var(--border) !important;
  color: var(--muted) !important;
  font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stHorizontalBlock"] > div > div[data-testid="stButton"] > button:hover {
  background: var(--bg) !important;
  border-color: var(--border2) !important;
  color: var(--text) !important;
}

/* ─ streamlit native overrides ─ */
.stDownloadButton > button {
  font-family: 'Bricolage Grotesque', sans-serif !important;
  font-size: 12px !important; font-weight: 600 !important;
  background: var(--text) !important; color: #fff !important;
  border: none !important; border-radius: var(--r) !important;
  padding: 6px 16px !important;
}
.stDownloadButton > button:hover { opacity: .82 !important; }
div[data-baseweb="tab-list"] { display: none !important; }
div[data-baseweb="tab-panel"] { padding: 0 !important; }
.stNumberInput input {
  font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
}
/* ─ native <details> styled as expander ─ */
details.x-expand {
  background: var(--surf2);
  border: 1px solid var(--border);
  border-radius: var(--r);
  margin: 4px 0 8px;
  transition: border-color .12s;
  overflow: hidden;
}
details.x-expand[open] { border-color: var(--border2); }
details.x-expand > summary {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 12px;
  cursor: pointer;
  font-size: 11.5px;
  color: var(--muted);
  font-weight: 500;
  user-select: none;
  outline: none;
}
details.x-expand > summary::-webkit-details-marker { display: none; }
details.x-expand > summary::before {
  content: '›';
  font-size: 15px;
  font-weight: 300;
  color: var(--muted2);
  transition: transform .15s ease;
  display: inline-block;
  line-height: 1;
}
details.x-expand[open] > summary::before { transform: rotate(90deg); }
details.x-expand > summary:hover { color: var(--text); }
details.x-expand > summary:hover::before { color: var(--muted); }
details.x-expand .x-body {
  padding: 0 14px 12px;
  font-size: 12.5px;
  line-height: 1.7;
  color: #3d3a30;
  font-style: italic;
  border-top: 1px solid var(--border);
  padding-top: 10px;
  margin-top: 0;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PALETTE
# ══════════════════════════════════════════════════════════════════════════════
GROUP_COLORS = {
    "1_PROBLEM_IDENTIFICATION":  {"bg":"#dbeafe","fg":"#1e40af","chart":"#3b82f6"},
    "2_SOLUTION_DEVELOPMENT":    {"bg":"#dcfce7","fg":"#166534","chart":"#22c55e"},
    "3_VALUE_PROPOSITION":       {"bg":"#fef9c3","fg":"#854d0e","chart":"#eab308"},
    "4_REVENUE_CAPTURE":         {"bg":"#fee2e2","fg":"#991b1b","chart":"#ef4444"},
    "5_OBSTACLES":               {"bg":"#fce7f3","fg":"#9d174d","chart":"#ec4899"},
    "6_NAVIGATING_OBSTACLES":    {"bg":"#ede9fe","fg":"#5b21b6","chart":"#8b5cf6"},
    "7_ECOSYSTEM_VALUES":        {"bg":"#e0f2fe","fg":"#075985","chart":"#0ea5e9"},
    "8_STARTUP_TRAJECTORY":      {"bg":"#fff7ed","fg":"#9a3412","chart":"#f97316"},
    "9_ENTREPRENEUR_PROFILE":    {"bg":"#f0fdf4","fg":"#14532d","chart":"#16a34a"},
    "10_RELATIONSHIP_CLIENTS":   {"bg":"#fdf4ff","fg":"#6b21a8","chart":"#a855f7"},
    "11_RELATIONSHIP_SUPPORT":   {"bg":"#ecfdf5","fg":"#065f46","chart":"#10b981"},
    "12_REFLEXIVITY":            {"bg":"#f1f5f9","fg":"#334155","chart":"#64748b"},
}
CONF_COLORS = {"high":{"bg":"#dcfce7","fg":"#166534"},"medium":{"bg":"#fef9c3","fg":"#854d0e"},"low":{"bg":"#fee2e2","fg":"#991b1b"}}
CONF_CHART  = {"high":"#22c55e","medium":"#eab308","low":"#ef4444"}
REVIEW_COLORS = {
    "auto":     {"bg":"#fef9c3","fg":"#92400e"},
    "reviewed": {"bg":"#dcfce7","fg":"#166534"},
    "flagged":  {"bg":"#fee2e2","fg":"#991b1b"},
}
GRP_DOMAIN  = list(GROUP_COLORS.keys())
GRP_RANGE   = [v["chart"] for v in GROUP_COLORS.values()]

def short_grp(g):  return g.split("_",1)[-1].replace("_"," ").title() if "_" in g else g
def short_int(iid): return iid.split("_",1)[-1].lower() if "_" in iid else iid

def bdg(label, palette):
    c = palette.get(label, {"bg":"#f0f0f0","fg":"#555"})
    short = label.split("_",1)[-1].replace("_"," ").title() if "_" in label else label
    return f'<span class="bdg" style="background:{c["bg"]};color:{c["fg"]}">{short}</span>'

def review_bdg(status):
    c = REVIEW_COLORS.get(status, {"bg":"#f0f0f0","fg":"#555"})
    lbl = status if status else "—"
    return f'<span class="bdg" style="background:{c["bg"]};color:{c["fg"]};font-size:9.5px">{lbl}</span>'

def code_chip_tt(code_name, cb_def, cb_id):
    cid  = cb_id.get(code_name, "")
    defn = cb_def.get(code_name, "")
    safe_name = code_name.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    if defn:
        d = defn.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')[:400]
        safe_cid = str(cid).replace("&","&amp;").replace("<","&lt;")
        return (f'<span class="tt-wrap"><span class="code-chip">{safe_name}</span>'
                f'<span class="tt"><span class="tt-head">{safe_cid} · {safe_name}</span>{d}{"…" if len(defn)>400 else ""}</span></span>')
    return f'<span class="code-chip">{safe_name}</span>'

def export_xlsx(df, sheet):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name=sheet)
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"

def _local_files_present():
    return all((DATA_DIR / f).exists() for f in
               ["master_corpus.xlsx", "index_passages.xlsx", "CODE_BOOK_v10.xlsx"])

@st.cache_data(show_spinner="Chargement du corpus…")
def load_data(mc_bytes=None, ip_bytes=None, cb_bytes=None):
    if mc_bytes is not None:
        mc = pd.read_excel(io.BytesIO(mc_bytes)).fillna("")
        ip = pd.read_excel(io.BytesIO(ip_bytes)).fillna("")
        cb = pd.read_excel(io.BytesIO(cb_bytes)).fillna("")
    else:
        mc = pd.read_excel(DATA_DIR/"master_corpus.xlsx").fillna("")
        ip = pd.read_excel(DATA_DIR/"index_passages.xlsx").fillna("")
        cb = pd.read_excel(DATA_DIR/"CODE_BOOK_v10.xlsx").fillna("")
    mc["coded_at"] = mc["coded_at"].astype(str)
    mc["line_start"] = pd.to_numeric(mc["line_start"], errors="coerce").fillna(0).astype(int)
    mc["line_end"]   = pd.to_numeric(mc["line_end"],   errors="coerce").fillna(0).astype(int)
    cb = cb[cb["Code_Name"].astype(str).str.strip() != ""]
    return mc, ip, cb

if not _local_files_present():
    if "data_loaded" not in st.session_state:
        st.markdown("### Chargement des données")
        st.caption("Les fichiers de données ne sont pas embarqués dans l'app. Uploadez-les pour continuer.")
        c1, c2, c3 = st.columns(3)
        uf_mc = c1.file_uploader("master_corpus.xlsx", type="xlsx", key="uf_mc")
        uf_ip = c2.file_uploader("index_passages.xlsx", type="xlsx", key="uf_ip")
        uf_cb = c3.file_uploader("CODE_BOOK_v10.xlsx",  type="xlsx", key="uf_cb")
        if not (uf_mc and uf_ip and uf_cb):
            st.stop()
        try:
            df_mc, df_ip, df_cb = load_data(
                mc_bytes=uf_mc.getvalue(),
                ip_bytes=uf_ip.getvalue(),
                cb_bytes=uf_cb.getvalue(),
            )
            st.session_state["data_loaded"] = (df_mc, df_ip, df_cb)
            st.rerun()
        except Exception as e:
            st.error(f"Erreur lors du chargement : {e}")
            st.stop()
    else:
        df_mc, df_ip, df_cb = st.session_state["data_loaded"]
else:
    try:
        df_mc, df_ip, df_cb = load_data()
    except FileNotFoundError:
        st.error("⚠️  Fichiers manquants dans data/")
        st.stop()

@st.cache_data(show_spinner=False)
def compute_cooccurrence(ip_df, top_n=40):
    top_codes = Counter()
    for codes_str in ip_df["codes"]:
        for c in str(codes_str).split(","):
            c = c.strip()
            if c: top_codes[c] += 1
    top_set = {c for c, _ in top_codes.most_common(top_n)}
    pair_counts = Counter()
    for codes_str in ip_df["codes"]:
        codes = [c.strip() for c in str(codes_str).split(",") if c.strip() and c.strip() in top_set]
        for a, b in itertools.combinations(sorted(set(codes)), 2):
            pair_counts[(a, b)] += 1
    rows = [{"code_a": a, "code_b": b, "n": n} for (a, b), n in pair_counts.items()]
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["code_a","code_b","n"])

@st.cache_data(show_spinner=False)
def compute_saturation(mc_df):
    order = mc_df.groupby("interview_id")["coded_at"].min().sort_values().index.tolist()
    seen = set()
    rows = []
    for i, iid in enumerate(order):
        codes_this = set(mc_df[mc_df["interview_id"] == iid]["code_name"].unique())
        new_codes = codes_this - seen
        seen |= codes_this
        rows.append({
            "interview": short_int(iid),
            "order": i + 1,
            "n_cumulative": len(seen),
            "n_new": len(new_codes),
        })
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def compute_ca(mc_df):
    try:
        import prince
    except ImportError:
        return None, None, []
    pivot = mc_df.pivot_table(index="interview_id", columns="code_name", aggfunc="size", fill_value=0)
    n_comp = min(5, len(pivot) - 1)
    ca = prince.CA(n_components=n_comp, n_iter=20, random_state=42)
    ca = ca.fit(pivot)
    row_coords = ca.row_coordinates(pivot).copy()
    col_coords = ca.column_coordinates(pivot).copy()
    row_coords.columns = [f"Dim{i+1}" for i in range(len(row_coords.columns))]
    col_coords.columns = [f"Dim{i+1}" for i in range(len(col_coords.columns))]
    try:
        explained = [v / 100 for v in ca.percentage_of_variance_]
    except AttributeError:
        try:
            explained = list(ca.explained_inertia_)
        except AttributeError:
            ev = list(ca.eigenvalues_)
            total = sum(ev) or 1
            explained = [e / total for e in ev]
    return row_coords, col_coords, explained

def build_network_html(mc_df, ip_df, top_n=50, min_weight=3):
    try:
        import networkx as nx
        from pyvis.network import Network
    except ImportError:
        return None
    # index_passages.codes contains code_ids (e.g. "SUP_CV_3"), not code_names
    id_freq  = mc_df["code_id"].astype(str).value_counts().to_dict()
    id_name  = dict(zip(mc_df["code_id"].astype(str), mc_df["code_name"].astype(str)))
    id_group = dict(zip(mc_df["code_id"].astype(str), mc_df["group"].astype(str)))
    # Top code_ids by passage frequency
    cid_counts = Counter()
    for codes_str in ip_df["codes"]:
        for c in str(codes_str).split(","):
            c = c.strip()
            if c: cid_counts[c] += 1
    top_ids = [c for c, _ in cid_counts.most_common(top_n)]
    top_set = set(top_ids)
    pairs = Counter()
    for codes_str in ip_df["codes"]:
        codes = [c.strip() for c in str(codes_str).split(",") if c.strip() in top_set]
        for a, b in itertools.combinations(sorted(set(codes)), 2):
            pairs[(a, b)] += 1
    import networkx as nx
    G = nx.Graph()
    for cid in top_ids:
        freq  = id_freq.get(cid, 1)
        name  = id_name.get(cid, cid)
        group = id_group.get(cid, "")
        color = GROUP_COLORS.get(group, {}).get("chart", "#888")
        size  = max(10, min(55, 6 + math.log(max(freq, 1)) * 5))
        label = name.replace("_", " ").lower()
        G.add_node(cid,
                   label=label,
                   title=f"<b>{name}</b><br>{freq} codings<br>{short_grp(group)}",
                   size=size,
                   color={"background": color, "border": color,
                          "highlight": {"background": color, "border": "#18170f"}})
    for (a, b), w in pairs.items():
        if w >= min_weight:
            G.add_edge(a, b, value=w, title=f"{w} co-occurrences")
    for node in list(nx.isolates(G)):
        G.remove_node(node)
    if G.number_of_nodes() == 0:
        return None
    from pyvis.network import Network
    net = Network(height="660px", width="100%", bgcolor="#f7f5f0",
                  font_color="#18170f", directed=False, notebook=False)
    net.from_nx(G)
    net.set_options("""
var options = {
  "physics": {
    "enabled": true,
    "solver": "forceAtlas2Based",
    "forceAtlas2Based": {
      "gravitationalConstant": -80,
      "centralGravity": 0.005,
      "springLength": 150,
      "springConstant": 0.08,
      "damping": 0.4,
      "avoidOverlap": 0.6
    },
    "stabilization": {"iterations": 200, "updateInterval": 25, "fit": true}
  },
  "nodes": {"font": {"size": 11, "face": "monospace"}, "borderWidth": 1.5},
  "edges": {
    "color": {"color": "#d4d0c8", "highlight": "#18170f", "hover": "#6b6758"},
    "smooth": {"type": "continuous"},
    "scaling": {"min": 1, "max": 10}
  },
  "interaction": {"hover": true, "tooltipDelay": 120, "hideEdgesOnDrag": true}
}
""")
    tmp = os.path.join(tempfile.gettempdir(), "corpus_net.html")
    net.save_graph(tmp)
    with open(tmp, encoding="utf-8") as f:
        html = f.read()
    try:
        os.unlink(tmp)
    except OSError:
        pass
    return html



ALL_INT    = sorted(df_mc["interview_id"].unique())
ALL_GRP    = sorted(df_mc["group"].unique())
ALL_CODE   = sorted(df_mc["code_name"].unique())
GRP_CNT    = df_mc["group"].value_counts().to_dict()
INT_CNT_MC = df_mc["interview_id"].value_counts().to_dict()
INT_CNT_IP = df_ip["interview_id"].value_counts().to_dict()
CB_DEF     = df_cb.set_index("Code_Name")["Description"].to_dict()
CB_ID      = df_cb.set_index("Code_Name")["ID"].to_dict()
CODE_FREQ  = df_mc["code_name"].value_counts().to_dict()
CN_TO_CIDS = df_mc.groupby("code_name")["code_id"].apply(lambda s: set(s.astype(str))).to_dict()

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
_D = {
    "view": "codings",
    "cross_iid": None,
    "cross_code": None,
    "c_ints":[], "c_grps":[], "c_codes":[], "c_conf":["high","medium","low"],
    "c_text":"", "c_page":1, "c_sort":"Défaut",
    "p_ints":[], "p_grps":[], "p_codes":[], "p_conf":["high","medium","low"],
    "p_nc":(1, int(df_ip["n_codes"].max())),
    "p_ng":(1, int(df_ip["n_groups"].max())),
    "p_text":"", "p_page":1, "p_sort":"Défaut",
    "a_ints":[], "a_grps":[], "a_topn":20,
    "cb_search":"", "cb_grps":[], "cb_sort":"Groupe",
    "i_int": ALL_INT[0] if ALL_INT else None,
    "k_topn": 50, "k_minw": 3, "k_dim1": 1, "k_dim2": 2,
    "k_show_codes": False,
}
for k, v in _D.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_c():
    for k in ["c_ints","c_grps","c_codes","c_conf","c_text","c_page","c_sort"]:
        st.session_state[k] = _D[k]
    st.session_state.c_conf = ["high","medium","low"]
    st.session_state.cross_iid = None
    st.session_state.cross_code = None

def reset_p():
    for k in ["p_ints","p_grps","p_codes","p_conf","p_nc","p_ng","p_text","p_page","p_sort"]:
        st.session_state[k] = _D[k]
    st.session_state.p_conf = ["high","medium","low"]
    st.session_state.cross_iid = None
    st.session_state.cross_code = None

view = st.session_state.view

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    st.markdown("""
    <div style="padding:16px 16px 10px;border-bottom:1px solid var(--border)">
      <div style="font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px">Corpus Explorer</div>
      <div style="font-size:10.5px;color:var(--muted2);font-family:'JetBrains Mono',monospace;margin-top:2px">
        Outil d'exploration du corpus codé pour la recherche sur le déplacement de la valeur
      </div>
    </div>
    """, unsafe_allow_html=True)

    k1,k2,k3,k4 = st.columns(4)
    for col, n, lbl in [(k1,len(ALL_INT),"ent."),(k2,len(df_mc),"cod."),(k3,len(df_ip),"pass."),(k4,len(ALL_CODE),"codes")]:
        col.markdown(f'<div style="text-align:center;padding:8px 0"><div style="font-size:13px;font-weight:700;color:var(--text)">{n:,}</div><div style="font-size:9px;color:var(--muted2);font-family:\'JetBrains Mono\',monospace">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:2px;border-bottom:1px solid var(--border);margin:0 0 4px"></div>', unsafe_allow_html=True)

    if view == "codings":
        st.markdown('<div class="sb-section">Filtres — Codings</div>', unsafe_allow_html=True)

        sel_c_ints = st.multiselect(
            "Entretien", ALL_INT, default=st.session_state.c_ints,
            format_func=short_int, placeholder="Tous", key="w_c_ints",
        )
        st.session_state.c_ints = sel_c_ints

        sel_c_grps = st.multiselect(
            "Groupe analytique", ALL_GRP, default=st.session_state.c_grps,
            format_func=short_grp, placeholder="Tous les groupes", key="w_c_grps",
        )
        st.session_state.c_grps = sel_c_grps

        avail_codes = sorted(
            df_mc[df_mc["group"].isin(sel_c_grps)]["code_name"].unique()
        ) if sel_c_grps else ALL_CODE

        sel_c_codes = st.multiselect(
            f"Code ({len(avail_codes)} dispo.)", avail_codes,
            default=[x for x in st.session_state.c_codes if x in avail_codes],
            placeholder="Tous", key="w_c_codes",
        )
        st.session_state.c_codes = sel_c_codes

        st.markdown("**Confiance**")
        cc1,cc2,cc3 = st.columns(3)
        for col, cf, lbl in [(cc1,"high","High"),(cc2,"medium","Med"),(cc3,"low","Low")]:
            with col:
                v = st.checkbox(lbl, value=cf in st.session_state.c_conf, key=f"w_cc_{cf}")
                if v and cf not in st.session_state.c_conf:
                    st.session_state.c_conf.append(cf)
                elif not v and cf in st.session_state.c_conf:
                    st.session_state.c_conf.remove(cf)

        c_txt = st.text_input("Rechercher dans l'extrait",
                              value=st.session_state.c_text,
                              placeholder="mot-clé…", key="w_c_text")
        if c_txt != st.session_state.c_text:
            st.session_state.c_text = c_txt
            st.session_state.c_page = 1

        c_sort = st.selectbox("Tri", ["Défaut","Confiance H→L","Confiance L→H","Groupe A→Z","Entretien"],
                              index=["Défaut","Confiance H→L","Confiance L→H","Groupe A→Z","Entretien"].index(st.session_state.c_sort),
                              key="w_c_sort")
        st.session_state.c_sort = c_sort

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        if st.button("↺  Réinitialiser", key="c_rst", width='stretch'):
            reset_c(); st.rerun()

    elif view == "passages":
        st.markdown('<div class="sb-section">Filtres — Passages</div>', unsafe_allow_html=True)

        sel_p_ints = st.multiselect(
            "Entretien", ALL_INT, default=st.session_state.p_ints,
            format_func=short_int, placeholder="Tous", key="w_p_ints",
        )
        st.session_state.p_ints = sel_p_ints

        sel_p_grps = st.multiselect(
            "Groupe présent", ALL_GRP, default=st.session_state.p_grps,
            format_func=short_grp, placeholder="Tous les groupes", key="w_p_grps",
        )
        st.session_state.p_grps = sel_p_grps

        avail_p_codes = sorted(
            df_mc[df_mc["group"].isin(sel_p_grps)]["code_name"].unique()
        ) if sel_p_grps else ALL_CODE

        sel_p_codes = st.multiselect(
            f"Code ({len(avail_p_codes)} dispo.)", avail_p_codes,
            default=[x for x in st.session_state.p_codes if x in avail_p_codes],
            placeholder="Tous", key="w_p_codes",
        )
        st.session_state.p_codes = sel_p_codes

        st.markdown("**Confiance min.**")
        pc1,pc2,pc3 = st.columns(3)
        for col, cf, lbl in [(pc1,"high","High"),(pc2,"medium","Med"),(pc3,"low","Low")]:
            with col:
                v = st.checkbox(lbl, value=cf in st.session_state.p_conf, key=f"w_pc_{cf}")
                if v and cf not in st.session_state.p_conf:
                    st.session_state.p_conf.append(cf)
                elif not v and cf in st.session_state.p_conf:
                    st.session_state.p_conf.remove(cf)

        p_nc = st.slider("Nb de codes", 1, int(df_ip["n_codes"].max()),
                         st.session_state.p_nc, key="w_p_nc")
        st.session_state.p_nc = p_nc

        p_ng = st.slider("Nb de groupes", 1, int(df_ip["n_groups"].max()),
                         st.session_state.p_ng, key="w_p_ng")
        st.session_state.p_ng = p_ng

        p_txt = st.text_input("Rechercher dans l'extrait",
                              value=st.session_state.p_text,
                              placeholder="mot-clé…", key="w_p_text")
        if p_txt != st.session_state.p_text:
            st.session_state.p_text = p_txt
            st.session_state.p_page = 1

        p_sort = st.selectbox("Tri", ["Défaut","Codes ↓","Codes ↑","Groupes ↓","Entretien"],
                              index=["Défaut","Codes ↓","Codes ↑","Groupes ↓","Entretien"].index(st.session_state.p_sort),
                              key="w_p_sort")
        st.session_state.p_sort = p_sort

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        if st.button("↺  Réinitialiser", key="p_rst", width='stretch'):
            reset_p(); st.rerun()

    elif view == "analytics":
        st.markdown('<div class="sb-section">Périmètre d\'analyse</div>', unsafe_allow_html=True)

        a_ints = st.multiselect("Entretien", ALL_INT, default=st.session_state.a_ints,
                                format_func=short_int, placeholder="Tous", key="w_a_ints")
        st.session_state.a_ints = a_ints

        a_grps = st.multiselect("Groupe", ALL_GRP, default=st.session_state.a_grps,
                                format_func=short_grp, placeholder="Tous", key="w_a_grps")
        st.session_state.a_grps = a_grps

        a_topn = st.slider("Top N codes", 5, 40, st.session_state.a_topn, key="w_a_topn")
        st.session_state.a_topn = a_topn

    elif view == "codebook":
        st.markdown('<div class="sb-section">Recherche Codebook</div>', unsafe_allow_html=True)

        cb_search = st.text_input("Mot-clé", value=st.session_state.cb_search,
                                  placeholder="nom ou définition…", key="w_cb_search")
        st.session_state.cb_search = cb_search

        cb_grps = st.multiselect("Groupe", ALL_GRP, default=st.session_state.cb_grps,
                                 format_func=short_grp, placeholder="Tous", key="w_cb_grps")
        st.session_state.cb_grps = cb_grps

        cb_sort = st.selectbox("Tri", ["Groupe","Fréquence ↓","A → Z"],
                               index=["Groupe","Fréquence ↓","A → Z"].index(st.session_state.cb_sort),
                               key="w_cb_sort")
        st.session_state.cb_sort = cb_sort

    elif view == "cartographie":
        st.markdown('<div class="sb-section">Carte factorielle</div>', unsafe_allow_html=True)
        k_dim1 = st.selectbox("Axe X", [1,2,3,4,5],
                              index=[1,2,3,4,5].index(st.session_state.k_dim1), key="w_k_dim1")
        st.session_state.k_dim1 = k_dim1
        k_dim2 = st.selectbox("Axe Y", [1,2,3,4,5],
                              index=[1,2,3,4,5].index(st.session_state.k_dim2), key="w_k_dim2")
        st.session_state.k_dim2 = k_dim2
        k_show_codes = st.checkbox("Afficher top codes", value=st.session_state.k_show_codes, key="w_k_show_codes")
        st.session_state.k_show_codes = k_show_codes
        st.markdown('<div class="sb-section">Réseau de codes</div>', unsafe_allow_html=True)
        k_topn = st.slider("Top N codes", 20, 80, st.session_state.k_topn, key="w_k_topn")
        st.session_state.k_topn = k_topn
        k_minw = st.slider("Co-occurrence min.", 1, 15, st.session_state.k_minw, key="w_k_minw")
        st.session_state.k_minw = k_minw

    elif view == "interview":
        st.markdown('<div class="sb-section">Entretien</div>', unsafe_allow_html=True)
        i_int = st.selectbox("Sélectionner", ALL_INT,
                             index=ALL_INT.index(st.session_state.i_int) if st.session_state.i_int in ALL_INT else 0,
                             format_func=short_int, key="w_i_int")
        st.session_state.i_int = i_int

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="topbar">
  <div style="display:flex;align-items:baseline;gap:10px">
    <span class="logo">Corpus Explorer</span>
    <span class="logo-dot">·</span>
    <span class="logo-sub">Outil d'exploration du corpus codé pour la recherche sur le déplacement de la valeur</span>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="kpi-n">{len(ALL_INT)}</div><div class="kpi-l">entretiens</div></div>
    <div class="kpi"><div class="kpi-n">{len(df_mc):,}</div><div class="kpi-l">codings</div></div>
    <div class="kpi"><div class="kpi-n">{len(df_ip)}</div><div class="kpi-l">passages</div></div>
    <div class="kpi"><div class="kpi-n">{len(ALL_CODE)}</div><div class="kpi-l">codes</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

VIEWS = [("codings","🏷  Codings"),("passages","📄  Passages"),("analytics","📊  Analytique"),("codebook","📖  Codebook"),("cartographie","🗺  Carto"),("interview","🔍  Entretien")]
n1,n2,n3,n4,n5,n6,_ = st.columns([1,1,1,1,1,1,1])
for col, (v, lbl) in zip([n1,n2,n3,n4,n5,n6], VIEWS):
    with col:
        if st.button(lbl, key=f"nav_{v}", width='stretch',
                     type="primary" if view==v else "secondary"):
            st.session_state.view = v
            st.session_state.c_page = 1
            st.session_state.p_page = 1
            st.rerun()

st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

def show_chips(items):
    if items:
        html = "".join(f'<span class="chip"><span class="chip-cat">{cat}</span>{val}</span>' for cat,val in items)
        st.markdown(f'<div class="chips">{html}</div>', unsafe_allow_html=True)

def show_xbanner(iid, view_key, count_key):
    if st.session_state.cross_iid:
        c1, c2 = st.columns([8,1])
        with c1:
            st.markdown(f'<div class="xbanner">🔗 cross-nav actif · <b>{iid}</b></div>', unsafe_allow_html=True)
        with c2:
            if st.button("✕", key=f"xclr_{view_key}"):
                st.session_state.cross_iid = None
                st.session_state[view_key] = []
                st.rerun()

def show_code_xbanner(code_name, codes_key):
    if st.session_state.cross_code:
        c1, c2 = st.columns([8,1])
        with c1:
            st.markdown(f'<div class="xbanner-code">🔵 code · <b>{code_name}</b></div>', unsafe_allow_html=True)
        with c2:
            if st.button("✕", key=f"xcode_clr_{codes_key}"):
                st.session_state.cross_code = None
                st.session_state[codes_key] = []
                st.rerun()

def paginate(df, page_key, size):
    n = len(df)
    n_pg = max(1,(n-1)//size+1)
    pg = max(1, min(st.session_state[page_key], n_pg))
    if n_pg > 1:
        pc1,pc2,pc3 = st.columns([2,3,2])
        with pc1:
            if pg > 1 and st.button("← Préc.", key=f"{page_key}_prev"):
                st.session_state[page_key] -= 1; st.rerun()
        with pc2:
            st.markdown(f'<div class="pgbar">Page {pg} / {n_pg} · {n} résultats</div>', unsafe_allow_html=True)
        with pc3:
            if pg < n_pg and st.button("Suiv. →", key=f"{page_key}_next"):
                st.session_state[page_key] += 1; st.rerun()
    return df.iloc[(pg-1)*size : pg*size].reset_index(drop=True)

def altcfg():
    return dict(
        labelFont="JetBrains Mono", titleFont="JetBrains Mono",
        labelFontSize=11, titleFontSize=11,
        labelColor="#6b6758", titleColor="#6b6758",
    )

def mkalt(chart):
    ac = altcfg()
    return (chart
            .configure_axis(**ac, grid=False, gridColor="#ece9e2")
            .configure_view(strokeWidth=0)
            .configure_legend(labelFont="JetBrains Mono", titleFont="JetBrains Mono",
                              labelFontSize=10, titleFontSize=10))

# ══════════════════════════════════════════════════════════════════════════════
#  VIEW: CODINGS
# ══════════════════════════════════════════════════════════════════════════════
if view == "codings":

    fc = df_mc.copy()
    if st.session_state.c_ints:  fc = fc[fc["interview_id"].isin(st.session_state.c_ints)]
    if st.session_state.c_grps:  fc = fc[fc["group"].isin(st.session_state.c_grps)]
    if st.session_state.c_codes: fc = fc[fc["code_name"].isin(st.session_state.c_codes)]
    if st.session_state.c_conf:  fc = fc[fc["confidence"].isin(st.session_state.c_conf)]
    if st.session_state.c_text:  fc = fc[fc["excerpt"].str.contains(st.session_state.c_text, case=False, na=False)]

    # sort
    srt = st.session_state.c_sort
    if srt == "Confiance H→L":
        conf_ord = {"high":0,"medium":1,"low":2}
        fc = fc.copy(); fc["_co"] = fc["confidence"].map(conf_ord); fc = fc.sort_values("_co")
    elif srt == "Confiance L→H":
        conf_ord = {"high":2,"medium":1,"low":0}
        fc = fc.copy(); fc["_co"] = fc["confidence"].map(conf_ord); fc = fc.sort_values("_co")
    elif srt == "Groupe A→Z":
        fc = fc.sort_values(["group","code_name"])
    elif srt == "Entretien":
        fc = fc.sort_values(["interview_id","line_start"])

    chips = []
    for i in st.session_state.c_ints:  chips.append(("ent.",  short_int(i)))
    for g in st.session_state.c_grps:  chips.append(("grp.",  short_grp(g)[:16]))
    for c in st.session_state.c_codes: chips.append(("code",  c[:16]))
    if set(st.session_state.c_conf) != {"high","medium","low"}:
        for cf in st.session_state.c_conf: chips.append(("conf.", cf))
    if st.session_state.c_text: chips.append(("q", f'"{st.session_state.c_text[:14]}"'))
    if srt != "Défaut": chips.append(("tri", srt))
    show_chips(chips)

    if st.session_state.cross_iid:
        show_xbanner(st.session_state.cross_iid, "c_ints", "c_page")
    if st.session_state.cross_code:
        show_code_xbanner(st.session_state.cross_code, "c_codes")

    n_fc = len(fc)
    rb1, rb2 = st.columns([7, 1.5])
    with rb1:
        st.markdown(
            f'<div class="rbar"><span class="rbar-n">{n_fc:,} codings</span>'
            f'<span class="rbar-meta">{fc["interview_id"].nunique()} entretiens · '
            f'{fc["code_name"].nunique()} codes distincts</span></div>',
            unsafe_allow_html=True,
        )
    with rb2:
        if n_fc > 0:
            st.download_button("⬇ Export", export_xlsx(fc,"codings"), "codings_export.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               width='stretch')

    if n_fc == 0:
        st.info("Aucun résultat pour ces filtres.")
    else:
        slic = paginate(fc, "c_page", 40)
        for _, row in slic.iterrows():
            iid       = row["interview_id"]
            exc       = str(row["excerpt"])
            rat       = str(row["rationale"])
            n_p       = INT_CNT_IP.get(iid, 0)
            g_b       = bdg(row["group"], GROUP_COLORS)
            c_b       = bdg(row["confidence"], CONF_COLORS)
            rvw       = review_bdg(str(row.get("review_status","")).strip())
            code_def  = CB_DEF.get(row["code_name"], "")
            def_html  = ""
            if code_def:
                d = code_def[:340] + ("…" if len(code_def)>340 else "")
                safe_d = d.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                def_html = (f'<div class="cc-def"><span class="cc-def-label">définition codebook</span>{safe_d}</div>')

            exc_short = exc[:280] + ("…" if len(exc)>280 else "")
            safe_exc  = exc_short.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            safe_rat  = rat[:280].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            safe_rat += "…" if len(rat)>280 else ""
            safe_code = str(row["code_name"]).replace("&","&amp;").replace("<","&lt;")
            safe_iid  = str(iid).replace("&","&amp;").replace("<","&lt;")
            safe_cid  = str(row["code_id"]).replace("&","&amp;").replace("<","&lt;")

            st.markdown(f"""
            <div class="ccard">
              <div class="cc-top">
                <div>
                  <div class="cc-code">{safe_code}</div>
                  <div class="cc-meta">{safe_iid} · L.{row['line_start']}–{row['line_end']} · {safe_cid}</div>
                </div>
                <span class="cc-xlink">→ {n_p} passages</span>
              </div>
              <div class="cc-excerpt">« {safe_exc} »</div>
              <div class="cc-rat">{safe_rat}</div>
              {def_html}
              <div class="cc-foot">
                <div style="display:flex;gap:5px;align-items:center">{g_b} {c_b} {rvw}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            btn_col, _ = st.columns([2, 6])
            with btn_col:
                if st.button(f"→ {n_p} passages", key=f"xp_{row['coding_id']}",
                             help=f"Voir les passages de {iid}"):
                    st.session_state.cross_iid  = iid
                    st.session_state.p_ints     = [iid]
                    st.session_state.p_page     = 1
                    st.session_state.view = "passages"
                    st.rerun()
            if len(exc) > 280:
                safe_full = exc.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                st.markdown(f'<details class="x-expand"><summary>Extrait complet — {len(exc)} caractères</summary><div class="x-body">« {safe_full} »</div></details>', unsafe_allow_html=True)

            st.markdown('<div style="margin-bottom:6px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  VIEW: PASSAGES
# ══════════════════════════════════════════════════════════════════════════════
elif view == "passages":

    fp = df_ip.copy()
    if st.session_state.p_ints:  fp = fp[fp["interview_id"].isin(st.session_state.p_ints)]
    if st.session_state.p_grps:
        fp = fp[fp["groups"].apply(lambda g: any(x in str(g) for x in st.session_state.p_grps))]
    if st.session_state.p_codes:
        target_cids = set()
        for cn in st.session_state.p_codes:
            target_cids |= CN_TO_CIDS.get(cn, set())
        fp = fp[fp["codes"].apply(
            lambda s: bool({c.strip() for c in str(s).split(",")} & target_cids)
        )]
    if st.session_state.p_conf:  fp = fp[fp["confidence_min"].isin(st.session_state.p_conf)]
    fp = fp[(fp["n_codes"]>=st.session_state.p_nc[0]) & (fp["n_codes"]<=st.session_state.p_nc[1])]
    fp = fp[(fp["n_groups"]>=st.session_state.p_ng[0]) & (fp["n_groups"]<=st.session_state.p_ng[1])]
    if st.session_state.p_text:
        fp = fp[fp["full_excerpt"].str.contains(st.session_state.p_text, case=False, na=False)]

    # sort
    ps = st.session_state.p_sort
    if ps == "Codes ↓":   fp = fp.sort_values("n_codes", ascending=False)
    elif ps == "Codes ↑": fp = fp.sort_values("n_codes", ascending=True)
    elif ps == "Groupes ↓": fp = fp.sort_values("n_groups", ascending=False)
    elif ps == "Entretien": fp = fp.sort_values(["interview_id","passage_id"])

    chips = []
    for i in st.session_state.p_ints:  chips.append(("ent.", short_int(i)))
    for g in st.session_state.p_grps:  chips.append(("grp.", short_grp(g)[:16]))
    for c in st.session_state.p_codes: chips.append(("code", c[:18]))
    if st.session_state.p_text: chips.append(("q", f'"{st.session_state.p_text[:14]}"'))
    nc, ng = st.session_state.p_nc, st.session_state.p_ng
    if nc != (1, int(df_ip["n_codes"].max())): chips.append(("codes", f"{nc[0]}–{nc[1]}"))
    if ng != (1, int(df_ip["n_groups"].max())): chips.append(("grps", f"{ng[0]}–{ng[1]}"))
    if ps != "Défaut": chips.append(("tri", ps))
    show_chips(chips)

    if st.session_state.cross_iid:
        show_xbanner(st.session_state.cross_iid, "p_ints", "p_page")
    if st.session_state.cross_code:
        show_code_xbanner(st.session_state.cross_code, "p_codes")

    n_fp  = len(fp)
    avg_c = fp["n_codes"].mean() if n_fp else 0
    rb1, rb2 = st.columns([7, 1.5])
    with rb1:
        st.markdown(
            f'<div class="rbar"><span class="rbar-n">{n_fp} passages</span>'
            f'<span class="rbar-meta">{fp["interview_id"].nunique()} entretiens · '
            f'moy. {avg_c:.1f} codes/passage</span></div>',
            unsafe_allow_html=True,
        )
    with rb2:
        if n_fp > 0:
            st.download_button("⬇ Export", export_xlsx(fp,"passages"), "passages_export.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               width='stretch')

    if n_fp == 0:
        st.info("Aucun résultat.")
    else:
        slic_p = paginate(fp, "p_page", 25)
        for _, row in slic_p.iterrows():
            iid       = row["interview_id"]
            exc       = str(row["full_excerpt"])
            exc_short = exc[:400] + ("…" if len(exc)>400 else "")
            raw_grps  = [g.strip() for g in str(row["groups"]).split(",") if g.strip()]
            raw_codes = [c.strip() for c in str(row["codes"]).split(",")   if c.strip()]
            grp_badges = "".join(bdg(g, GROUP_COLORS) for g in raw_grps)
            code_chips = "".join(code_chip_tt(c, CB_DEF, CB_ID) for c in raw_codes[:18])
            if len(raw_codes)>18:
                code_chips += f'<span class="code-chip" style="color:var(--muted2)">+{len(raw_codes)-18}</span>'
            conf_b   = bdg(row["confidence_min"], CONF_COLORS)
            n_c_link = INT_CNT_MC.get(iid, 0)

            safe_pid  = str(row["passage_id"]).replace("&","&amp;").replace("<","&lt;")
            safe_iid  = str(iid).replace("&","&amp;").replace("<","&lt;")
            safe_exc  = exc_short.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

            st.markdown(f"""
            <div class="pcard">
              <div class="pc-header">
                <div>
                  <div class="pc-id">{safe_pid}</div>
                  <div class="pc-meta">{safe_iid} · L.{row['lines']} · {row['n_codes']} codes · {row['n_groups']} groupes</div>
                </div>
                <div class="pc-grp-stack">{grp_badges}</div>
              </div>
              <div class="pc-excerpt">« {safe_exc} »</div>
              <div class="pc-codes">{code_chips}</div>
              <div class="pc-foot">
                <div class="pc-stats">
                  <span class="pc-stat">conf. min <b>{row['confidence_min']}</b></span>
                  <span class="pc-stat">explicit <b>{row['n_explicit']}</b></span>
                  <span class="pc-stat">implicit <b>{row['n_implicit']}</b></span>
                  <span class="pc-stat">profil <b>{row['group_profile']}</b></span>
                </div>
                {conf_b}
              </div>
            </div>
            """, unsafe_allow_html=True)

            btn_a, btn_b, _ = st.columns([2, 2, 4])
            with btn_a:
                if st.button(f"→ {n_c_link} codings", key=f"xc_{row['passage_id']}",
                             help=f"Aller aux codings de {iid}"):
                    st.session_state.cross_iid  = iid
                    st.session_state.c_ints     = [iid]
                    st.session_state.c_page     = 1
                    st.session_state.view = "codings"
                    st.rerun()
            with btn_b:
                if st.button(f"Entretien", key=f"xi_{row['passage_id']}",
                             help=f"Profil de {iid}"):
                    st.session_state.i_int = iid
                    st.session_state.view  = "interview"
                    st.rerun()
            if len(exc) > 400:
                safe_full = exc.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                st.markdown(f'<details class="x-expand"><summary>Extrait complet — {len(exc)} caractères</summary><div class="x-body">« {safe_full} »</div></details>', unsafe_allow_html=True)

            st.markdown('<div style="margin-bottom:6px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  VIEW: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif view == "analytics":

    da   = df_mc.copy()
    da_p = df_ip.copy()
    if st.session_state.a_ints:
        da   = da[da["interview_id"].isin(st.session_state.a_ints)]
        da_p = da_p[da_p["interview_id"].isin(st.session_state.a_ints)]
    if st.session_state.a_grps:
        da = da[da["group"].isin(st.session_state.a_grps)]

    a_top = st.session_state.a_topn

    st.markdown(
        f'<div class="rbar"><span class="rbar-n">{len(da):,} codings</span>'
        f'<span class="rbar-meta">{da["interview_id"].nunique()} entretiens · '
        f'{da["code_name"].nunique()} codes</span></div>',
        unsafe_allow_html=True,
    )

    # ── Row 1: Top codes + Group distribution ────────────────────────────────
    c1, c2 = st.columns([3,2])
    with c1:
        st.markdown('<div class="sec-title">Top codes</div>', unsafe_allow_html=True)
        tc = da["code_name"].value_counts().head(a_top).reset_index()
        tc.columns = ["code","n"]
        cgmap = da.drop_duplicates("code_name").set_index("code_name")["group"].to_dict()
        tc["group"] = tc["code"].map(cgmap).fillna("")
        st.altair_chart(
            mkalt(alt.Chart(tc, background="transparent")
            .mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3)
            .encode(
                x=alt.X("n:Q", title="occurrences", axis=alt.Axis(grid=True, gridColor="#ece9e2")),
                y=alt.Y("code:N", sort="-x", title=None, axis=alt.Axis(labelLimit=210)),
                color=alt.Color("group:N", scale=alt.Scale(domain=GRP_DOMAIN,range=GRP_RANGE), legend=None),
                tooltip=["code:N","group:N","n:Q"],
            ).properties(height=max(320,a_top*20), background="transparent")),
            width='stretch',
        )
    with c2:
        st.markdown('<div class="sec-title">Répartition groupes</div>', unsafe_allow_html=True)
        gc = da["group"].value_counts().reset_index()
        gc.columns = ["group","n"]
        gc["short"] = gc["group"].apply(short_grp)
        st.altair_chart(
            mkalt(alt.Chart(gc, background="transparent")
            .mark_arc(innerRadius=54, outerRadius=110)
            .encode(
                theta="n:Q",
                color=alt.Color("group:N",
                    scale=alt.Scale(domain=GRP_DOMAIN,range=GRP_RANGE),
                    legend=alt.Legend(title=None, labelLimit=180, labelFont="JetBrains Mono", labelFontSize=10)),
                tooltip=["short:N","n:Q"],
            ).properties(height=320, background="transparent")),
            width='stretch',
        )

    # ── Row 2: Stacked bar ───────────────────────────────────────────────────
    st.markdown('<div class="sec-title">Codings par entretien × groupe</div>', unsafe_allow_html=True)
    piv = da.groupby(["interview_id","group"]).size().reset_index(name="n")
    piv["sg"] = piv["group"].apply(short_grp)
    order_x = piv.groupby("interview_id")["n"].sum().sort_values(ascending=False).index.tolist()
    st.altair_chart(
        mkalt(alt.Chart(piv, background="transparent")
        .mark_bar()
        .encode(
            x=alt.X("interview_id:N", sort=order_x, title=None,
                    axis=alt.Axis(labelAngle=-35, labelFont="JetBrains Mono", labelFontSize=10, labelColor="#6b6758")),
            y=alt.Y("n:Q", title="codings"),
            color=alt.Color("group:N", scale=alt.Scale(domain=GRP_DOMAIN,range=GRP_RANGE),
                legend=alt.Legend(title=None, labelLimit=180, labelFont="JetBrains Mono", labelFontSize=10)),
            order=alt.Order("group:N"),
            tooltip=["interview_id:N","sg:N","n:Q"],
        ).properties(height=300, background="transparent")),
        width='stretch',
    )

    # ── Row 3: Confidence + Code density ────────────────────────────────────
    c3,c4 = st.columns(2)
    with c3:
        st.markdown('<div class="sec-title">Confiance des codings</div>', unsafe_allow_html=True)
        cfd = da["confidence"].value_counts().reset_index()
        cfd.columns = ["conf","n"]
        st.altair_chart(
            mkalt(alt.Chart(cfd, background="transparent")
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("conf:N", sort=["high","medium","low"], title=None),
                y=alt.Y("n:Q", title="codings"),
                color=alt.Color("conf:N",
                    scale=alt.Scale(domain=list(CONF_CHART.keys()),range=list(CONF_CHART.values())), legend=None),
                tooltip=["conf:N","n:Q"],
            ).properties(height=240, background="transparent")),
            width='stretch',
        )
    with c4:
        st.markdown('<div class="sec-title">Densité codes / passage</div>', unsafe_allow_html=True)
        st.altair_chart(
            mkalt(alt.Chart(da_p, background="transparent")
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#18170f")
            .encode(
                x=alt.X("n_codes:Q", bin=alt.Bin(maxbins=20), title="codes / passage"),
                y=alt.Y("count():Q", title="passages"),
                tooltip=[alt.Tooltip("n_codes:Q",bin=True), "count():Q"],
            ).properties(height=240, background="transparent")),
            width='stretch',
        )

    # ── Row 4: Heatmap ───────────────────────────────────────────────────────
    st.markdown(f'<div class="sec-title">Heatmap top {min(a_top,30)} codes × entretiens</div>', unsafe_allow_html=True)
    tn = list(da["code_name"].value_counts().head(min(a_top,30)).index)
    hd = da[da["code_name"].isin(tn)].groupby(["interview_id","code_name"]).size().reset_index(name="n")
    st.altair_chart(
        mkalt(alt.Chart(hd, background="transparent")
        .mark_rect()
        .encode(
            x=alt.X("interview_id:N", title=None,
                    axis=alt.Axis(labelAngle=-40, labelFont="JetBrains Mono", labelFontSize=10,
                                  labelColor="#6b6758", labelLimit=120)),
            y=alt.Y("code_name:N", sort=tn, title=None,
                    axis=alt.Axis(labelFont="JetBrains Mono", labelFontSize=10, labelColor="#6b6758")),
            color=alt.Color("n:Q", scale=alt.Scale(scheme="greys"), title="n"),
            tooltip=["interview_id:N","code_name:N","n:Q"],
        ).properties(height=max(320,len(tn)*19), background="transparent")),
        width='stretch',
    )

    # ── Row 5: Saturation curve ──────────────────────────────────────────────
    st.markdown('<div class="sec-title">Courbe de saturation théorique</div>', unsafe_allow_html=True)
    sat_src = da if st.session_state.a_ints else df_mc
    sat_df = compute_saturation(sat_src)
    if len(sat_df) > 1:
        base = alt.Chart(sat_df)
        line = base.mark_line(color="#18170f", strokeWidth=2.5, point=True).encode(
            x=alt.X("order:Q", title="entretiens (ordre chronologique)", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("n_cumulative:Q", title="codes uniques cumulés"),
            tooltip=["interview:N","order:Q","n_cumulative:Q","n_new:Q"],
        )
        area = base.mark_area(color="#3b82f6", opacity=0.15).encode(
            x=alt.X("order:Q"),
            y=alt.Y("n_cumulative:Q"),
        )
        st.altair_chart(
            mkalt(alt.layer(area, line).properties(height=280, background="transparent")),
            width='stretch',
        )
        st.markdown(f'<div style="font-size:11px;color:var(--muted2);font-family:\'JetBrains Mono\',monospace;margin-top:-8px">Codes uniques cumulés par entretien · hover = nouveaux codes introduits · saturation à <b>{sat_df["n_cumulative"].max()}</b> codes sur {len(df_cb)} dans le codebook</div>', unsafe_allow_html=True)

    # ── Row 6: Renvoi vers Cartographie ─────────────────────────────────────
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="xbanner-code">🗺 Réseau de co-occurrence et carte factorielle disponibles dans l\'onglet <b>Carto</b></div>', unsafe_allow_html=True)
    if st.button("→ Ouvrir Cartographie", key="a_goto_carto"):
        st.session_state.view = "cartographie"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  VIEW: CODEBOOK
# ══════════════════════════════════════════════════════════════════════════════
elif view == "codebook":

    cb_df = df_cb.copy()
    if st.session_state.cb_grps:
        cb_df = cb_df[cb_df["Group"].isin(st.session_state.cb_grps)]
    if st.session_state.cb_search:
        s = st.session_state.cb_search
        cb_df = cb_df[
            cb_df["Code_Name"].str.contains(s, case=False, na=False) |
            cb_df["Description"].str.contains(s, case=False, na=False)
        ]

    if st.session_state.cb_sort == "Fréquence ↓":
        cb_df = cb_df.copy()
        cb_df["_f"] = cb_df["Code_Name"].map(CODE_FREQ).fillna(0)
        cb_df = cb_df.sort_values("_f", ascending=False)
    elif st.session_state.cb_sort == "A → Z":
        cb_df = cb_df.sort_values("Code_Name")
    else:
        cb_df = cb_df.sort_values(["Group","Code_Name"])

    n_cb = len(cb_df)
    st.markdown(
        f'<div class="rbar"><span class="rbar-n">{n_cb} codes</span>'
        f'<span class="rbar-meta">{cb_df["Group"].nunique()} groupes</span></div>',
        unsafe_allow_html=True,
    )

    if n_cb == 0:
        st.info("Aucun code pour cette recherche.")
    else:
        groups_present = [g for g in ALL_GRP if g in cb_df["Group"].values] \
            if st.session_state.cb_sort == "Groupe" \
            else list(cb_df["Group"].unique())

        for grp in groups_present:
            grp_codes = cb_df[cb_df["Group"] == grp]
            if grp_codes.empty: continue
            total_occ = int(sum(CODE_FREQ.get(c,0) for c in grp_codes["Code_Name"]))
            g_b = bdg(grp, GROUP_COLORS)
            st.markdown(
                f'<div class="cb-grp-hdr">{g_b}'
                f'<span class="cb-grp-meta">{len(grp_codes)} codes · {total_occ:,} occ.</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            for _, row in grp_codes.iterrows():
                freq = CODE_FREQ.get(str(row["Code_Name"]), 0)
                safe_cname = str(row["Code_Name"]).replace("&","&amp;").replace("<","&lt;")
                safe_cid   = str(row["ID"]).replace("&","&amp;").replace("<","&lt;")
                safe_desc  = str(row["Description"]).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                st.markdown(
                    f'<div class="cb-card">'
                    f'<div class="cb-card-head">'
                    f'<span class="cb-name">{safe_cname}</span>'
                    f'<span class="cb-id">{safe_cid}</span>'
                    f'<span class="cb-freq">{freq:,} occ.</span>'
                    f'</div>'
                    f'<div class="cb-desc">{safe_desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                b1, b2, b3, _ = st.columns([2, 2, 2, 2])
                with b1:
                    if freq > 0 and st.button(f"→ {freq} codings", key=f"cb_c_{row['Code_Name']}",
                                              help=f"Voir les codings de {row['Code_Name']}"):
                        st.session_state.cross_code = str(row["Code_Name"])
                        st.session_state.c_codes    = [str(row["Code_Name"])]
                        st.session_state.c_grps     = []
                        st.session_state.c_ints     = []
                        st.session_state.c_page     = 1
                        st.session_state.view = "codings"
                        st.rerun()
                with b2:
                    n_pass = len(df_ip[df_ip["codes"].apply(
                        lambda s: bool({c.strip() for c in str(s).split(",")} & CN_TO_CIDS.get(str(row["Code_Name"]), set()))
                    )])
                    if n_pass > 0 and st.button(f"→ {n_pass} passages", key=f"cb_p_{row['Code_Name']}",
                                                help=f"Voir les passages de {row['Code_Name']}"):
                        st.session_state.cross_code = str(row["Code_Name"])
                        st.session_state.p_codes    = [str(row["Code_Name"])]
                        st.session_state.p_ints     = []
                        st.session_state.p_page     = 1
                        st.session_state.view = "passages"
                        st.rerun()
                with b3:
                    if st.button(f"Entretiens", key=f"cb_i_{row['Code_Name']}",
                                 help=f"Analyser {row['Code_Name']} par entretien"):
                        st.session_state.a_grps = [grp]
                        st.session_state.view   = "analytics"
                        st.rerun()
                st.markdown('<div style="margin-bottom:2px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  VIEW: INTERVIEW DETAIL
# ══════════════════════════════════════════════════════════════════════════════
elif view == "interview":

    iid = st.session_state.i_int
    if not iid:
        st.info("Sélectionnez un entretien dans la barre latérale.")
    else:
        i_mc = df_mc[df_mc["interview_id"] == iid]
        i_ip = df_ip[df_ip["interview_id"] == iid]
        n_coding  = len(i_mc)
        n_passage = len(i_ip)
        n_code    = i_mc["code_name"].nunique()
        n_grp     = i_mc["group"].nunique()
        avg_conf  = (i_mc["confidence"] == "high").sum() / max(n_coding, 1) * 100

        st.markdown(
            f'<div class="rbar"><span class="rbar-n">{short_int(iid)}</span>'
            f'<span class="rbar-meta">{iid}</span></div>',
            unsafe_allow_html=True,
        )

        # KPI row
        kc1,kc2,kc3,kc4,kc5 = st.columns(5)
        for col, n, lbl in [
            (kc1, n_coding,  "codings"),
            (kc2, n_passage, "passages"),
            (kc3, n_code,    "codes uniques"),
            (kc4, n_grp,     "groupes"),
            (kc5, f"{avg_conf:.0f}%", "confiance high"),
        ]:
            col.markdown(
                f'<div class="int-stat-box">'
                f'<div class="int-stat-n">{n}</div>'
                f'<div class="int-stat-l">{lbl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

        # Code frequency chart
        ic1, ic2 = st.columns([3, 2])
        with ic1:
            st.markdown('<div class="sec-title">Codes les plus fréquents</div>', unsafe_allow_html=True)
            i_codes = i_mc["code_name"].value_counts().head(20).reset_index()
            i_codes.columns = ["code","n"]
            cgmap = i_mc.drop_duplicates("code_name").set_index("code_name")["group"].to_dict()
            i_codes["group"] = i_codes["code"].map(cgmap).fillna("")
            st.altair_chart(
                mkalt(alt.Chart(i_codes, background="transparent")
                .mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3)
                .encode(
                    x=alt.X("n:Q", title="occurrences"),
                    y=alt.Y("code:N", sort="-x", title=None, axis=alt.Axis(labelLimit=200)),
                    color=alt.Color("group:N", scale=alt.Scale(domain=GRP_DOMAIN,range=GRP_RANGE), legend=None),
                    tooltip=["code:N","group:N","n:Q"],
                ).properties(height=380, background="transparent")),
                width='stretch',
            )
        with ic2:
            st.markdown('<div class="sec-title">Groupes analytiques</div>', unsafe_allow_html=True)
            i_grps = i_mc["group"].value_counts().reset_index()
            i_grps.columns = ["group","n"]
            i_grps["short"] = i_grps["group"].apply(short_grp)
            st.altair_chart(
                mkalt(alt.Chart(i_grps, background="transparent")
                .mark_arc(innerRadius=40, outerRadius=100)
                .encode(
                    theta="n:Q",
                    color=alt.Color("group:N", scale=alt.Scale(domain=GRP_DOMAIN,range=GRP_RANGE),
                                    legend=alt.Legend(title=None, labelLimit=160, labelFont="JetBrains Mono", labelFontSize=10)),
                    tooltip=["short:N","n:Q"],
                ).properties(height=380, background="transparent")),
                width='stretch',
            )

        # Passages list
        st.markdown(f'<div class="sec-title">{n_passage} passages</div>', unsafe_allow_html=True)
        for _, row in i_ip.iterrows():
            exc = str(row["full_excerpt"])
            exc_short = exc[:400] + ("…" if len(exc)>400 else "")
            raw_codes = [c.strip() for c in str(row["codes"]).split(",") if c.strip()]
            code_chips = "".join(code_chip_tt(c, CB_DEF, CB_ID) for c in raw_codes[:12])
            if len(raw_codes)>12:
                code_chips += f'<span class="code-chip" style="color:var(--muted2)">+{len(raw_codes)-12}</span>'
            conf_b = bdg(row["confidence_min"], CONF_COLORS)
            safe_pid = str(row["passage_id"]).replace("&","&amp;").replace("<","&lt;")
            safe_exc = exc_short.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            st.markdown(f"""
            <div class="pcard">
              <div class="pc-header">
                <div>
                  <div class="pc-id">{safe_pid}</div>
                  <div class="pc-meta">L.{row['lines']} · {row['n_codes']} codes · {row['n_groups']} groupes</div>
                </div>
                {conf_b}
              </div>
              <div class="pc-excerpt">« {safe_exc} »</div>
              <div class="pc-codes">{code_chips}</div>
            </div>
            """, unsafe_allow_html=True)
            if len(exc) > 400:
                safe_full = exc.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                st.markdown(f'<details class="x-expand"><summary>Extrait complet — {len(exc)} caractères</summary><div class="x-body">« {safe_full} »</div></details>', unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom:4px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  VIEW: CARTOGRAPHIE
# ══════════════════════════════════════════════════════════════════════════════
elif view == "cartographie":

    st.markdown(
        f'<div class="rbar"><span class="rbar-n">Cartographie</span>'
        f'<span class="rbar-meta">{len(ALL_INT)} entretiens · {len(ALL_CODE)} codes</span></div>',
        unsafe_allow_html=True,
    )

    # ── Carte factorielle (CA) ────────────────────────────────────────────────
    st.markdown('<div class="sec-title">Carte factorielle des entretiens (Analyse des Correspondances)</div>', unsafe_allow_html=True)

    with st.spinner("Calcul de l'AC…"):
        row_coords, col_coords, explained = compute_ca(df_mc)

    if row_coords is None:
        st.warning("Package `prince` non installé. Lancez `pip install prince`.")
    else:
        d1 = f"Dim{st.session_state.k_dim1}"
        d2 = f"Dim{st.session_state.k_dim2}"

        # Safeguard: fallback if chosen dimension doesn't exist
        if d1 not in row_coords.columns: d1 = row_coords.columns[0]
        if d2 not in row_coords.columns: d2 = row_coords.columns[min(1, len(row_coords.columns)-1)]

        pct1 = explained[int(d1[-1])-1] * 100 if len(explained) >= int(d1[-1]) else 0
        pct2 = explained[int(d2[-1])-1] * 100 if len(explained) >= int(d2[-1]) else 0

        # Build row (interview) dataframe
        row_df = row_coords[[d1, d2]].copy()
        row_df.index.name = "interview_id"
        row_df = row_df.reset_index()
        row_df["label"]   = row_df["interview_id"].apply(short_int)
        row_df["n_cod"]   = row_df["interview_id"].map(INT_CNT_MC).fillna(0).astype(int)
        dom_grp = df_mc.groupby("interview_id")["group"].agg(lambda x: x.value_counts().index[0])
        row_df["dom_grp"] = row_df["interview_id"].map(dom_grp).fillna("")

        # Zero reference lines
        zero_h = alt.Chart(pd.DataFrame({"y":[0]})).mark_rule(
            strokeDash=[4,4], color="#ccc9c0", strokeWidth=1).encode(y=alt.Y("y:Q", title=""))
        zero_v = alt.Chart(pd.DataFrame({"x":[0]})).mark_rule(
            strokeDash=[4,4], color="#ccc9c0", strokeWidth=1).encode(x=alt.X("x:Q", title=""))

        pts = alt.Chart(row_df).mark_point(size=90, filled=True, opacity=0.85).encode(
            x=alt.X(f"{d1}:Q", title=f"Axe {d1[-1]}  ({pct1:.1f}% inertie)"),
            y=alt.Y(f"{d2}:Q", title=f"Axe {d2[-1]}  ({pct2:.1f}% inertie)"),
            color=alt.Color("dom_grp:N", scale=alt.Scale(domain=GRP_DOMAIN, range=GRP_RANGE),
                            legend=alt.Legend(title="Groupe dominant", labelFont="JetBrains Mono",
                                              labelFontSize=10, titleFontSize=10)),
            size=alt.Size("n_cod:Q", scale=alt.Scale(range=[60,260]), legend=None),
            tooltip=[alt.Tooltip("label:N", title="entretien"),
                     alt.Tooltip("dom_grp:N", title="groupe dominant"),
                     alt.Tooltip("n_cod:Q",  title="codings"),
                     alt.Tooltip(f"{d1}:Q",  title=f"Axe {d1[-1]}", format=".3f"),
                     alt.Tooltip(f"{d2}:Q",  title=f"Axe {d2[-1]}", format=".3f")],
        )
        lbls = alt.Chart(row_df).mark_text(align="left", dx=9, dy=-4, fontSize=10,
                                           font="JetBrains Mono", color="#6b6758").encode(
            x=alt.X(f"{d1}:Q"), y=alt.Y(f"{d2}:Q"), text="label:N")

        # Optionally overlay top-30 code positions
        if st.session_state.k_show_codes and col_coords is not None:
            top30 = list(df_mc["code_name"].value_counts().head(30).index)
            col_df = col_coords[[d1, d2]].copy()
            col_df.index.name = "code_name"
            col_df = col_df.reset_index()
            col_df = col_df[col_df["code_name"].isin(top30)]
            col_df["grp"] = col_df["code_name"].map(
                df_mc.drop_duplicates("code_name").set_index("code_name")["group"])
            code_pts = alt.Chart(col_df).mark_point(shape="diamond", size=55,
                                                     filled=True, opacity=0.45).encode(
                x=f"{d1}:Q", y=f"{d2}:Q",
                color=alt.Color("grp:N", scale=alt.Scale(domain=GRP_DOMAIN, range=GRP_RANGE), legend=None),
                tooltip=["code_name:N","grp:N"])
            code_lbl = alt.Chart(col_df).mark_text(fontSize=8, font="JetBrains Mono",
                                                    color="#a39f92", dx=6).encode(
                x=f"{d1}:Q", y=f"{d2}:Q", text="code_name:N")
            ca_chart = alt.layer(zero_h, zero_v, code_pts, code_lbl, pts, lbls)
        else:
            ca_chart = alt.layer(zero_h, zero_v, pts, lbls)

        st.altair_chart(
            mkalt(ca_chart.properties(height=500, background="transparent")),
            width="stretch",
        )
        st.markdown(
            f'<div style="font-size:11px;color:var(--muted2);font-family:\'JetBrains Mono\',monospace;margin-top:-6px">'
            f'Taille des points = nombre de codings · couleur = groupe analytique dominant · '
            f'inertie totale expliquée axes 1+2 = {pct1+pct2:.1f}%</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

    # ── Réseau de co-occurrence ───────────────────────────────────────────────
    st.markdown(f'<div class="sec-title">Réseau de co-occurrence — top {st.session_state.k_topn} codes · seuil {st.session_state.k_minw}</div>', unsafe_allow_html=True)

    with st.spinner("Construction du réseau…"):
        net_html = build_network_html(df_mc, df_ip,
                                      top_n=st.session_state.k_topn,
                                      min_weight=st.session_state.k_minw)

    if net_html is None:
        st.warning("Package `networkx` ou `pyvis` non installé, ou aucun nœud après filtrage.")
    else:
        components.html(net_html, height=680, scrolling=False)
        st.markdown(
            f'<div style="font-size:11px;color:var(--muted2);font-family:\'JetBrains Mono\',monospace">'
            f'Taille des nœuds ∝ fréquence · épaisseur des arêtes ∝ co-occurrence · '
            f'couleur = groupe analytique · hover pour le détail · glisser pour réorganiser</div>',
            unsafe_allow_html=True,
        )
