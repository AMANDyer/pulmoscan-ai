# streamlit_app.py - PulmoScan AI v4
# Features: Grad-CAM | PDF Report | Analytics Dashboard | Scan History

import streamlit as st
import requests
from PIL import Image
import io, base64, json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

API = "http://backend:8000"
#API = "http://127.0.0.1:8000"

st.set_page_config(page_title="PulmoScan AI", page_icon="🫁", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Courier+Prime:wght@400;700&family=Bebas+Neue&display=swap');
:root {
  --bg:#020810;--bg2:#050f1e;--panel:#080f1d;
  --border:rgba(0,200,255,0.1);--border2:rgba(0,200,255,0.25);
  --cyan:#00c8ff;--cyan-dim:rgba(0,200,255,0.12);--cyan-glow:rgba(0,200,255,0.35);
  --red:#ff3b5c;--red-dim:rgba(255,59,92,0.12);
  --green:#00ff88;--green-dim:rgba(0,255,136,0.1);
  --yellow:#f5c518;--yellow-dim:rgba(245,197,24,0.1);
  --text:#cdd8e8;--muted:#3a5068;
  --mono:'Courier Prime',monospace;--sans:'Syne',sans-serif;--display:'Bebas Neue',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:var(--sans);background:var(--bg);color:var(--text)}
#MainMenu,footer,header,.stDeployButton{visibility:hidden}
section[data-testid="stSidebar"]{display:none}
.block-container{padding:0!important;max-width:100%!important}
body::before{content:'';position:fixed;inset:0;z-index:0;
  background-image:linear-gradient(rgba(0,200,255,0.025) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,200,255,0.025) 1px,transparent 1px);
  background-size:40px 40px;animation:gridshift 25s linear infinite;pointer-events:none}
@keyframes gridshift{0%{background-position:0 0}100%{background-position:40px 40px}}
.topbar{position:relative;z-index:10;display:flex;align-items:center;justify-content:space-between;
  padding:0.9rem 2.5rem;border-bottom:1px solid var(--border);background:rgba(2,8,16,0.95);backdrop-filter:blur(20px)}
.logo-main{font-family:var(--display);font-size:1.6rem;letter-spacing:0.08em;color:#fff;text-shadow:0 0 30px var(--cyan-glow)}
.logo-tag{font-family:var(--mono);font-size:0.6rem;color:var(--cyan);letter-spacing:0.2em;
  border:1px solid var(--border2);padding:2px 7px;border-radius:3px;background:var(--cyan-dim);margin-left:8px}
.status-dot{display:flex;align-items:center;gap:6px;font-family:var(--mono);font-size:0.62rem;color:var(--green)}
.status-dot::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--green);
  box-shadow:0 0 8px var(--green);animation:blink 2s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border)!important;padding:0 2.5rem!important;gap:0!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:var(--mono)!important;
  font-size:0.68rem!important;letter-spacing:0.15em!important;text-transform:uppercase!important;
  padding:0.9rem 1.5rem!important;border:none!important;border-bottom:2px solid transparent!important;transition:all 0.2s!important}
.stTabs [aria-selected="true"]{color:var(--cyan)!important;border-bottom-color:var(--cyan)!important;background:transparent!important}
.stTabs [data-baseweb="tab-panel"]{padding:0!important}
.tab-content{padding:2rem 2.5rem;position:relative;z-index:5}
.panel-hdr{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem}
.panel-num{font-family:var(--mono);font-size:0.58rem;color:var(--cyan);background:var(--cyan-dim);
  border:1px solid var(--border2);padding:2px 7px;border-radius:2px;letter-spacing:0.1em}
.panel-title{font-family:var(--mono);font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--muted)}
.panel-line{flex:1;height:1px;background:linear-gradient(90deg,var(--border2),transparent)}
.stFileUploader>div{background:rgba(0,200,255,0.02)!important;border:1px dashed rgba(0,200,255,0.2)!important;border-radius:8px!important;transition:all 0.3s!important}
.stFileUploader>div:hover{border-color:rgba(0,200,255,0.45)!important;background:rgba(0,200,255,0.04)!important}
.stFileUploader label{color:var(--muted)!important;font-family:var(--mono)!important;font-size:0.75rem!important}
.stButton>button{background:transparent!important;border:1px solid var(--cyan)!important;color:var(--cyan)!important;
  font-family:var(--mono)!important;font-size:0.72rem!important;font-weight:700!important;letter-spacing:0.18em!important;
  text-transform:uppercase!important;padding:0.72rem 1.5rem!important;border-radius:4px!important;width:100%!important;transition:all 0.25s!important}
