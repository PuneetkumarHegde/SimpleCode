"""
CodeXplain Hub — Interactive Animated Code Execution Visualizer & IDE.
Transforms code into an animated execution journey directly inside the code editor.
Features:
- Animated SVG execution paths with traveling particles & directional arrows inside the code editor.
- Distant jumps, constructor calls, method invocations, returns, loops, and conditions.
- Synchronized live debugging panels: Variables Inspector, Call Stack, Heap Allocations, Live Console.
- Full interactive controls: Play, Pause, Step, Step Back, Reset, Speed selector.
- Preserves all existing features: AI Explanation, Auto-Debugger, Complexity, Translations, Markdown Export.
- Universal zero-fail deployment guarantee (runs seamlessly with or without API keys).
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from core.detector import detect_language, LANGUAGE_NAMES
from core.ai_service import (
    CodeXplainService,
    compile_markdown_documentation,
    auto_detect_provider_and_model
)
from core.keyword_analyzer import analyze_scope_keywords
from core.sample_codes import SAMPLE_SNIPPETS
from core.tracer.universal_tracer import generate_execution_trace
from core.visualizer.code_visualizer import render_execution_visualizer

# Configure Streamlit Page
st.set_page_config(
    page_title="CodeXplain Hub — Animated Execution Visualizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Obsidian Cobalt Theme
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Default to the Java Student Constructor snippet requested by the user
DEFAULT_CODE = SAMPLE_SNIPPETS["Java: Student Constructor & Execution Path"]["code"]

# Session State Initialization
if "api_key" not in st.session_state:
    st.session_state["api_key"] = (
        os.getenv("AI_API_KEY") or 
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("OPENAI_API_KEY") or 
        os.getenv("ANTHROPIC_API_KEY") or 
        os.getenv("GROQ_API_KEY") or ""
    )
if "code_text" not in st.session_state:
    st.session_state["code_text"] = DEFAULT_CODE
if "active_trace" not in st.session_state:
    st.session_state["active_trace"] = None
if "analysis" not in st.session_state:
    st.session_state["analysis"] = None
if "translations" not in st.session_state:
    st.session_state["translations"] = {}

# Compute auto-detected engine
_, active_provider_name, active_model_name = auto_detect_provider_and_model(st.session_state["api_key"])

# ----------------- OPTIONAL API KEY DIALOG -----------------
@st.dialog("🔑 Optional API Key (Live Model Integration)")
def key_dialog():
    st.markdown("CodeXplain Hub works **with or without** an API key. You can paste any key below (Gemini, OpenAI, Claude, Groq):")

    input_key = st.text_input(
        "API Key",
        value=st.session_state["api_key"],
        type="password",
        placeholder="AIzaSy... / sk-... / gsk_..."
    )

    if input_key.strip():
        _, p_name, m_name = auto_detect_provider_and_model(input_key.strip())
        st.markdown(f"✨ **Auto-Detected:** `{p_name}` (`{m_name}`)")

    st.markdown("""
    <div style="font-size: 0.82rem; color: #94a3b8; margin: 8px 0;">
        • <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #60a5fa;">Get Free Gemini Key</a><br>
        • <a href="https://console.groq.com/keys" target="_blank" style="color: #60a5fa;">Get Free Groq Key</a>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save Key", use_container_width=True):
            st.session_state["api_key"] = input_key.strip()
            st.rerun()
    with col2:
        if st.button("Clear Key", use_container_width=True):
            st.session_state["api_key"] = ""
            st.rerun()

