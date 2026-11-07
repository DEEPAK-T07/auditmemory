import json, pathlib
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from src import agent, config, llm
from src.eval import score_text, TRAPS
from src.memory import get_memory, LocalMemory, HindsightMemory

# Page setup with modern layout
st.set_page_config(
    page_title="AuditMemory | AI Compliance & Audit Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished presentation
st.markdown("""
<style>
    /* Main container and font styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Banner / Hero */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f766e 100%);
        padding: 24px 28px;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-subtitle {
        font-size: 0.98rem;
        color: #cbd5e1;
        margin-top: 6px;
        line-height: 1.45;
    }
    .hero-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }
    .hero-tag {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(4px);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Comparison Side-by-Side Cards */
    .comparison-card {
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
    }
    .card-off {
        background: #fffaf0;
        border: 1px solid #fed7aa;
        border-top: 4px solid #f97316;
    }
    .card-on {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-top: 4px solid #10b981;
    }
    .card-header-off {
        color: #c2410c;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-header-on {
        color: #047857;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-caption {
        font-size: 0.82rem;
        color: #64748b;
        margin-bottom: 14px;
        line-height: 1.35;
    }
    .card-content {
        color: #1e293b;
        font-size: 0.92rem;
        line-height: 1.6;
        flex-grow: 1;
        white-space: pre-wrap;
    }
    
    /* Memory pill tags */
    .mem-item {
        border-left: 4px solid #0d9488;
        padding: 10px 14px;
        margin: 8px 0;
        background: #f8fafc;
        border-radius: 0 8px 8px 0;
        font-size: 0.88rem;
        color: #1e293b;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .mem-badge {
        display: inline-block;
        padding: 2px 7px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 4px;
        margin-right: 6px;
    }
    .badge-finding { background: #fee2e2; color: #991b1b; }
    .badge-ticket { background: #fef3c7; color: #92400e; }
    .badge-policy { background: #e0e7ff; color: #3730a3; }
    .badge-test { background: #dcfce7; color: #166534; }
    .badge-feedback { background: #f3e8ff; color: #6b21a8; }
    .badge-slack { background: #e2e8f0; color: #334155; }
    
    /* Score banner */
    .metric-box {
        background: #ffffff;
        border-radius: 10px;
        padding: 14px 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-lbl {
        font-size: 0.8rem;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    
    /* Tabs styling polish */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def memory():
    return get_memory()

mem = memory()
PRESETS = [
    "What should I worry about before the audit?",
    "Which past findings might repeat this year?",
    "What evidence should we prepare and in what format?"
]
ss = st.session_state
ss.setdefault("q", PRESETS[0])
ss.setdefault("res", None)
ss.setdefault("after", None)

# --- SIDEBAR PRESENTATION ---
with st.sidebar:
    st.markdown("## 🛡️ **AuditMemory**")
    st.caption("Autonomous Compliance & Audit Preparation Agent")
    
    st.markdown("""
    <div style='background:#f8fafc; border: 1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:12px;'>
        <div style='font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:600;'>Audited Organization</div>
        <div style='font-weight:700; color:#0f172a; font-size:0.95rem; margin-top:2px;'>Northwind Payments</div>
        <div style='font-size:0.8rem; color:#475569;'>120 employees • SOC 2 Type II</div>
    </div>
    """, unsafe_allow_html=True)

    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown(f"**Fieldwork:**  \n📅 `{config.AUDIT_START}`")
    with col_sb2:
        st.markdown(f"**As Of:**  \n🕒 `{config.TODAY}`")
        
    st.divider()
    
    st.markdown("### ⚙️ Engine Status")
    is_hindsight = isinstance(mem, HindsightMemory)
    mem_color = "#10b981" if is_hindsight else "#0284c7"
    mem_icon = "🌐" if is_hindsight else "⚡"
    st.markdown(f"**Memory Engine:**  \n<span style='color:{mem_color}; font-weight:600;'>{mem_icon} {mem.name}</span>", unsafe_allow_html=True)
    
    if config.GEMINI_API_KEY:
        llm_name = f"Google Gemini (`{config.PRIMARY_MODEL}`)"
    elif config.GROQ_API_KEY:
        llm_name = f"Groq (`{config.PRIMARY_MODEL}`)"
    else:
        llm_name = "Offline Demo Engine (Deterministic Fallback)"
    st.markdown(f"**Inference:**  \n`{llm_name}`")
    
    if isinstance(mem, LocalMemory):
        st.markdown("<div style='font-size:0.75rem; color:#64748b; margin-top:4px;'>Running in zero-friction demo mode. No API keys required for full functionality.</div>", unsafe_allow_html=True)
        if st.button("🧹 Reset Demo Feedback Memory", use_container_width=True):
            LocalMemory.reset_feedback()
            st.cache_resource.clear()
            ss.res = ss.after = None
            st.toast("Demo feedback memory cleared!", icon="🧹")
            st.rerun()
            
    st.divider()
    show_score = st.checkbox("🎯 Show Judge Trap Scorecard", value=True)
    show_audit_stats = st.checkbox("📊 Show Audit Dataset Stats", value=True)
    
    if show_audit_stats:
        st.caption("Active Audit Corpus:")
        st.markdown("""
        - 📄 **10** SOC 2 Controls
        - 🔍 **8** Past Findings (2024–2025)
        - 🎟️ **10** Remediation Tickets
        - 📋 **8** Control Tests (Pass/Fail/Overdue)
        - 📜 **5** Policy Changes
        - 💬 **8** Slack Audit Snippets
        """)

# --- MAIN HERO BANNER ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">
        <span>🛡️ AuditMemory</span>
        <span style="font-size: 0.85rem; background: #059669; padding: 3px 10px; border-radius: 12px; font-weight: 600;">HACKATHON DEMO</span>
    </div>
    <div class="hero-subtitle">
        An AI Compliance & Audit Agent that remembers regulatory requirements, multi-year audit findings, remediation proofs, and control execution history to eliminate repeat audit failures.
    </div>
    <div class="hero-tags">
        <span class="hero-tag">🎯 SOC 2 Type II</span>
        <span class="hero-tag">🧠 Cross-Audit Historical Memory</span>
        <span class="hero-tag">⚠️ Pre-Audit Gap Hunter</span>
        <span class="hero-tag">🔄 Instant Lead Feedback Loop</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper for memory tag badges
def format_mem_badge(text):
    if text.startswith("[F-"): return "<span class='mem-badge badge-finding'>AUDIT FINDING</span>"
    if text.startswith("[REM-"): return "<span class='mem-badge badge-ticket'>REMEDIATION</span>"
    if text.startswith("[POL-"): return "<span class='mem-badge badge-policy'>POLICY</span>"
    if text.startswith("[CT-"): return "<span class='mem-badge badge-test'>CONTROL TEST</span>"
    if text.startswith("[FB-"): return "<span class='mem-badge badge-feedback'>COMPLIANCE FEEDBACK</span>"
    if text.startswith("[SLACK-"): return "<span class='mem-badge badge-slack'>SLACK / AUDITOR</span>"
    return "<span class='mem-badge' style='background:#e2e8f0; color:#334155;'>RECORD</span>"

# Execution helpers
def run_both(q):
    with ThreadPoolExecutor(max_workers=2) as ex:
        off = ex.submit(agent.answer, q, False, mem)
        on = ex.submit(agent.answer, q, True, mem)
        return {"q": q, "off": off.result(), "on": on.result()}

def score_badge(text):
    s = score_text(text)
    n = sum(s.values())
    return n, len(TRAPS), s

# --- TABS FOR DEMO PRESENTATION ---
tab1, tab2, tab3 = st.tabs(["🚀 Side-by-Side Agent Comparison", "📈 Verification & Learning Curve", "🔍 Raw Memory Explorer"])

# TAB 1: LIVE DEMO
with tab1:
    st.markdown("#### 1. Select or Enter an Audit Readiness Query")
    st.caption("Notice how generic LLMs output high-level checklists, while AuditMemory citations uncover actual operational discrepancies before the auditors arrive.")
    
    cols = st.columns(len(PRESETS))
    for i, (c, p) in enumerate(zip(cols, PRESETS)):
        if c.button(f"💡 {p}", key=f"pre_{i}", use_container_width=True):
            ss.q = p
            
    q_col1, q_col2 = st.columns([4, 1])
    with q_col1:
        q = st.text_input("Audit Query", value=ss.q, label_visibility="collapsed")
    with q_col2:
        run_btn = st.button("⚡ Run Comparison", type="primary", use_container_width=True)

    if run_btn:
        ss.q = q
        ss.after = None
        with st.spinner("🧠 Recalling historical audit records, policy versions & control tests..."):
            ss.res = run_both(q)

    r = ss.res
    if r:
        st.divider()
        st.markdown("#### 2. Agent Intelligence Comparison")
        
        # Display side-by-side cards
        col_off, col_on = st.columns(2)
        
        with col_off:
            st.markdown("""
            <div class="card-header-off">
                <span>❌ Memory OFF (Standard LLM / Checklist)</span>
            </div>
            <div class="card-caption">
                No access to company history, tickets, or evidence logs. Only gives textbook, generic advice.
            </div>
            """, unsafe_allow_html=True)
            
            for n in r["off"]["notes"]:
                st.info(n)
            
            with st.container():
                st.markdown(r["off"]["answer"])
            
            if r["off"]["model"]:
                st.caption(f"Engine: `{r['off']['model']}`")

        with col_on:
            st.markdown("""
            <div class="card-header-on">
                <span>✅ Memory ON (AuditMemory Agent)</span>
            </div>
            <div class="card-caption">
                Recalls past findings, unverified closed tickets, auditor preferences, and stale tests with citations.
            </div>
            """, unsafe_allow_html=True)
            
            for n in r["on"]["notes"]:
                st.warning(n)
                
            with st.container():
                st.markdown(r["on"]["answer"])
            
            if r["on"]["model"]:
                st.caption(f"Engine: `{r['on']['model']}` (Cited audit records)")

        # Scorecard section for Judges
        if show_score:
            st.markdown("#### 3. Judge Evaluation Scorecard")
            st.caption("Automatic verification of 5 hidden pre-audit operational risks (ground-truth planted issues):")
            
            a, total, traps_off = score_badge(r["off"]["answer"])
            b, _, traps_on = score_badge(r["on"]["answer"])
            
            sc1, sc2, sc3 = st.columns([1, 1, 2])
            with sc1:
                st.metric("Standard LLM Catch Rate", f"{a} / {total}", delta=f"0% caught", delta_color="off")
            with sc2:
                st.metric("AuditMemory Catch Rate", f"{b} / {total}", delta=f"+{b - a} specific risks flagged!", delta_color="normal")
            with sc3:
                st.markdown("<div style='font-size:0.85rem; font-weight:600; margin-bottom:4px;'>Trap Verification Matrix:</div>", unsafe_allow_html=True)
                for trap_name, caught in traps_on.items():
                    status_icon = "🟢 **CAUGHT:**" if caught else "⚪ *MISSED:*"
                    st.markdown(f"{status_icon} <span style='font-size:0.85rem;'>{trap_name}</span>", unsafe_allow_html=True)

        # Recalled memories inspect panel
        st.divider()
        st.markdown("#### 4. Recalled Audit Memory Context")
        st.caption("Multi-facet recall dynamically assembles relevant audit items across departments into the agent's prompt:")
        
        if not r["on"]["memories"]:
            st.info("No memories recalled for this query.")
        else:
            with st.expander(f"📁 View all {len(r['on']['memories'])} recalled evidence & audit items", expanded=False):
                for m in r["on"]["memories"]:
                    badge = format_mem_badge(m["text"])
                    st.markdown(f"<div class='mem-item'>{badge} {m['text']}</div>", unsafe_allow_html=True)

        # Interactive Feedback Loop
        st.divider()
        st.markdown("#### 5. Interactive Adaptation Loop (Continuous Compliance)")
        st.caption("When the compliance lead updates status or learns a new auditor preference, AuditMemory retains it immediately and overrides old assumptions.")
        
        ex1 = "Priya rejected the evidence for REM-14 again. The ticket needs to be re-opened and treated as critical."
        ex2 = "We completed a full backup restore test today (2026-11-07) with screenshots, so that risk is closed."
        
        col_ex1, col_ex2 = st.columns(2)
        if col_ex1.button("📋 Preset: Auditor Priya rejected REM-14 evidence", use_container_width=True):
            ss.fb = ex1
        if col_ex2.button("📋 Preset: Backup restore test was completed today", use_container_width=True):
            ss.fb = ex2
            
        fb = st.text_area("Compliance Lead Feedback / New Ground Truth", value=ss.get("fb", ""), height=75)
        
        btn_fb1, btn_fb2 = st.columns([1, 1])
        with btn_fb1:
            if st.button("💾 Retain Feedback into Memory", type="primary", use_container_width=True) and fb.strip():
                try:
                    agent.give_feedback(fb.strip(), mem)
                    st.toast("Retained feedback into memory bank!", icon="✅")
                    st.success("Retained. The agent's knowledge is now updated.")
                except Exception as e:
                    st.error(f"Could not retain feedback: {e}")
                    
        with btn_fb2:
            if st.button("🔄 Re-Ask Agent With Updated Memory", use_container_width=True):
                with st.spinner("Re-evaluating with feedback..."):
                    ss.after = agent.answer(r["q"], True, mem)
                    
        if ss.after:
            st.markdown("##### Adaptation Results:")
            af1, af2 = st.columns(2)
            with af1:
                st.markdown("**Initial Response (Before Feedback)**")
                st.info(r["on"]["answer"])
            with af2:
                st.markdown("**Updated Response (After Feedback Retained)**")
                st.success(ss.after["answer"])

# TAB 2: LEARNING CURVE
with tab2:
    st.markdown("### 📈 Quantitative Learning Curve")
    st.write("Demonstration of memory as a compounding asset: as more historical company records are loaded into memory, the agent catches systematically more audit traps.")
    
    # Path resolved relative to app.py file location
    p = pathlib.Path(__file__).resolve().parent / "data" / "learning_curve.json"
    if not p.exists():
        st.warning("`data/learning_curve.json` not found. Click the button below to generate it:")
        if st.button("⚡ Run Evaluation Benchmark Now", type="primary"):
            with st.spinner("Running evaluation benchmark across memory stages..."):
                from src import eval as eval_module
                eval_module.run()
                st.rerun()
    else:
        # Provide an instant re-run button directly in UI
        col_bench1, col_bench2 = st.columns([3, 1])
        with col_bench2:
            if st.button("🔄 Re-run Benchmark", use_container_width=True):
                with st.spinner("Recalculating learning curve..."):
                    from src import eval as eval_module
                    eval_module.run()
                    st.rerun()
                    
        d = json.loads(p.read_text())
        st.caption(f"Benchmark Configuration: Engine=`{d['meta']['backend']}` | LLM=`{d['meta']['llm']}`")
        
        import pandas as pd
        
        # Key metrics row
        m_col1, m_col2, m_col3 = st.columns(3)
        stages = d["stages"]
        with m_col1:
            st.metric("Base Performance (0% Memory)", f"{stages[0]['caught']}/{d['meta']['total_traps']} risks", "Textbook LLM")
        with m_col2:
            st.metric("Midway Performance (50% Memory)", f"{stages[2]['caught']}/{d['meta']['total_traps']} risks", f"+{stages[2]['caught']} risks")
        with m_col3:
            st.metric("Full Memory Bank (100% Memory)", f"{stages[-1]['caught']}/{d['meta']['total_traps']} risks", f"+{stages[-1]['caught']} risks caught", delta_color="normal")
            
        chart_data = pd.DataFrame([
            {"Memory Retained": f"{s['pct']}% ({s['records']} records)", "Audit Traps Caught": s["caught"]} 
            for s in stages
        ]).set_index("Memory Retained")
        
        st.bar_chart(chart_data)
        
        st.markdown("#### Detailed Progression Matrix Across Benchmark Stages")
        rows = [
            {
                "Memory Load": f"{s['pct']}%",
                "Records Stored": s["records"],
                "Total Caught": f"{s['caught']} / {d['meta']['total_traps']}",
                **{k: ("✅ CAUGHT" if v else "❌ MISSED") for k, v in s["traps"].items()}
            }
            for s in stages
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

# TAB 3: MEMORY BROWSER
with tab3:
    st.markdown("### 🔍 Raw Memory Explorer & Vector Reflection")
    st.write("Direct inspection of recalled audit units, control definitions, and auditor behavioral patterns.")
    
    search_q = st.text_input("Search Memory Bank", "vendor access review")
    if search_q:
        results = mem.recall(search_q, k=8)
        st.caption(f"Found {len(results)} matching records:")
        for m in results:
            badge = format_mem_badge(m["text"])
            st.markdown(f"<div class='mem-item'>{badge} {m['text']}</div>", unsafe_allow_html=True)
            
    if isinstance(mem, HindsightMemory):
        st.divider()
        st.markdown("#### 🧠 High-Level Hindsight Synthesis (`reflect`)")
        if st.button("Synthesize Trends Across History"):
            with st.spinner("Synthesizing memory bank..."):
                reflection = mem.reflect(search_q)
                st.markdown(f"**Synthesis:**\n\n{reflection}")