.stButton>button:hover{background:rgba(0,200,255,0.08)!important;box-shadow:0 0 25px rgba(0,200,255,0.2)!important;transform:translateY(-1px)!important}
.res-card{border-radius:10px;padding:1.8rem;margin-bottom:1rem;position:relative;overflow:hidden;animation:fadeup 0.4s ease}
@keyframes fadeup{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.res-card.normal{background:var(--green-dim);border:1px solid rgba(0,255,136,0.28)}
.res-card.tb{background:var(--red-dim);border:1px solid rgba(255,59,92,0.32)}
.res-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.res-card.normal::before{background:linear-gradient(90deg,transparent,var(--green),transparent)}
.res-card.tb::before{background:linear-gradient(90deg,transparent,var(--red),transparent)}
.res-tag{font-family:var(--mono);font-size:0.58rem;letter-spacing:0.25em;text-transform:uppercase;margin-bottom:0.4rem}
.res-tag.normal{color:var(--green)}.res-tag.tb{color:var(--red)}
.res-verdict{font-family:var(--display);font-size:3rem;line-height:1;letter-spacing:0.05em;margin-bottom:0.25rem}
.res-verdict.normal{color:var(--green);text-shadow:0 0 35px rgba(0,255,136,0.35)}
.res-verdict.tb{color:var(--red);text-shadow:0 0 35px rgba(255,59,92,0.35)}
.res-sub{font-size:0.75rem;color:var(--muted);margin-bottom:1.1rem}
.conf-label{font-family:var(--mono);font-size:0.58rem;color:var(--muted);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.35rem;display:flex;justify-content:space-between}
.conf-track{height:4px;border-radius:4px;background:rgba(255,255,255,0.05);overflow:hidden;margin-bottom:0.25rem}
.conf-fill{height:100%;border-radius:4px}
.conf-fill.normal{background:linear-gradient(90deg,#00cc70,var(--green));box-shadow:0 0 8px rgba(0,255,136,0.4)}
.conf-fill.tb{background:linear-gradient(90deg,#cc1a35,var(--red));box-shadow:0 0 8px rgba(255,59,92,0.4)}
.stats-row{display:grid;grid-template-columns:repeat(3,1fr);gap:0.6rem;margin-bottom:1rem}
.stat-box{background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:6px;padding:0.65rem;text-align:center}
.stat-box-val{font-family:var(--display);font-size:1.3rem;color:#fff;line-height:1}
.stat-box-key{font-family:var(--mono);font-size:0.53rem;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;margin-top:3px}
.disclaimer{background:rgba(245,197,24,0.06);border:1px solid rgba(245,197,24,0.2);border-radius:6px;padding:0.75rem 1rem;font-family:var(--mono);font-size:0.63rem;color:#c9a614;line-height:1.6}
.gradcam-hdr{font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--cyan);margin:1.4rem 0 0.8rem;display:flex;align-items:center;gap:8px}
.gradcam-hdr::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(0,200,255,0.3),transparent)}
.gradcam-caption{font-family:var(--mono);font-size:0.6rem;color:var(--muted);text-align:center;margin-top:0.5rem;letter-spacing:0.1em}
.prec-hdr{font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--red);margin:1.4rem 0 0.8rem;display:flex;align-items:center;gap:8px}
.prec-hdr::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(255,59,92,0.3),transparent)}
.prec-grid{display:grid;grid-template-columns:1fr 1fr;gap:0.55rem;margin-bottom:1rem}
.prec-card{background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;padding:0.85rem;transition:border-color 0.2s,background 0.2s;position:relative;overflow:hidden}
.prec-card:hover{border-color:rgba(255,59,92,0.3);background:rgba(255,59,92,0.03)}
.prec-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:2px;background:linear-gradient(180deg,transparent,var(--red),transparent);opacity:0;transition:opacity 0.2s}
.prec-card:hover::before{opacity:1}
.pc-icon{font-size:1.1rem;margin-bottom:0.3rem}.pc-title{font-size:0.72rem;font-weight:700;color:#e2e8f0;margin-bottom:0.2rem}
.pc-body{font-size:0.66rem;color:var(--muted);line-height:1.55}
.emergency{background:linear-gradient(135deg,rgba(255,59,92,0.1),rgba(185,28,28,0.04));border:1px solid rgba(255,59,92,0.32);border-radius:8px;padding:0.9rem 1.1rem;display:flex;gap:0.8rem;align-items:flex-start;margin-top:0.5rem}
.em-title{font-family:var(--mono);font-size:0.62rem;font-weight:700;color:var(--red);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.2rem}
.em-body{font-size:0.68rem;color:var(--muted);line-height:1.6}
.normal-tips{background:var(--green-dim);border:1px solid rgba(0,255,136,0.18);border-radius:8px;padding:1rem 1.2rem;margin-top:0.8rem}
.nt-title{font-family:var(--mono);font-size:0.6rem;color:var(--green);letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.6rem}
.nt-item{font-size:0.7rem;color:var(--muted);line-height:1.8;padding-left:1rem;position:relative}
.nt-item::before{content:'>';position:absolute;left:0;color:var(--green)}
.metric-card{background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:10px;padding:1.4rem;text-align:center;transition:border-color 0.2s}
.metric-card:hover{border-color:var(--border2)}
.metric-val{font-family:var(--display);font-size:2.8rem;color:#fff;line-height:1;text-shadow:0 0 20px rgba(0,200,255,0.2)}
.metric-key{font-family:var(--mono);font-size:0.6rem;color:var(--muted);letter-spacing:0.15em;text-transform:uppercase;margin-top:6px}
.metric-sub{font-family:var(--mono);font-size:0.68rem;margin-top:4px}
.metric-sub.green{color:var(--green)}.metric-sub.red{color:var(--red)}.metric-sub.cyan{color:var(--cyan)}
.hist-row{display:grid;grid-template-columns:1.8fr 1.2fr 1fr 1fr 1fr;gap:0.5rem;align-items:center;padding:0.7rem 1rem;border-radius:6px;margin-bottom:0.4rem;background:rgba(255,255,255,0.02);border:1px solid var(--border);font-size:0.72rem;transition:border-color 0.2s}
.hist-row:hover{border-color:var(--border2)}
.hist-hdr{font-family:var(--mono);font-size:0.58rem;color:var(--muted);letter-spacing:0.12em;text-transform:uppercase}
.badge{display:inline-block;padding:2px 8px;border-radius:3px;font-family:var(--mono);font-size:0.58rem;font-weight:700;letter-spacing:0.1em}
.badge.normal{background:var(--green-dim);color:var(--green);border:1px solid rgba(0,255,136,0.2)}
.badge.tb{background:var(--red-dim);color:var(--red);border:1px solid rgba(255,59,92,0.2)}
.idle{border:1px dashed var(--border);border-radius:8px;padding:3.5rem 2rem;text-align:center}
.idle-icon{font-size:2.5rem;margin-bottom:0.8rem;opacity:0.25}
.idle-text{font-family:var(--mono);font-size:0.68rem;color:var(--muted);letter-spacing:0.15em}
.stSpinner>div{border-top-color:var(--cyan)!important}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────────

def fetch_analytics():
    try:
        r = requests.get(f"{API}/analytics", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"total": 0, "normal": 0, "tb": 0, "history": []}


def generate_pdf(result, confidence, raw_score, inference_ms, filename, gradcam_b64=None):
    buf = io.BytesIO()
    W, H = A4
    c = rl_canvas.Canvas(buf, pagesize=A4)
    BG=colors.HexColor("#020810"); PANEL=colors.HexColor("#080f1d"); DARK=colors.HexColor("#0a1929")
    CYAN=colors.HexColor("#00c8ff"); RED=colors.HexColor("#ff3b5c"); GREEN=colors.HexColor("#00ff88")
    MUTED=colors.HexColor("#3a5068"); YELLOW=colors.HexColor("#f5c518")
    ACCENT = RED if result == "TUBERCULOSIS" else GREEN
    is_tb  = result == "TUBERCULOSIS"

    # BG
    c.setFillColor(BG); c.rect(0,0,W,H,fill=1,stroke=0)
    # Top bar
    c.setFillColor(CYAN); c.rect(0,H-4*mm,W,4*mm,fill=1,stroke=0)
    # Header panel
    c.setFillColor(DARK); c.rect(0,H-50*mm,W,46*mm,fill=1,stroke=0)
    # Logo
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",26); c.drawString(15*mm,H-22*mm,"PULMOSCAN AI")
    c.setFillColor(CYAN); c.setFont("Courier-Bold",7.5); c.drawString(15*mm,H-29*mm,"TUBERCULOSIS SCREENING REPORT  //  AI-POWERED DIAGNOSTICS")
    # Meta
    now = datetime.now()
    for i, line in enumerate([f"Date : {now.strftime('%B %d, %Y')}",f"Time : {now.strftime('%H:%M:%S')}",f"File : {filename}",f"Model: MobileNetV2  Threshold: 0.50"]):
        c.setFillColor(MUTED); c.setFont("Courier",7.5); c.drawRightString(W-15*mm,H-20*mm-(i*5.5*mm),line)

    # Result box
    c.setFillColor(PANEL); c.roundRect(10*mm,H-80*mm,W-20*mm,26*mm,4*mm,fill=1,stroke=0)
    c.setFillColor(ACCENT); c.rect(10*mm,H-80*mm,2*mm,26*mm,fill=1,stroke=0)
    c.setFillColor(ACCENT); c.setFont("Courier-Bold",8); c.drawString(17*mm,H-57*mm,"DIAGNOSIS RESULT")
    label = "NEGATIVE — No TB Indicators Detected" if not is_tb else "POSITIVE — TB Indicators Detected"
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",18); c.drawString(17*mm,H-67*mm,label)
    # Pill
    px=W-68*mm; c.setFillColor(ACCENT); c.roundRect(px,H-70*mm,53*mm,13*mm,3*mm,fill=1,stroke=0)
    c.setFillColor(BG); c.setFont("Helvetica-Bold",13); c.drawCentredString(px+26.5*mm,H-64.5*mm,f"{round(confidence*100,1)}% Confidence")

    # Metrics
    def mbox(x,y,val,key,col):
        c.setFillColor(PANEL); c.roundRect(x,y,42*mm,20*mm,3*mm,fill=1,stroke=0)
        c.setFillColor(col); c.setFont("Helvetica-Bold",15); c.drawCentredString(x+21*mm,y+13*mm,str(val))
        c.setFillColor(MUTED); c.setFont("Courier",6.5); c.drawCentredString(x+21*mm,y+5.5*mm,key)
    mbox(10*mm,H-108*mm,f"{round(confidence*100,1)}%","CONFIDENCE",ACCENT)
    mbox(56*mm,H-108*mm,round(raw_score,4),"RAW SCORE",CYAN)
    mbox(102*mm,H-108*mm,f"{inference_ms}ms","INFERENCE TIME",YELLOW)
    mbox(148*mm,H-108*mm,result,"RESULT",ACCENT)

    # Bar
    by=H-116*mm
    c.setFillColor(MUTED); c.setFont("Courier",7); c.drawString(10*mm,by+4*mm,"CONFIDENCE SCALE"); c.drawRightString(W-10*mm,by+4*mm,f"{round(confidence*100,1)}%")
    c.setFillColor(DARK); c.roundRect(10*mm,by-2*mm,W-20*mm,5*mm,2*mm,fill=1,stroke=0)
    c.setFillColor(ACCENT); c.roundRect(10*mm,by-2*mm,(W-20*mm)*confidence,5*mm,2*mm,fill=1,stroke=0)

    # Grad-CAM
    cam_y = H-165*mm
    if gradcam_b64:
        c.setFillColor(PANEL); c.roundRect(10*mm,cam_y,W-20*mm,42*mm,4*mm,fill=1,stroke=0)
        c.setFillColor(CYAN); c.setFont("Courier-Bold",7.5); c.drawString(15*mm,cam_y+37*mm,"GRAD-CAM EXPLAINABILITY — AI ATTENTION HEATMAP")
        img_buf2 = io.BytesIO(base64.b64decode(gradcam_b64))
        c.drawImage(ImageReader(img_buf2),12*mm,cam_y+3*mm,width=W-24*mm,height=32*mm,preserveAspectRatio=True)

    # Precautions / tips
    py = H-215*mm if gradcam_b64 else H-175*mm
    if is_tb:
        c.setFillColor(RED); c.setFont("Courier-Bold",9); c.drawString(10*mm,py+3*mm,"RECOMMENDED PRECAUTIONS")
        c.setFillColor(RED); c.rect(10*mm,py-1*mm,W-20*mm,0.4*mm,fill=1,stroke=0)
        precs=[("Wear N95 Mask","Use N95/surgical masks in all shared spaces. TB spreads via airborne droplets."),
               ("Seek Immediate Care","Visit a pulmonologist now. Early DOTS therapy dramatically improves outcomes."),
               ("Self-Isolate","Stay home, avoid crowds and immunocompromised contacts until cleared."),
               ("Confirmatory Testing","Sputum smear, GeneXpert MTB/RIF, or IGRA blood test for definitive diagnosis."),
               ("Complete Treatment","Full 6-month RHEZ antibiotic course. Stopping early causes drug resistance."),
               ("Ventilate Spaces","Open windows, use HEPA filters. TB bacilli survive in enclosed poorly-ventilated spaces.")]
        for i,(t,b) in enumerate(precs):
            col=i%2; row=i//2
            bx=(10+col*95)*mm; by2=py-(row+1)*18*mm
            c.setFillColor(DARK); c.roundRect(bx,by2,90*mm,15*mm,2*mm,fill=1,stroke=0)
            c.setFillColor(RED); c.setFont("Helvetica-Bold",7.5); c.drawString(bx+3*mm,by2+9*mm,t)
            c.setFillColor(MUTED); c.setFont("Courier",6.5)
            words=b.split(); line=""; ly=by2+4.5*mm
            for w in words:
                test=line+w+" "
                if c.stringWidth(test,"Courier",6.5)<84*mm: line=test
                else:
                    c.drawString(bx+3*mm,ly,line.strip()); ly-=3.5*mm; line=w+" "
            if line: c.drawString(bx+3*mm,ly,line.strip())
    else:
        c.setFillColor(GREEN); c.setFont("Courier-Bold",9); c.drawString(10*mm,py+3*mm,"PREVENTIVE GUIDELINES")
        tips=["Maintain BCG vaccination schedule. Annual TB screening if in high-risk zones.",
              "Balanced nutrition and adequate sleep strengthen immune defenses against TB.",
              "Avoid prolonged unprotected contact with patients showing chronic cough.",
              "Monitor symptoms: persistent cough 3+ weeks, night sweats, weight loss."]
        c.setFillColor(MUTED); c.setFont("Courier",8)
        for i,t in enumerate(tips):
            c.drawString(12*mm,py-6*mm-(i*7*mm),f">  {t}")

    # Disclaimer
    c.setFillColor(colors.HexColor("#1a1400")); c.roundRect(10*mm,18*mm,W-20*mm,12*mm,3*mm,fill=1,stroke=0)
    c.setFillColor(YELLOW); c.setFont("Courier-Bold",7); c.drawString(14*mm,27*mm,"MEDICAL DISCLAIMER")
    c.setFillColor(colors.HexColor("#a07a00")); c.setFont("Courier",6.5)
    c.drawString(14*mm,22.5*mm,"This report is generated by an AI model for research and screening assistance only. It does not constitute a clinical diagnosis.")
    c.setFillColor(CYAN); c.rect(0,0,W,3*mm,fill=1,stroke=0)
    c.save(); buf.seek(0)
    return buf


# ── TOPBAR ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div style="display:flex;align-items:baseline;gap:6px">
    <div class="logo-main">PULMOSCAN AI</div>
    <div class="logo-tag">v4.0</div>
  </div>
  <div style="display:flex;align-items:center;gap:2rem">
    <div style="font-family:var(--mono);font-size:0.62rem;color:var(--muted)">GRAD-CAM &nbsp;·&nbsp; PDF REPORTS &nbsp;·&nbsp; ANALYTICS</div>
    <div class="status-dot">SYSTEM ONLINE</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔬  Diagnostics", "📊  Analytics Dashboard", "🗂  Scan History"])


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 — DIAGNOSTICS
# ══════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1.15], gap="large")

    with col_l:
        st.markdown("""<div class="panel-hdr"><div class="panel-num">01</div>
          <div class="panel-title">Upload Radiograph</div><div class="panel-line"></div></div>""", unsafe_allow_html=True)
        uploaded = st.file_uploader("Drop chest X-ray  PNG / JPG / JPEG", type=["png","jpg","jpeg"], label_visibility="visible")
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            w, h = image.size; kb = uploaded.size // 1024
            st.image(image, use_column_width=True)
            st.markdown(f"""<div style="font-family:var(--mono);font-size:0.62rem;color:var(--muted);padding:0.6rem 0.8rem;
              border:1px solid var(--border);border-radius:6px;background:rgba(0,200,255,0.02);margin-top:0.6rem;line-height:2">
              FILE &nbsp;<span style="color:var(--cyan)">{uploaded.name}</span><br>
              DIMS &nbsp;<span style="color:var(--cyan)">{w} x {h} px</span><br>
              SIZE &nbsp;<span style="color:var(--cyan)">{kb} KB</span></div>""", unsafe_allow_html=True)
            run = st.button("INITIATE ANALYSIS")
        else:
            st.markdown('<div class="idle"><div class="idle-icon">XRAY</div><div class="idle-text">AWAITING RADIOGRAPH INPUT</div></div>', unsafe_allow_html=True)
            run = False

    with col_r:
        st.markdown("""<div class="panel-hdr"><div class="panel-num">02</div>
          <div class="panel-title">Diagnostic Output</div><div class="panel-line"></div></div>""", unsafe_allow_html=True)

        if not uploaded:
            st.markdown('<div class="idle"><div class="idle-icon">AI</div><div class="idle-text">RESULTS APPEAR AFTER ANALYSIS</div></div>', unsafe_allow_html=True)
        elif run:
            with st.spinner("Running inference + Grad-CAM..."):
                try:
                    uploaded.seek(0)
                    files = {"file": ("xray.jpg", uploaded.read(), "image/jpeg")}
                    resp  = requests.post(f"{API}/predict", files=files, timeout=90)
                    if resp.status_code == 200:
                        data    = resp.json()
                        result  = data["result"]
                        conf    = data["confidence"]
                        raw     = data.get("raw_score", conf)
                        ms      = data.get("inference_ms", "N/A")
                        gcam    = data.get("gradcam")
                        pct     = round(conf * 100, 1)
                        cls     = "normal" if result == "NORMAL" else "tb"
                        verdict = "NORMAL" if result == "NORMAL" else "TB DETECTED"
                        tag     = "NEGATIVE" if result == "NORMAL" else "POSITIVE"

                        st.markdown(f"""
                        <div class="res-card {cls}">
                          <div class="res-tag {cls}">{tag}</div>
                          <div class="res-verdict {cls}">{verdict}</div>
                          <div class="res-sub">{"No TB indicators detected in this radiograph." if result == "NORMAL" else "Possible TB indicators found. Immediate follow-up required."}</div>
                          <div class="conf-label"><span>Confidence Score</span><span>{pct}%</span></div>
                          <div class="conf-track"><div class="conf-fill {cls}" style="width:{pct}%"></div></div>
                        </div>
                        <div class="stats-row">
                          <div class="stat-box"><div class="stat-box-val">{pct}%</div><div class="stat-box-key">Confidence</div></div>
                          <div class="stat-box"><div class="stat-box-val">{round(raw,3)}</div><div class="stat-box-key">Raw Score</div></div>
                          <div class="stat-box"><div class="stat-box-val">{ms}</div><div class="stat-box-key">Infer. ms</div></div>
                        </div>
                        <div class="disclaimer">NOTICE — AI screening only. Not a clinical diagnosis. Consult a licensed physician.</div>
                        """, unsafe_allow_html=True)

                        if gcam:
                            st.markdown('<div class="gradcam-hdr">Grad-CAM Explainability</div>', unsafe_allow_html=True)
                            st.image(base64.b64decode(gcam), use_column_width=True)
                            st.markdown('<div class="gradcam-caption">Red/Yellow regions = high model attention · Left: Original | Center: Heatmap | Right: Overlay</div>', unsafe_allow_html=True)

                        if result == "TUBERCULOSIS":
                            st.markdown("""
                            <div class="prec-hdr">Recommended Precautions</div>
                            <div class="prec-grid">
                              <div class="prec-card"><div class="pc-icon">mask</div><div class="pc-title">Wear N95 Mask</div><div class="pc-body">Use N95 or surgical masks in all shared spaces. TB spreads via airborne droplets.</div></div>
                              <div class="prec-card"><div class="pc-icon">hosp</div><div class="pc-title">Seek Immediate Care</div><div class="pc-body">Visit a pulmonologist now. Early DOTS therapy dramatically improves outcomes.</div></div>
                              <div class="prec-card"><div class="pc-icon">home</div><div class="pc-title">Self-Isolate</div><div class="pc-body">Stay home, avoid crowds and contact with immunocompromised individuals.</div></div>
                              <div class="prec-card"><div class="pc-icon">test</div><div class="pc-title">Confirmatory Test</div><div class="pc-body">Sputum smear, GeneXpert MTB/RIF, or IGRA blood test for definitive diagnosis.</div></div>
                              <div class="prec-card"><div class="pc-icon">rx</div><div class="pc-title">Complete Treatment</div><div class="pc-body">Full 6-month RHEZ antibiotic course. Stopping early causes drug resistance.</div></div>
                              <div class="prec-card"><div class="pc-icon">air</div><div class="pc-title">Ventilate Spaces</div><div class="pc-body">Open windows, use HEPA filters. TB bacilli survive in enclosed spaces.</div></div>
                            </div>
                            <div class="emergency"><div><div class="em-title">Notify Health Authorities</div>
                            <div class="em-body">TB is notifiable. Inform close contacts for screening.<br>
                            India TB Helpline: <strong style="color:#fca5a5">1800-11-6666</strong> &nbsp; who.int/tb</div></div></div>""", unsafe_allow_html=True)
                            st.error("HIGH-RISK FINDING — Seek medical attention immediately.")
                        else:
                            st.balloons()
                            st.markdown("""<div class="normal-tips">
                              <div class="nt-title">Preventive Guidelines</div>
                              <div class="nt-item">Maintain BCG vaccination. Annual screening in high-risk zones.</div>
                              <div class="nt-item">Balanced nutrition strengthens immune defenses against TB.</div>
                              <div class="nt-item">Avoid prolonged contact with patients showing chronic cough.</div>
                              <div class="nt-item">Watch for: cough 3+ weeks, night sweats, unexplained weight loss.</div>
                            </div>""", unsafe_allow_html=True)
                            st.success("Scan appears normal — no TB indicators detected.")

                        # PDF
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("""<div class="panel-hdr"><div class="panel-num">03</div>
                          <div class="panel-title">Download Report</div><div class="panel-line"></div></div>""", unsafe_allow_html=True)
                        with st.spinner("Generating PDF..."):
                            pdf = generate_pdf(result, conf, raw, ms, uploaded.name, gcam)
                        fname = f"PulmoScan_{result}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        st.download_button("DOWNLOAD DIAGNOSTIC REPORT (PDF)", data=pdf, file_name=fname, mime="application/pdf")

                    else:
                        st.error(f"Backend error {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Start FastAPI on port 8000.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.markdown('<div class="idle"><div class="idle-icon">GO</div><div class="idle-text">PRESS INITIATE ANALYSIS TO BEGIN</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("""<div class="panel-hdr"><div class="panel-num">LIVE</div>
      <div class="panel-title">Analytics Dashboard</div><div class="panel-line"></div></div>""", unsafe_allow_html=True)

    analytics = fetch_analytics()
    total  = analytics.get("total", 0)
    normal = analytics.get("normal", 0)
    tb     = analytics.get("tb", 0)
    hist   = analytics.get("history", [])
    tb_pct  = round(tb/total*100,1) if total>0 else 0
    avg_conf= round(sum(h["confidence"] for h in hist)/len(hist)*100,1) if hist else 0
    avg_ms  = round(sum(h.get("inference_ms",0) for h in hist)/len(hist),1) if hist else 0

    m1,m2,m3,m4 = st.columns(4,gap="small")
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-val">{total}</div><div class="metric-key">Total Scans</div><div class="metric-sub cyan">All time</div></div>',unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-val">{normal}</div><div class="metric-key">Normal Cases</div><div class="metric-sub green">{round(100-tb_pct,1)}% of total</div></div>',unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="metric-val">{tb}</div><div class="metric-key">TB Positive</div><div class="metric-sub red">{tb_pct}% rate</div></div>',unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_ms}ms</div><div class="metric-key">Avg Inference</div><div class="metric-sub cyan">{avg_conf}% avg conf</div></div>',unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if total == 0:
        st.markdown('<div class="idle"><div class="idle-icon">CHART</div><div class="idle-text">RUN SCANS TO SEE ANALYTICS</div></div>',unsafe_allow_html=True)
    else:
        ca, cb = st.columns(2, gap="large")
        with ca:
            st.markdown("""<div class="panel-hdr"><div class="panel-num">A</div>
              <div class="panel-title">Case Distribution</div><div class="panel-line"></div></div>""",unsafe_allow_html=True)
            fig,ax=plt.subplots(figsize=(5,4))
            fig.patch.set_facecolor("#020810"); ax.set_facecolor("#080f1d")
            vals=[normal,tb] if tb>0 else [normal,0.0001]
            wedges,texts,autotexts=ax.pie(vals,labels=["Normal","TB+"],colors=["#00ff88","#ff3b5c"],
              autopct="%1.1f%%",startangle=90,wedgeprops=dict(linewidth=2,edgecolor="#020810"),
              textprops=dict(color="#cdd8e8",fontsize=9,fontfamily="monospace"))
            for at in autotexts: at.set_color("#020810"); at.set_fontweight("bold"); at.set_fontsize(9)
            ax.set_title("Case Distribution",color="#00c8ff",fontsize=10,fontfamily="monospace",pad=12)
            plt.tight_layout(); st.pyplot(fig); plt.close(fig)

        with cb:
            st.markdown("""<div class="panel-hdr"><div class="panel-num">B</div>
              <div class="panel-title">Confidence Over Time</div><div class="panel-line"></div></div>""",unsafe_allow_html=True)
            if len(hist)>=2:
                confs=[h["confidence"]*100 for h in hist[-30:]]
                results=[h["result"] for h in hist[-30:]]
                x=list(range(len(confs)))
                cc=["#00ff88" if r=="NORMAL" else "#ff3b5c" for r in results]
                fig2,ax2=plt.subplots(figsize=(5,4))
                fig2.patch.set_facecolor("#020810"); ax2.set_facecolor("#080f1d")
                ax2.plot(x,confs,color="#00c8ff",linewidth=1.5,alpha=0.4)
                ax2.scatter(x,confs,c=cc,s=40,zorder=5,edgecolors="#020810",linewidths=0.5)
                ax2.axhline(50,color="#3a5068",linestyle="--",linewidth=0.8,alpha=0.6)
                ax2.set_xlabel("Scan Index",color="#3a5068",fontsize=8,fontfamily="monospace")
                ax2.set_ylabel("Confidence %",color="#3a5068",fontsize=8,fontfamily="monospace")
                ax2.set_title("Recent 30 Scans",color="#00c8ff",fontsize=10,fontfamily="monospace",pad=12)
                ax2.tick_params(colors="#3a5068",labelsize=7)
                for sp in ax2.spines.values(): sp.set_edgecolor("#0a1929")
                ax2.set_ylim(0,105); ax2.grid(axis="y",color="#0a1929",linewidth=0.5)
                n_p=mpatches.Patch(color="#00ff88",label="Normal"); t_p=mpatches.Patch(color="#ff3b5c",label="TB+")
                ax2.legend(handles=[n_p,t_p],facecolor="#080f1d",edgecolor="#0a1929",labelcolor="#cdd8e8",fontsize=7)
                plt.tight_layout(); st.pyplot(fig2); plt.close(fig2)
            else:
                st.markdown('<div class="idle" style="margin-top:0"><div class="idle-icon">CHART</div><div class="idle-text">NEED 2+ SCANS FOR CHART</div></div>',unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 3 — SCAN HISTORY
# ══════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("""<div class="panel-hdr"><div class="panel-num">LOG</div>
      <div class="panel-title">Scan History</div><div class="panel-line"></div></div>""",unsafe_allow_html=True)

    analytics = fetch_analytics()
    hist = list(reversed(analytics.get("history",[])))
    if not hist:
        st.markdown('<div class="idle"><div class="idle-icon">LOG</div><div class="idle-text">NO SCAN HISTORY YET</div></div>',unsafe_allow_html=True)
    else:
        st.markdown("""<div class="hist-row" style="background:rgba(0,200,255,0.04);border-color:rgba(0,200,255,0.15)">
          <div class="hist-hdr">Timestamp</div><div class="hist-hdr">File</div>
          <div class="hist-hdr">Result</div><div class="hist-hdr">Confidence</div><div class="hist-hdr">Infer. ms</div></div>""",unsafe_allow_html=True)
        for entry in hist[:50]:
            ts=entry.get("timestamp","")[:19].replace("T"," ")
            fn=entry.get("filename","N/A")[:22]
            res=entry.get("result","N/A")
            cf=round(entry.get("confidence",0)*100,1)
            ims=entry.get("inference_ms","N/A")
            cls="normal" if res=="NORMAL" else "tb"
            col=("var(--green)" if cls=="normal" else "var(--red)")
            st.markdown(f"""<div class="hist-row">
              <div style="font-family:var(--mono);font-size:0.65rem;color:var(--muted)">{ts}</div>
              <div style="font-family:var(--mono);font-size:0.65rem;color:var(--text)">{fn}</div>
              <div><span class="badge {cls}">{res}</span></div>
              <div style="font-family:var(--mono);font-size:0.7rem;color:{col}">{cf}%</div>
              <div style="font-family:var(--mono);font-size:0.65rem;color:var(--muted)">{ims}ms</div></div>""",unsafe_allow_html=True)
        st.markdown(f"""<div style="font-family:var(--mono);font-size:0.6rem;color:var(--muted);margin-top:1rem;
          text-align:right;letter-spacing:0.1em">SHOWING {min(50,len(hist))} OF {len(hist)} RECORDS</div>""",unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