# ----------------- MODERN HEADER -----------------
head_left, head_right = st.columns([3, 1])
with head_left:
    st.markdown("""
    <div class="obsidian-header">
        <div>
            <h1 class="obsidian-title">⚡ CodeXplain Hub <span style="font-size:0.9rem; font-weight:600; color:#c084fc; background:rgba(168,85,247,0.18); padding:2px 10px; border-radius:9999px; border:1px solid rgba(168,85,247,0.4); margin-left:10px;">ANIMATED DEBUGGER IDE</span></h1>
            <div class="obsidian-subtitle">Interactive code execution visualizer with in-editor animated SVG paths, live call stack, heap tracking & console.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with head_right:
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    key_badge_text = f"🔑 Key: {active_provider_name}" if st.session_state["api_key"] else "🔑 Optional API Key"
    if st.button(key_badge_text, use_container_width=True):
        key_dialog()

# ----------------- CODE UPLOAD & AUTO-DETECTION -----------------
# Auto-detect language immediately from text
detected_key, detected_name = detect_language(st.session_state["code_text"])

# File Uploader
uploaded_file = st.file_uploader(
    "Upload a source code file (.java, .py, .cpp, .js, .go, .rs, .cs...)",
    type=["java", "py", "js", "ts", "cpp", "c", "cs", "go", "rs", "php", "rb", "kt", "swift", "sql", "sh", "txt"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    try:
        content_str = uploaded_file.read().decode("utf-8", errors="replace")
        if content_str != st.session_state["code_text"]:
            st.session_state["code_text"] = content_str
            detected_key, detected_name = detect_language(content_str, filename=uploaded_file.name)
            st.session_state["active_trace"] = None
            st.rerun()
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Live Language & Engine Indicators
c_info1, c_info2 = st.columns([1, 1])
with c_info1:
    st.markdown(f'<div style="margin-bottom: 6px;"><span class="badge-auto-lang">Detected Language: <b>{detected_name}</b></span></div>', unsafe_allow_html=True)
with c_info2:
    if st.session_state["api_key"]:
        st.markdown(f'<div style="text-align: right; margin-bottom: 6px;"><span class="badge-fallback-active">✨ Engine: {active_provider_name}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: right; margin-bottom: 6px;"><span class="badge-fallback-active">🛡️ Unfailing Zero-Quota Engine Active</span></div>', unsafe_allow_html=True)

# Code Input Area (automatically detects language on paste)
pasted_code = st.text_area(
    "Source Code",
    value=st.session_state["code_text"],
    height=210,
    placeholder="// Paste your code here (Java, Python, C++, JavaScript, Go, Rust, etc.)...\n// The language is automatically detected on the fly.",
    label_visibility="collapsed"
)

if pasted_code != st.session_state["code_text"]:
    st.session_state["code_text"] = pasted_code
    st.session_state["active_trace"] = None
    st.rerun()

# Action Buttons
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.5, 1.2, 0.8, 1.5])

with btn_col1:
    visualize_clicked = st.button("⚡ Debug & Animate Execution", use_container_width=True)

with btn_col2:
    explain_clicked = st.button("🚀 Explain Code", use_container_width=True)

with btn_col3:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state["code_text"] = ""
        st.session_state["active_trace"] = None
        st.session_state["analysis"] = None
        st.session_state["translations"] = {}
        st.rerun()

with btn_col4:
    sample_options = list(SAMPLE_SNIPPETS.keys())
    selected_sample = st.selectbox("📂 Load Preset Sample", options=sample_options, index=0, label_visibility="collapsed")
    if st.button("Load Selected Sample", use_container_width=True):
        st.session_state["code_text"] = SAMPLE_SNIPPETS[selected_sample]["code"]
        st.session_state["active_trace"] = None
        st.session_state["analysis"] = None
        st.session_state["translations"] = {}
        st.rerun()

# ----------------- EXECUTE VISUALIZATION TRIGGER -----------------
if visualize_clicked:
    if not st.session_state["code_text"].strip():
        st.warning("Please paste or upload some code first.")
    else:
        with st.spinner("Generating execution trace and computing in-editor paths..."):
            trace = generate_execution_trace(st.session_state["code_text"], detected_key)
            st.session_state["active_trace"] = trace
            st.success(f"Execution trace loaded ({trace.total_steps} execution steps captured)!")

# If active trace is None but we have code, auto-generate trace so visualizer is ready immediately
if st.session_state["active_trace"] is None and st.session_state["code_text"].strip():
    st.session_state["active_trace"] = generate_execution_trace(st.session_state["code_text"], detected_key)

# ----------------- 1. THE MAIN INTERACTIVE ANIMATED VISUALIZER -----------------
current_trace = st.session_state["active_trace"]

if current_trace and current_trace.events:
    st.markdown("<hr style='border:0; border-top:1px solid #1f2937; margin: 1.2rem 0 1rem 0;'>", unsafe_allow_html=True)
    
    # Visualizer Header Ribbon
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:1.1rem; font-weight:700; color:#f8fafc;">🎬 In-Editor Execution Visualizer</span>
            <span style="font-size:0.75rem; color:#38bdf8; background:rgba(56,189,248,0.15); padding:2px 8px; border-radius:4px; border:1px solid rgba(56,189,248,0.3);">
                {current_trace.trace_type}
            </span>
        </div>
        <div style="font-size:0.82rem; color:#94a3b8;">
            Paths animate directly inside code editor • Press <b>▶ Play</b> or <b>⏭ Step</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render HTML/JS Visualizer
    visualizer_html = render_execution_visualizer(current_trace, height=740)
    st.components.v1.html(visualizer_html, height=740, scrolling=False)

# ----------------- EXECUTE AI EXPLANATION TRIGGER -----------------
if explain_clicked:
    if not st.session_state["code_text"].strip():
        st.warning("Please paste or upload some code first.")
    else:
        with st.spinner("Analyzing code structure, scopes & complexity..."):
            service = CodeXplainService(api_key=st.session_state["api_key"])
            res = service.analyze_code(
                code=st.session_state["code_text"],
                language=detected_key
            )
            st.session_state["analysis"] = res
            st.session_state["translations"] = {}
            badge_msg = res.get("engine_badge", "Explanation complete!")
            st.success(badge_msg)
            if res.get("fallback_note"):
                st.caption(f"ℹ️ {res['fallback_note']}")

# ----------------- DISPLAY PRESERVED EXPLANATION RESULTS -----------------
analysis = st.session_state["analysis"]

if analysis:
    st.markdown("<hr style='border:0; border-top:1px solid #1f2937; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # 1. Functional Overview
    fo = analysis.get("functional_overview", {})
    st.markdown(f"""
    <div class="obsidian-card">
        <div class="obsidian-card-title">📝 Functional Overview</div>
        <p style="font-size: 1rem; line-height: 1.6; color: #f1f5f9; margin: 0;">
            {fo.get("summary", "Summary not generated.")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Scope & Pointer Simulation (with Arrow Marks)
    kw_sim = analysis.get("keyword_simulation") or analyze_scope_keywords(
        st.session_state["code_text"],
        detected_key
    )

    if kw_sim and (kw_sim.get("has_keywords") or kw_sim.get("mappings")):
        st.markdown("""
        <div class="obsidian-card">
            <div class="obsidian-card-title">🧭 Scope & Reference Simulation (Arrow Mapping)</div>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.8rem;">
                Visualizing how keywords and references bind in memory and resolve context:
            </p>
        """, unsafe_allow_html=True)

        mappings = kw_sim.get("mappings") or kw_sim.get("explanations") or []
        for m in mappings:
            k = m.get("keyword", "ref")
            target = m.get("arrow_target", "Instance/Memory")
            desc = m.get("explanation") or m.get("description", "")
            
            st.markdown(f"""
            <div class="scope-arrow-row">
                <span class="scope-keyword">{k}</span>
                <span class="scope-arrow">──►</span>
                <span class="scope-target">{target}</span>
                <span class="scope-detail">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

        diagram = kw_sim.get("mermaid_diagram") or kw_sim.get("mermaid_scope")
        if diagram:
            st.markdown(f"```mermaid\n{diagram}\n```")
        elif kw_sim.get("arrow_diagram"):
            st.code(kw_sim["arrow_diagram"], language="text")

        st.markdown("</div>", unsafe_allow_html=True)

    # Tabs for Detailed Breakdown, Debugger, Complexity, Translator & Downloader
    tab_trace, tab_debug, tab_complexity, tab_trans, tab_export = st.tabs([
        "🔍 Step-by-Step Breakdown",
        "🛠️ Issues & Fixes",
        "📊 Complexity Analysis",
        "🌐 Language Translation",
        "📥 Download Markdown"
    ])

    # Tab 1: Breakdown
    with tab_trace:
        breakdown_items = analysis.get("line_breakdown", [])
        if breakdown_items:
            for idx, item in enumerate(breakdown_items, 1):
                st.markdown(f"**Step {idx}: {item.get('line_range', '')}**")
                st.code(item.get("code", ""), language=detected_key)
                st.markdown(f"> {item.get('explanation', '')}")
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No step breakdown available.")

    # Tab 2: Debugger
    with tab_debug:
        dbg = analysis.get("debugger", {})
        status = dbg.get("status", "Inspected")
        st.markdown(f"**Diagnostic Status:** `{status}`")
        if dbg.get("summary"):
            st.markdown(dbg.get("summary"))

        issues = dbg.get("issues", [])
        for iss in issues:
            sev = iss.get("severity", "Warning").lower()
            st.markdown(f"""
            <div class="obsidian-issue {'warning' if sev == 'warning' else ''}">
                <div style="font-weight: 700; color: #f8fafc;">[{iss.get('severity', 'Note')}] {iss.get('title', 'Issue')}</div>
                <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 4px;"><b>Cause:</b> {iss.get('description', '')}</div>
                <div style="font-size: 0.9rem; color: #60a5fa; margin-top: 2px;"><b>Fix:</b> {iss.get('fix', '')}</div>
            </div>
            """, unsafe_allow_html=True)

        if dbg.get("corrected_code"):
            st.markdown("#### Corrected Code")
            st.code(dbg.get("corrected_code"), language=detected_key)

    # Tab 3: Complexity
    with tab_complexity:
        cx = analysis.get("complexity", {})
        score = cx.get("score", 3)
        badge = cx.get("badge", "Normal")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="obsidian-metric">
                <div class="obsidian-metric-val">{score} / 10</div>
                <div class="obsidian-metric-label">Complexity Score ({badge})</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="obsidian-metric">
                <div class="obsidian-metric-val" style="color: #60a5fa;">{cx.get('time_complexity', 'O(1)')}</div>
                <div class="obsidian-metric-label">Time Complexity</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="obsidian-metric">
                <div class="obsidian-metric-val" style="color: #a78bfa;">{cx.get('space_complexity', 'O(1)')}</div>
                <div class="obsidian-metric-label">Space Complexity</div>
            </div>
            """, unsafe_allow_html=True)

        if cx.get("bottlenecks"):
            st.markdown(f"**Hotspots:** {cx.get('bottlenecks')}")
        if cx.get("architecture_critique"):
            st.markdown(f"**Architecture Critique:** {cx.get('architecture_critique')}")

    # Tab 4: Translation
    with tab_trans:
        target_options = ["python", "javascript", "cpp", "java", "go", "rust"]
        filtered_targets = [t for t in target_options if t != detected_key]
        
        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            target_lang = st.selectbox(
                "Translate to:",
                options=filtered_targets,
                format_func=lambda x: LANGUAGE_NAMES.get(x, x.capitalize())
            )
        with col_t2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_trans = st.button("Translate", use_container_width=True)

        if run_trans:
            with st.spinner(f"Translating into {target_lang}..."):
                svc = CodeXplainService(api_key=st.session_state["api_key"])
                t_res = svc.translate_code(
                    code=st.session_state["code_text"],
                    source_lang=detected_key,
                    target_lang=target_lang
                )
                st.session_state["translations"][target_lang] = t_res.get("translated_code", "")
                st.success("Translated!")

        if target_lang in st.session_state["translations"]:
            st.code(st.session_state["translations"][target_lang], language=target_lang)

    # Tab 5: Download Markdown
    with tab_export:
        doc_md = compile_markdown_documentation(
            code=st.session_state["code_text"],
            language=detected_key,
            analysis=analysis,
            translated_codes=st.session_state["translations"]
        )
        st.download_button(
            label="📥 Download Analysis.md",
            data=doc_md,
            file_name=f"Code_Analysis_{detected_key.upper()}.md",
            mime="text/markdown",
            use_container_width=True
        )
        st.markdown("---")
        st.markdown(doc_md)
