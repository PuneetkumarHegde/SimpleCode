"""
Standardized Execution Event Model for CodeXplain Hub.
Defines the schema for structured runtime and simulated execution traces.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import json

@dataclass
class StackFrame:
    name: str
    line: int
    file: str = "main"
    args: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HeapObject:
    id: str
    type: str
    fields: Dict[str, Any] = field(default_factory=dict)
    color: str = "#a855f7"

@dataclass
class ExecutionEvent:
    step_index: int
    source_line: int
    target_line: int
    event: str          # 'line', 'call', 'constructor_call', 'return', 'assign', 'branch', 'loop', 'output', 'exception'
    label: str          # 'EXECUTE', 'CALL', 'ENTER CONSTRUCTOR', 'RETURN', 'ASSIGN', 'BRANCH', 'LOOP', 'OUTPUT'
    color: str          # '#38bdf8', '#00f2fe', '#a855f7', '#10b981', '#f59e0b', '#ef4444'
    function_name: str
    description: str
    call_stack: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)  # {'locals': [...], 'globals': [...]}
    heap: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # {'Student@0x101': {'type': 'Student', 'fields': {...}}}
    console_output: str = ""
    active_keyword: Optional[str] = None

@dataclass
class ExecutionTrace:
    language: str
    code: str
    events: List[ExecutionEvent] = field(default_factory=list)
    is_runtime: bool = True     # True if real runtime execution, False if semantic simulation
    trace_type: str = "Runtime Traced"
    total_steps: int = 0
    error: Optional[str] = None

    def add_event(self, event: ExecutionEvent):
        self.events.append(event)
        self.total_steps = len(self.events)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "code": self.code,
            "is_runtime": self.is_runtime,
            "trace_type": self.trace_type,
            "total_steps": len(self.events),
            "error": self.error,
            "events": [asdict(e) for e in self.events]
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
