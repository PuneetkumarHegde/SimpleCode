"""Tracer package initialization."""
from core.tracer.event_model import ExecutionEvent, ExecutionTrace
from core.tracer.universal_tracer import generate_execution_trace

__all__ = ["ExecutionEvent", "ExecutionTrace", "generate_execution_trace"]
