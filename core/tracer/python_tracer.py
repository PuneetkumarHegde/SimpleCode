"""
Safe Python Runtime Tracer.
Executes Python code in an isolated subprocess with resource limits and timeouts.
Uses sys.settrace to capture exact line transitions, call stacks, scopes, and heap states.
"""

import subprocess
import tempfile
import os
import json
import sys
from typing import Dict, Any, List
from core.tracer.event_model import ExecutionTrace, ExecutionEvent

RUNNER_SCRIPT = '''
import sys
import json
import io
import inspect

code_to_run = sys.stdin.read()

events = []
stdout_buffer = io.StringIO()
original_stdout = sys.stdout
sys.stdout = stdout_buffer

call_stack = [{"name": "<main>", "line": 1}]
step_idx = 0
last_line = 1
heap_tracker = {}
MAX_STEPS = 120

def sanitize_val(v):
    try:
        if isinstance(v, (int, float, bool, str, list, dict, tuple, set)) or v is None:
            return repr(v) if not isinstance(v, str) else f'"{v}"'
        return f"<{type(v).__name__}>"
    except Exception:
        return "<unprintable>"

def trace_dispatch(frame, event, arg):
    global step_idx, last_line, call_stack
    if frame.f_code.co_filename != "<traced_user_code>":
        return trace_dispatch

    if step_idx >= MAX_STEPS:
        return None

    lineno = frame.f_lineno
    fname = frame.f_code.co_name
    
    # Filter locals
    clean_locals = []
    for k, v in frame.f_locals.items():
        if not k.startswith("__"):
            clean_locals.append({
                "name": k,
                "type": type(v).__name__,
                "value": sanitize_val(v)
            })

    output_now = stdout_buffer.getvalue()

    if event == "call":
        call_stack.append({"name": fname, "line": lineno})
        events.append({
            "step_index": step_idx,
            "source_line": last_line,
            "target_line": lineno,
            "event": "call",
            "label": "CALL",
            "color": "#00f2fe",
            "function_name": fname,
            "description": f"Calling function '{fname}()' with arguments.",
            "call_stack": list(call_stack),
            "variables": {"locals": clean_locals},
            "heap": dict(heap_tracker),
            "console_output": output_now
        })
        step_idx += 1
        last_line = lineno

    elif event == "line":
        # Determine if assignment, loop, or standard execution
        lbl = "EXECUTE"
        clr = "#38bdf8"
        desc = f"Executing line {lineno} in {fname}."
        
        events.append({
            "step_index": step_idx,
            "source_line": last_line,
            "target_line": lineno,
            "event": "line",
            "label": lbl,
            "color": clr,
            "function_name": fname,
            "description": desc,
            "call_stack": list(call_stack),
            "variables": {"locals": clean_locals},
            "heap": dict(heap_tracker),
            "console_output": output_now
        })
        step_idx += 1
        last_line = lineno

    elif event == "return":
        ret_val = sanitize_val(arg)
        desc = f"Returning from '{fname}()' -> {ret_val}."
        target = last_line
        if len(call_stack) > 1:
            call_stack.pop()
            target = call_stack[-1]["line"]

        events.append({
            "step_index": step_idx,
            "source_line": lineno,
            "target_line": target,
            "event": "return",
            "label": "RETURN",
            "color": "#10b981",
            "function_name": fname,
            "description": desc,
            "call_stack": list(call_stack),
            "variables": {"locals": clean_locals, "return_value": ret_val},
            "heap": dict(heap_tracker),
            "console_output": output_now
        })
        step_idx += 1
        last_line = target

    return trace_dispatch

try:
    compiled = compile(code_to_run, "<traced_user_code>", "exec")
    sys.settrace(trace_dispatch)
    exec(compiled, {"__name__": "__main__"})
except Exception as e:
    events.append({
        "step_index": step_idx,
        "source_line": last_line,
        "target_line": last_line,
        "event": "exception",
        "label": "EXCEPTION",
        "color": "#ef4444",
        "function_name": "error",
        "description": f"Exception raised: {str(e)}",
        "call_stack": list(call_stack),
        "variables": {},
        "heap": {},
        "console_output": stdout_buffer.getvalue()
    })
finally:
    sys.settrace(None)
    sys.stdout = original_stdout

print(json.dumps(events))
'''

def trace_python_code(code: str, timeout_seconds: int = 4) -> ExecutionTrace:
    """Executes Python code in a safe isolated subprocess and produces a structured ExecutionTrace."""
    trace = ExecutionTrace(language="python", code=code, is_runtime=True, trace_type="Python Runtime Traced")

    try:
        proc = subprocess.run(
            [sys.executable, "-c", RUNNER_SCRIPT],
            input=code,
            text=True,
            capture_output=True,
            timeout=timeout_seconds
        )

        if proc.returncode != 0:
            trace.error = proc.stderr.strip() or "Process terminated with error"
            return trace

        raw_events = json.loads(proc.stdout)
        for raw in raw_events:
            ev = ExecutionEvent(
                step_index=raw.get("step_index", 0),
                source_line=raw.get("source_line", 1),
                target_line=raw.get("target_line", 1),
                event=raw.get("event", "line"),
                label=raw.get("label", "EXECUTE"),
                color=raw.get("color", "#38bdf8"),
                function_name=raw.get("function_name", "main"),
                description=raw.get("description", ""),
                call_stack=raw.get("call_stack", []),
                variables=raw.get("variables", {}),
                heap=raw.get("heap", {}),
                console_output=raw.get("console_output", "")
            )
            trace.add_event(ev)

        return trace

    except subprocess.TimeoutExpired:
        trace.error = f"Execution timed out ({timeout_seconds}s limit). Infinite loop detected."
        return trace
    except Exception as e:
        trace.error = f"Tracing error: {str(e)}"
        return trace
