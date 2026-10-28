"""
Interactive Code Execution Visualizer Component for CodeXplain Hub.
Renders a real code editor with animated SVG execution paths, traveling particles,
curved bezier routing around code, and synchronized debugging panels (Stack, Heap, Variables, Console).
"""

import json
import html
from typing import Dict, Any
from core.tracer.event_model import ExecutionTrace

def highlight_syntax(code: str, language: str) -> str:
    """Escapes and adds syntax highlighting spans to source code."""
    escaped = html.escape(code)
    lines = escaped.split("\n")
    formatted_lines = []

    for idx, line in enumerate(lines, 1):
        # Line numbers and content
        formatted_lines.append(f'<div class="code-line" id="line-{idx}" data-line="{idx}">'
                               f'<span class="gutter-num">{idx}</span>'
                               f'<span class="line-content">{line if line else "&nbsp;"}</span>'
                               f'</div>')
    return "\n".join(formatted_lines)

def render_execution_visualizer(trace: ExecutionTrace, height: int = 760) -> str:
    """Generates the full self-contained HTML/JS/CSS visualizer component."""
    trace_dict = trace.to_dict()
    trace_json = json.dumps(trace_dict)
    code_lines_html = highlight_syntax(trace.code, trace.language)

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  :root {{
    --bg-dark: #080514;
    --bg-panel: #0e0a24;
    --bg-surface: #151036;
    --border-color: #2b2056;
    --accent-purple: #a855f7;
    --accent-violet: #8b5cf6;
    --accent-emerald: #10b981;
    --accent-cyan: #06b6d4;
    --accent-amber: #f59e0b;
    --accent-rose: #f43f5e;
    --text-primary: #f8fafc;
    --text-secondary: #a1a1aa;
    --font-code: 'JetBrains Mono', Consolas, Monaco, monospace;
    --font-ui: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background-color: var(--bg-dark);
    color: var(--text-primary);
    font-family: var(--font-ui);
    overflow: hidden;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }}

  /* Top Toolbar */
  .visualizer-toolbar {{
    background: #0d0822;
    border-bottom: 1px solid var(--border-color);
    padding: 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    z-index: 50;
  }}

  .toolbar-group {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .btn-ctrl {{
    background: #191238;
    border: 1px solid #362963;
    color: var(--text-primary);
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }}

  .btn-ctrl:hover {{
    background: #7c3aed;
    border-color: #a855f7;
    color: #ffffff;
  }}

  .btn-ctrl.btn-primary {{
    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    border-color: #a855f7;
    color: #ffffff;
  }}

  .btn-ctrl.btn-primary:hover {{
    background: linear-gradient(135deg, #9333ea, #8b5cf6);
  }}

  .status-badge {{
    background: rgba(168, 85, 247, 0.15);
    border: 1px solid rgba(168, 85, 247, 0.4);
    color: #c084fc;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }}

  .step-counter {{
    font-family: var(--font-code);
    font-size: 0.85rem;
    color: var(--text-secondary);
    min-width: 90px;
  }}

  /* Main Two-Panel Layout */
  .visualizer-main {{
    display: flex;
    flex: 1;
    overflow: hidden;
    position: relative;
  }}

  /* Left: Real Code Editor Area Container */
  .editor-pane-outer {{
    flex: 1.5;
    position: relative;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border-right: 1px solid var(--border-color);
  }}

  .editor-container {{
    flex: 1;
    background: #080515;
    position: relative;
    overflow: auto;
  }}

  /* Sleek Custom Scrollbar */
  .editor-container::-webkit-scrollbar {{
    width: 9px;
    height: 9px;
  }}
  .editor-container::-webkit-scrollbar-track {{
    background: rgba(13, 8, 34, 0.6);
  }}
  .editor-container::-webkit-scrollbar-thumb {{
    background: #362866;
    border-radius: 6px;
    border: 1px solid rgba(168, 85, 247, 0.35);
  }}
  .editor-container::-webkit-scrollbar-thumb:hover {{
    background: #8b5cf6;
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.6);
  }}

  /* Floating Controls Docked Beside the Scroll Bar */
  .editor-dock-controls {{
    position: absolute;
    bottom: 18px;
    right: 22px; /* Positioned directly adjacent to the editor vertical scrollbar */
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(18, 13, 44, 0.94);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1.5px solid rgba(168, 85, 247, 0.5);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.75), 0 0 20px rgba(168, 85, 247, 0.35);
    border-radius: 9999px;
    padding: 6px 12px;
    z-index: 100;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }}

  .editor-dock-controls:hover {{
    border-color: rgba(168, 85, 247, 0.85);
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.85), 0 0 26px rgba(168, 85, 247, 0.55);
    transform: translateY(-2px);
  }}

  .dock-step-badge {{
    font-family: var(--font-code);
    font-size: 0.76rem;
    font-weight: 700;
    color: #c084fc;
    background: rgba(168, 85, 247, 0.18);
    border: 1px solid rgba(168, 85, 247, 0.4);
    padding: 4px 10px;
    border-radius: 9999px;
    white-space: nowrap;
  }}

  .dock-buttons {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .dock-btn {{
    background: #1b143f;
    border: 1px solid #3d2f75;
    color: #e2e8f0;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    transition: all 0.15s ease;
  }}

  .dock-btn:hover {{
    background: #2b205e;
    border-color: #a855f7;
    color: #ffffff;
    transform: scale(1.04);
  }}

  .dock-btn-primary {{
    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    border-color: #a855f7;
    color: #ffffff;
    box-shadow: 0 2px 10px rgba(139, 92, 246, 0.4);
  }}

  .dock-btn-primary:hover {{
    background: linear-gradient(135deg, #9333ea, #8b5cf6);
    box-shadow: 0 4px 14px rgba(168, 85, 247, 0.6);
  }}

  .dock-btn-accent {{
    background: linear-gradient(135deg, #10b981, #059669);
    border-color: #34d399;
    color: #ffffff;
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4);
  }}

  .dock-btn-accent:hover {{
    background: linear-gradient(135deg, #059669, #047857);
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.6);
  }}

  .editor-wrapper {{
    position: relative;
    min-height: 100%;
    min-width: 100%;
    padding: 16px 0 60px 0; /* Extra bottom padding so last lines are never blocked by dock */
  }}

  /* Code Line Rows */
  .code-line {{
    display: flex;
    align-items: center;
    font-family: var(--font-code);
    font-size: 0.88rem;
    line-height: 1.6;
    padding: 2px 0;
    position: relative;
    transition: background 0.2s ease;
  }}

  .gutter-num {{
    width: 50px;
    text-align: right;
    padding-right: 16px;
    color: #475569;
    user-select: none;
    font-size: 0.78rem;
    flex-shrink: 0;
  }}

  .line-content {{
    white-space: pre;
    color: #e2e8f0;
    padding-left: 8px;
    flex: 1;
    z-index: 5;
  }}

  /* Active Line Glow */
  .code-line.active-target {{
    background: rgba(56, 189, 248, 0.15);
    border-left: 4px solid var(--accent-cyan);
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.35);
  }}

  .code-line.active-source {{
    background: rgba(168, 85, 247, 0.12);
    border-left: 4px solid var(--accent-purple);
  }}

  /* Animated SVG Execution Path Canvas */
  .svg-canvas {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 20;
    overflow: visible;
  }}

  /* Dynamic Path Styling */
  .animated-path {{
    fill: none;
    stroke-width: 2.8;
    stroke-linecap: round;
    stroke-dasharray: 8 4;
    animation: flowDash 1.2s linear infinite;
    filter: drop-shadow(0 0 8px currentColor);
  }}

  @keyframes flowDash {{
    from {{ stroke-dashoffset: 24; }}
    to {{ stroke-dashoffset: 0; }}
  }}

  .path-particle {{
    r: 5;
    fill: #ffffff;
    filter: drop-shadow(0 0 8px #ffffff);
  }}

  /* Floating Event Label Badge on Canvas */
  .canvas-event-badge {{
    position: absolute;
    transform: translate(-50%, -50%);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 800;
    font-family: var(--font-code);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6);
    z-index: 30;
    pointer-events: none;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  /* Right: Synchronized Debugger Sidebars */
  .debugger-container {{
    flex: 1.1;
    background: var(--bg-panel);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    border-left: 1px solid var(--border-color);
  }}

  .panel-section {{
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
  }}

  .panel-title {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-secondary);
    font-weight: 700;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  /* Explanation Box */
  .explanation-card {{
    background: #100b2a;
    border: 1px solid #362963;
    border-left: 4px solid var(--accent-violet);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.88rem;
    line-height: 1.5;
    color: #f1f5f9;
  }}

  /* Call Stack */
  .stack-frame {{
    background: #100b2a;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 6px 12px;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: var(--font-code);
    font-size: 0.82rem;
  }}

  .stack-frame.frame-active {{
    border-color: var(--accent-cyan);
    background: rgba(6, 182, 212, 0.15);
    color: #22d3ee;
  }}

  /* Variables Table */
  .vars-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-code);
    font-size: 0.8rem;
  }}

  .vars-table th {{
    text-align: left;
    color: var(--text-secondary);
    padding: 4px 8px;
    border-bottom: 1px solid var(--border-color);
  }}

  .vars-table td {{
    padding: 5px 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  }}

  .var-name {{ color: #c084fc; font-weight: 600; }}
  .var-type {{ color: #818cf8; font-size: 0.74rem; }}
  .var-val {{ color: #34d399; }}

  /* Heap Object Cards */
  .heap-card {{
    background: #0f0a28;
    border: 1.5px solid var(--accent-purple);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 8px;
    box-shadow: 0 4px 14px rgba(168, 85, 247, 0.25);
  }}

  .heap-id {{
    font-family: var(--font-code);
    font-size: 0.8rem;
    font-weight: 700;
    color: #c084fc;
    margin-bottom: 4px;
  }}

  .heap-fields {{
    font-family: var(--font-code);
    font-size: 0.8rem;
    color: #cbd5e1;
    padding-left: 8px;
  }}

  /* Live Console */
  .console-box {{
    background: #060412;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 8px 12px;
    font-family: var(--font-code);
    font-size: 0.82rem;
    color: #34d399;
    min-height: 60px;
    max-height: 100px;
    overflow-y: auto;
    white-space: pre-wrap;
  }}
</style>
</head>
<body>

<!-- Visualizer Top Control Bar -->
<div class="visualizer-toolbar">
  <div class="toolbar-group">
    <button class="btn-ctrl btn-primary" id="btn-play">▶ Play</button>
    <button class="btn-ctrl" id="btn-pause" style="display:none;">⏸ Pause</button>
    <button class="btn-ctrl" id="btn-prev">⏮ Step Back</button>
    <button class="btn-ctrl" id="btn-next">⏭ Step</button>
    <button class="btn-ctrl" id="btn-reset">🔄 Reset</button>
  </div>

  <div class="toolbar-group">
    <span class="step-counter" id="step-display">Step 1 / {len(trace.events)}</span>
    <select class="btn-ctrl" id="speed-select" style="padding: 4px 8px;">
      <option value="2200">0.5x Speed</option>
      <option value="1200" selected>1.0x Normal</option>
      <option value="600">2.0x Fast</option>
      <option value="300">4.0x Turbo</option>
    </select>
    <span class="status-badge" id="mode-badge">{trace.trace_type}</span>
  </div>
</div>

<!-- Main Two-Column View -->
<div class="visualizer-main">
  <!-- Left: Real Code Editor with Floating Scrollbar Dock -->
  <div class="editor-pane-outer">
    <div class="editor-container" id="editor-scroller">
      <div class="editor-wrapper" id="editor-wrapper">
        <!-- SVG Path Canvas -->
        <svg class="svg-canvas" id="canvas-svg">
          <defs>
            <marker id="arrow-cyan" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
              <path d="M 0 0 L 8 4 L 0 8 Z" fill="#06b6d4" />
            </marker>
            <marker id="arrow-purple" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
              <path d="M 0 0 L 8 4 L 0 8 Z" fill="#a855f7" />
            </marker>
            <marker id="arrow-emerald" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
              <path d="M 0 0 L 8 4 L 0 8 Z" fill="#10b981" />
            </marker>
            <marker id="arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
              <path d="M 0 0 L 8 4 L 0 8 Z" fill="#8b5cf6" />
            </marker>
            <marker id="arrow-amber" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
              <path d="M 0 0 L 8 4 L 0 8 Z" fill="#f59e0b" />
            </marker>
          </defs>

          <!-- Dynamic Curved Path -->
          <path id="exec-path" class="animated-path" d="" stroke="#06b6d4" style="display:none;" />
          <!-- Traveling Particle Circle -->
          <circle id="exec-particle" class="path-particle" cx="0" cy="0" style="display:none;" />
        </svg>

        <!-- Floating Event Label Badge -->
        <div id="event-badge" class="canvas-event-badge" style="display:none;">EXECUTE</div>

        <!-- Code Lines -->
        <div id="code-lines-block">
          {code_lines_html}
        </div>
      </div>
    </div>

    <!-- Floating Controller Dock Beside Scroll Bar (Always visible in big programs) -->
    <div class="editor-dock-controls" id="editor-dock-controls">
      <span class="dock-step-badge" id="dock-step-display">Step 1 / {len(trace.events)}</span>
      <div class="dock-buttons">
        <button class="dock-btn" id="dock-btn-prev" title="Step Back (Left Arrow / P)">⏮ Back</button>
        <button class="dock-btn dock-btn-primary" id="dock-btn-play" title="Play (Space)">▶ Play</button>
        <button class="dock-btn dock-btn-primary" id="dock-btn-pause" style="display:none;" title="Pause (Space)">⏸ Pause</button>
        <button class="dock-btn dock-btn-accent" id="dock-btn-next" title="Next Step (Right Arrow / N)">⏭ Step</button>
        <button class="dock-btn" id="dock-btn-reset" title="Reset (R / Esc)">🔄 Reset</button>
      </div>
    </div>
  </div>

  <!-- Right: Synchronized Debugger Sidebars -->
  <div class="debugger-container">
    <!-- Active Statement Explanation -->
    <div class="panel-section">
      <div class="panel-title">💡 Current Line Explanation</div>
      <div class="explanation-card" id="exp-text">
        Ready to visualize code execution. Click 'Play' or 'Step' to begin.
      </div>
    </div>

    <!-- Call Stack -->
    <div class="panel-section">
      <div class="panel-title">📚 Call Stack Frames</div>
      <div id="stack-container">
        <div class="stack-frame frame-active">main:12</div>
      </div>
    </div>

    <!-- Variables Scope -->
    <div class="panel-section">
      <div class="panel-title">🔍 Local Variables Inspector</div>
      <table class="vars-table">
        <thead>
          <tr><th>Name</th><th>Type</th><th>Value</th></tr>
        </thead>
        <tbody id="vars-body">
          <tr><td colspan="3" style="color:#64748b;">No variables in scope</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Heap Objects -->
    <div class="panel-section">
      <div class="panel-title">📦 Heap Object Allocations</div>
      <div id="heap-container">
        <div style="font-size:0.8rem; color:#64748b;">Heap empty</div>
      </div>
    </div>

    <!-- Live Terminal Console -->
    <div class="panel-section" style="flex:1;">
      <div class="panel-title">💻 Live Console Output</div>
      <div class="console-box" id="console-stream">> Ready</div>
    </div>
  </div>
</div>

<script>
  // Trace Data Injected from Python
  const traceData = {trace_json};
  const events = traceData.events || [];
  let currentStep = 0;
  let isPlaying = false;
  let playTimer = null;
  let stepInterval = 1200;

  // DOM Elements
  const btnPlay = document.getElementById('btn-play');
  const btnPause = document.getElementById('btn-pause');
  const btnNext = document.getElementById('btn-next');
  const btnPrev = document.getElementById('btn-prev');
  const btnReset = document.getElementById('btn-reset');
  const speedSelect = document.getElementById('speed-select');
  const stepDisplay = document.getElementById('step-display');

  // Floating Dock Elements Beside Scroll Bar
  const dockBtnPlay = document.getElementById('dock-btn-play');
  const dockBtnPause = document.getElementById('dock-btn-pause');
  const dockBtnNext = document.getElementById('dock-btn-next');
  const dockBtnPrev = document.getElementById('dock-btn-prev');
  const dockBtnReset = document.getElementById('dock-btn-reset');
  const dockStepDisplay = document.getElementById('dock-step-display');

  const expText = document.getElementById('exp-text');
  const stackContainer = document.getElementById('stack-container');
  const varsBody = document.getElementById('vars-body');
  const heapContainer = document.getElementById('heap-container');
  const consoleStream = document.getElementById('console-stream');
  
  const execPath = document.getElementById('exec-path');
  const execParticle = document.getElementById('exec-particle');
  const eventBadge = document.getElementById('event-badge');
  const editorScroller = document.getElementById('editor-scroller');
  const editorWrapper = document.getElementById('editor-wrapper');
  const canvasSvg = document.getElementById('canvas-svg');

  // Animation frame request for particle
  let particleAnim = null;

  function renderStep(idx) {{
    if (events.length === 0) return;
    idx = Math.max(0, Math.min(idx, events.length - 1));
    currentStep = idx;

    const ev = events[idx];
    stepDisplay.innerText = `Step ${{idx + 1}} / ${{events.length}}`;
    if (dockStepDisplay) dockStepDisplay.innerText = `Step ${{idx + 1}} / ${{events.length}}`;

    // 1. Highlight lines in editor
    document.querySelectorAll('.code-line').forEach(el => {{
      el.classList.remove('active-target', 'active-source');
    }});

    const targetLineEl = document.getElementById(`line-${{ev.target_line}}`);
    const sourceLineEl = document.getElementById(`line-${{ev.source_line}}`);

    if (sourceLineEl && ev.source_line !== ev.target_line) {{
      sourceLineEl.classList.add('active-source');
    }}
    if (targetLineEl) {{
      targetLineEl.classList.add('active-target');
      // Smoothly scroll active line into view
      targetLineEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}

    // 2. Draw SVG Curved Path connecting source to target
    try {{
      drawExecutionPath(ev, sourceLineEl, targetLineEl);
    }} catch (e) {{
      console.warn("Path render issue:", e);
    }}

    // 3. Update Explanation
    expText.innerText = ev.description || 'Executing statement.';

    // 4. Update Call Stack
    renderCallStack(ev.call_stack);

    // 5. Update Variables Table
    renderVariables(ev.variables);

    // 6. Update Heap Objects
    renderHeap(ev.heap);

    // 7. Update Console Output
    consoleStream.innerText = ev.console_output ? `> ${{ev.console_output}}` : '> (No output yet)';
  }}

  function drawExecutionPath(ev, sourceEl, targetEl) {{
    if (!sourceEl || !targetEl || ev.source_line === ev.target_line) {{
      execPath.style.display = 'none';
      execParticle.style.display = 'none';
      eventBadge.style.display = 'none';
      return;
    }}

    const wrapperRect = editorWrapper.getBoundingClientRect();
    const r1 = sourceEl.getBoundingClientRect();
    const r2 = targetEl.getBoundingClientRect();

    // Calculate (x, y) relative to wrapper
    const x1 = Math.max(30, (r1.left - wrapperRect.left) + 60);
    const y1 = (r1.top - wrapperRect.top) + (r1.height / 2);

    const x2 = Math.max(30, (r2.left - wrapperRect.left) + 60);
    const y2 = (r2.top - wrapperRect.top) + (r2.height / 2);

    // Distance and outward curve control point - clamp to wrapper width
    const dy = Math.abs(y2 - y1);
    const maxAllowedWidth = Math.max(250, (wrapperRect.width || 450) - 40);
    const outwardOffset = Math.max(80, Math.min(220, dy * 0.75));
    const cx = Math.min(maxAllowedWidth, Math.max(x1, x2) + outwardOffset);

    // Cubic Bezier curve routing around the code: M x1 y1 C cx y1, cx y2, x2 y2
    const d = `M ${{x1}} ${{y1}} C ${{cx}} ${{y1}}, ${{cx}} ${{y2}}, ${{x2}} ${{y2}}`;
    
    const color = ev.color || '#38bdf8';
    let markerId = 'arrow-blue';
    if (color === '#00f2fe') markerId = 'arrow-cyan';
    else if (color === '#a855f7') markerId = 'arrow-purple';
    else if (color === '#10b981') markerId = 'arrow-emerald';
    else if (color === '#f59e0b') markerId = 'arrow-amber';

    execPath.setAttribute('d', d);
    execPath.setAttribute('stroke', color);
    execPath.setAttribute('marker-end', `url(#${{markerId}})`);
    execPath.style.display = 'block';

    // Position Event Badge at apex of curve
    const badgeX = Math.min(maxAllowedWidth - 50, cx * 0.82 + (x1 + x2) * 0.09);
    const badgeY = (y1 + y2) / 2;
    eventBadge.innerText = ev.label || 'EXECUTE';
    eventBadge.style.backgroundColor = `${{color}}25`;
    eventBadge.style.border = `1.5px solid ${{color}}`;
    eventBadge.style.color = '#ffffff';
    eventBadge.style.left = `${{badgeX}}px`;
    eventBadge.style.top = `${{badgeY}}px`;
    eventBadge.style.display = 'block';

    // Animate glowing particle along path
    try {{
      animateParticleAlongPath(d, color);
    }} catch (err) {{
      console.warn("Particle anim error:", err);
    }}
  }}

  function animateParticleAlongPath(d, color) {{
    if (particleAnim) cancelAnimationFrame(particleAnim);
    execParticle.setAttribute('fill', color);
    execParticle.style.display = 'block';

    let pathLength = 0;
    try {{
      pathLength = execPath.getTotalLength();
    }} catch (e) {{
      pathLength = 0;
    }}
    if (!pathLength || isNaN(pathLength) || pathLength <= 0) return;

    let startTime = null;
    const duration = Math.min(900, stepInterval * 0.85);

    function stepParticle(timestamp) {{
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const point = execPath.getPointAtLength(progress * pathLength);
      
      execParticle.setAttribute('cx', point.x);
      execParticle.setAttribute('cy', point.y);

      if (progress < 1) {{
        particleAnim = requestAnimationFrame(stepParticle);
      }}
    }}
    particleAnim = requestAnimationFrame(stepParticle);
  }}

  function renderCallStack(frames) {{
    stackContainer.innerHTML = '';
    if (!frames || frames.length === 0) {{
      stackContainer.innerHTML = '<div class="stack-frame">Global Frame</div>';
      return;
    }}
    // Render top frame active
    for (let i = frames.length - 1; i >= 0; i--) {{
      const f = frames[i];
      const isActive = (i === frames.length - 1);
      const div = document.createElement('div');
      div.className = `stack-frame ${{isActive ? 'frame-active' : ''}}`;
      div.innerHTML = `<span>${{f.name}}</span><span style="opacity:0.7;">line ${{f.line}}</span>`;
      stackContainer.appendChild(div);
    }}
  }}

  function renderVariables(vars) {{
    varsBody.innerHTML = '';
    const locals = (vars && vars.locals) || [];
    if (locals.length === 0) {{
      varsBody.innerHTML = '<tr><td colspan="3" style="color:#64748b;">No variables in scope</td></tr>';
      return;
    }}
    locals.forEach(v => {{
      const tr = document.createElement('tr');
      tr.innerHTML = `<td class="var-name">${{v.name}}</td><td class="var-type">${{v.type}}</td><td class="var-val">${{v.value}}</td>`;
      varsBody.appendChild(tr);
    }});
  }}

  function renderHeap(heap) {{
    heapContainer.innerHTML = '';
    const keys = Object.keys(heap || {{}});
    if (keys.length === 0) {{
      heapContainer.innerHTML = '<div style="font-size:0.8rem; color:#64748b;">Heap empty</div>';
      return;
    }}
    keys.forEach(k => {{
      const obj = heap[k];
      const div = document.createElement('div');
      div.className = 'heap-card';
      let fieldsHtml = '';
      if (obj.fields) {{
        for (const [fname, fval] of Object.entries(obj.fields)) {{
          fieldsHtml += `<div>• ${{fname}}: <span style="color:#6ee7b7;">${{fval}}</span></div>`;
        }}
      }}
      div.innerHTML = `<div class="heap-id">${{k}} (${{obj.type}})</div><div class="heap-fields">${{fieldsHtml || 'No fields'}}</div>`;
      heapContainer.appendChild(div);
    }});
  }}

  // Playback Controls
  function play() {{
    if (isPlaying) return;
    isPlaying = true;
    btnPlay.style.display = 'none';
    btnPause.style.display = 'inline-flex';
    if (dockBtnPlay) dockBtnPlay.style.display = 'none';
    if (dockBtnPause) dockBtnPause.style.display = 'inline-flex';

    if (currentStep >= events.length - 1) {{
      currentStep = 0;
    }}

    playTimer = setInterval(() => {{
      if (currentStep < events.length - 1) {{
        renderStep(currentStep + 1);
      }} else {{
        pause();
      }}
    }}, stepInterval);
  }}

  function pause() {{
    isPlaying = false;
    if (playTimer) clearInterval(playTimer);
    btnPlay.style.display = 'inline-flex';
    btnPause.style.display = 'none';
    if (dockBtnPlay) dockBtnPlay.style.display = 'inline-flex';
    if (dockBtnPause) dockBtnPause.style.display = 'none';
  }}

  function next() {{
    pause();
    if (currentStep < events.length - 1) {{
      renderStep(currentStep + 1);
    }}
  }}

  function prev() {{
    pause();
    if (currentStep > 0) {{
      renderStep(currentStep - 1);
    }}
  }}

  function reset() {{
    pause();
    renderStep(0);
  }}

  btnPlay.addEventListener('click', play);
  btnPause.addEventListener('click', pause);
  btnNext.addEventListener('click', next);
  btnPrev.addEventListener('click', prev);
  btnReset.addEventListener('click', reset);

  if (dockBtnPlay) dockBtnPlay.addEventListener('click', play);
  if (dockBtnPause) dockBtnPause.addEventListener('click', pause);
  if (dockBtnNext) dockBtnNext.addEventListener('click', next);
  if (dockBtnPrev) dockBtnPrev.addEventListener('click', prev);
  if (dockBtnReset) dockBtnReset.addEventListener('click', reset);

  // Global window methods for programmatic control & testing
  window.renderStep = renderStep;
  window.play = play;
  window.pause = pause;
  window.next = next;
  window.prev = prev;
  window.reset = reset;
  window.getCurrentStep = () => currentStep;
  window.getEvents = () => events;

  // Keyboard navigation
  window.addEventListener('keydown', (e) => {{
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowRight' || e.key === 'n') {{
      next();
    }} else if (e.key === 'ArrowLeft' || e.key === 'p') {{
      prev();
    }} else if (e.key === ' ' || e.key === 'Spacebar') {{
      e.preventDefault();
      isPlaying ? pause() : play();
    }} else if (e.key === 'r' || e.key === 'Escape') {{
      reset();
    }}
  }});

  speedSelect.addEventListener('change', (e) => {{
    stepInterval = parseInt(e.target.value);
    if (isPlaying) {{
      pause();
      play();
    }}
  }});

  // Re-align paths on scroll and resize
  editorScroller.addEventListener('scroll', () => {{
    if (events[currentStep]) {{
      const ev = events[currentStep];
      drawExecutionPath(
        ev,
        document.getElementById(`line-${{ev.source_line}}`),
        document.getElementById(`line-${{ev.target_line}}`)
      );
    }}
  }});

  window.addEventListener('resize', () => {{
    if (events[currentStep]) {{
      const ev = events[currentStep];
      drawExecutionPath(
        ev,
        document.getElementById(`line-${{ev.source_line}}`),
        document.getElementById(`line-${{ev.target_line}}`)
      );
    }}
  }});

  // Initial render step 0
  setTimeout(() => {{
    renderStep(0);
  }}, 150);
</script>
</body>
</html>
"""
    return html_content
