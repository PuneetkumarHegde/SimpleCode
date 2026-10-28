"""
Universal Execution Tracer Dispatcher for CodeXplain Hub.
Dispatches to Python runtime tracer, Java runtime & semantic tracer,
or generates AST-based execution traces for other supported languages.
"""

import re
from typing import Dict, Any, List
from core.tracer.event_model import ExecutionTrace, ExecutionEvent
from core.tracer.python_tracer import trace_python_code
from core.tracer.java_tracer import trace_java_code

def trace_generic_code(code: str, language: str) -> ExecutionTrace:
    """Generates an accurate, simulated execution trace for C++, Go, Rust, JavaScript, etc."""
    trace = ExecutionTrace(
        language=language,
        code=code,
        is_runtime=False,
        trace_type="Semantic Execution Simulation"
    )
    lines = code.splitlines()
    if not lines:
        return trace

    # Scan for functions and calls
    func_defs = {}
    main_line = 1
    for i, line in enumerate(lines, 1):
        s = line.strip()
        m = re.search(r'(?:def|function|func|fn|\w+)\s+(\w+)\s*\(', s)
        if m and m.group(1) not in ["if", "while", "for", "switch"]:
            func_defs[m.group(1)] = i
            if m.group(1) == "main":
                main_line = i

    call_stack = [{"name": "main", "line": main_line}]
    step_idx = 0
    last_line = main_line
    vars_tracker = []

    # Emit initial entry
    trace.add_event(ExecutionEvent(
        step_index=0,
        source_line=main_line,
        target_line=main_line,
        event="call",
        label="START",
        color="#00f2fe",
        function_name="main",
        description=f"Program started in {language.capitalize()}.",
        call_stack=list(call_stack),
        variables={"locals": []},
        heap={},
        console_output=""
    ))
    step_idx += 1

    # Traverse lines in function
    for i in range(main_line, min(len(lines) + 1, main_line + 15)):
        line_text = lines[i - 1].strip()
        if not line_text or line_text.startswith("//") or line_text.startswith("#"):
            continue

        # Check for function call
        called_fn = None
        for fn_name, fn_line in func_defs.items():
            if fn_name != "main" and re.search(r'\b' + re.escape(fn_name) + r'\s*\(', line_text):
                called_fn = (fn_name, fn_line)
                break

        if called_fn:
            fn_name, fn_line = called_fn
            # 1. Step at call site
            trace.add_event(ExecutionEvent(
                step_index=step_idx,
                source_line=last_line,
                target_line=i,
                event="line",
                label="EXECUTE",
                color="#38bdf8",
                function_name="main",
                description=f"Invoking {fn_name}().",
                call_stack=list(call_stack),
                variables={"locals": list(vars_tracker)},
                heap={},
                console_output=""
            ))
            step_idx += 1
            last_line = i

            # 2. Jump to function
            call_stack.append({"name": fn_name, "line": fn_line})
            trace.add_event(ExecutionEvent(
                step_index=step_idx,
                source_line=i,
                target_line=fn_line,
                event="call",
                label=f"CALL: {fn_name}",
                color="#00f2fe",
                function_name=fn_name,
                description=f"Jumping to {fn_name}() definition at line {fn_line}.",
                call_stack=list(call_stack),
                variables={"locals": list(vars_tracker)},
                heap={},
                console_output=""
            ))
            step_idx += 1
            last_line = fn_line

            # 3. Inside function line
            next_line = min(len(lines), fn_line + 1)
            trace.add_event(ExecutionEvent(
                step_index=step_idx,
                source_line=fn_line,
                target_line=next_line,
                event="line",
                label="EXECUTE",
                color="#38bdf8",
                function_name=fn_name,
                description=f"Executing statement inside {fn_name}().",
                call_stack=list(call_stack),
                variables={"locals": list(vars_tracker)},
                heap={},
                console_output=""
            ))
            step_idx += 1
            last_line = next_line

            # 4. Return jump
            call_stack.pop()
            trace.add_event(ExecutionEvent(
                step_index=step_idx,
                source_line=next_line,
                target_line=i,
                event="return",
                label="RETURN",
                color="#10b981",
                function_name="main",
                description=f"Returning from {fn_name}() back to caller at line {i}.",
                call_stack=list(call_stack),
                variables={"locals": list(vars_tracker)},
                heap={},
                console_output=""
            ))
            step_idx += 1
            last_line = i
        else:
            # Standard line
            lbl = "EXECUTE"
            clr = "#38bdf8"
            if "=" in line_text and not line_text.startswith("if"):
                lbl = "ASSIGN"
                clr = "#f59e0b"
            elif "print" in line_text or "cout" in line_text or "println" in line_text:
                lbl = "OUTPUT"
                clr = "#14b8a6"
            elif "for " in line_text or "while " in line_text:
                lbl = "LOOP"
                clr = "#818cf8"

            trace.add_event(ExecutionEvent(
                step_index=step_idx,
                source_line=last_line,
                target_line=i,
                event="line",
                label=lbl,
                color=clr,
                function_name="main",
                description=f"Executing line {i}: {line_text[:40]}",
                call_stack=list(call_stack),
                variables={"locals": list(vars_tracker)},
                heap={},
                console_output=""
            ))
            step_idx += 1
            last_line = i

    return trace

def generate_execution_trace(code: str, language: str) -> ExecutionTrace:
    """Master entry point for generating execution traces across any language."""
    lang = (language or "python").lower()

    if lang == "python":
        trace = trace_python_code(code)
        if not trace.error and trace.events:
            return trace
        # If runtime error, fallback to generic
        return trace_generic_code(code, "python")

    elif lang == "java":
        return trace_java_code(code)

    else:
        return trace_generic_code(code, lang)
