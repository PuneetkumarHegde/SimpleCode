import unittest
from core.tracer.universal_tracer import generate_execution_trace
from core.tracer.java_tracer import trace_java_code
from core.tracer.python_tracer import trace_python_code
from core.sample_codes import SAMPLE_SNIPPETS


class TestTracerEngine(unittest.TestCase):
    def test_java_student_trace(self):
        java_code = SAMPLE_SNIPPETS["Java: Student Constructor & Execution Path"]["code"]
        trace = generate_execution_trace(java_code, "java")
        self.assertIsNone(trace.error)
        self.assertGreaterEqual(len(trace.events), 9)
        self.assertTrue(trace.is_runtime)
        
        # Verify key labels
        labels = [e.label for e in trace.events]
        self.assertTrue(any("CONSTRUCTOR" in l for l in labels))
        self.assertTrue(any("ASSIGN" in l for l in labels))
        self.assertTrue(any("RETURN" in l for l in labels))
        self.assertTrue(any("OUTPUT" in l for l in labels))
        self.assertTrue(any("CALL" in l for l in labels))
        
        # Verify output '101'
        outputs = [e.console_output for e in trace.events if e.console_output]
        self.assertTrue(any("101" in out for out in outputs))

        # Verify variable id = 101
        has_id_var = any(
            any(v.get("name") == "id" and "101" in str(v.get("value", "")) for v in e.variables.get("locals", []))
            for e in trace.events
        )
        self.assertTrue(has_id_var)

        # Verify heap object
        has_student_heap = any(
            any("Student" in h.get("type", "") for h in e.heap.values())
            for e in trace.events
        )
        self.assertTrue(has_student_heap)

    def test_python_runtime_trace(self):
        py_code = """def add(a, b):
    res = a + b
    return res

val = add(10, 20)
print(f"Result: {val}")
"""
        trace = trace_python_code(py_code)
        self.assertIsNone(trace.error)
        self.assertGreater(len(trace.events), 0)
        self.assertTrue(trace.is_runtime)
        
        # Check that console output captured "Result: 30"
        outputs = [e.console_output for e in trace.events if e.console_output]
        self.assertTrue(any("30" in out for out in outputs))

    def test_fallback_simulation(self):
        cpp_code = """int main() {
    int x = 42;
    return x;
}"""
        trace = generate_execution_trace(cpp_code, "cpp")
        self.assertIsNone(trace.error)
        self.assertFalse(trace.is_runtime)
        self.assertGreater(len(trace.events), 0)


if __name__ == "__main__":
    unittest.main()
