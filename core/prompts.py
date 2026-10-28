"""
Prompt templates and schema definitions for Google GenAI SDK interactions.
"""

SYSTEM_INSTRUCTION = """You are CodeXplain Hub, an elite AI developer workspace assistant.
Your mission is to transform complex, raw source code into clear, structured, human-readable insights.
You excel at:
1. Translating cryptic syntax into plain-English functional concepts without unnecessary jargon.
2. Step-by-step sequential execution tracing.
3. Auto-debugging logical flaws, concurrency traps, boundary/off-by-one errors, and syntax anomalies.
4. Simulating and visualizing scope keywords (e.g. Java 'this' and 'super', Python 'self' and 'cls', C++ pointers/references) using arrow marks (──►) to show what memory or class context they point to.
5. Providing algorithmic complexity ratings (1-10) with Big-O notations.
6. Idiomatic cross-language code translation (Python, JavaScript, C++, Java, Go, Rust).

When requested in JSON format, output valid JSON only.
"""

def get_full_analysis_prompt(code: str, language: str) -> str:
    return f"""Perform an end-to-end full analysis on the following {language} code.

Special requirement for OOP keywords:
If the code contains keywords like 'this', 'super', 'self', 'cls', or pointer dereferences:
Trace and simulate what each keyword points to at runtime using arrow representations (e.g., 'this.speed ──► Current Instance Heap [@0x7F2A]', 'super.displaySpecs() ──► Parent Vehicle Class Frame').

Output MUST be a valid JSON object strictly adhering to this schema:
{{
  "functional_overview": {{
    "summary": "High-level human-readable summary without dense technical jargon",
    "capabilities": ["Capability 1", "Capability 2", "Capability 3"],
    "inputs": [{{"param": "name", "type": "type", "description": "desc"}}],
    "outputs": {{"type": "return type", "description": "desc"}},
    "mermaid": "graph TD\\n  A[Start] --> B[Process]\\n  B --> C[End]"
  }},
  "keyword_simulation": {{
    "has_keywords": true,
    "mappings": [
      {{
        "keyword": "this.field or super.method()",
        "arrow_target": "Current Instance in Heap OR Parent Superclass Frame",
        "role": "Disambiguates parameter shadowing OR invokes base class",
        "explanation": "Clear explanation of how this pointer behaves in memory at runtime"
      }}
    ],
    "arrow_diagram": "SubClass.this ──► [Current Instance: @0x4B3F]\\nSubClass.super ──► [Parent Superclass: @Base]",
    "mermaid_scope": "graph TD\\n  SubClass -- this --> InstanceHeap\\n  SubClass -- super --> ParentClass"
  }},
  "line_breakdown": [
    {{
      "line_range": "Lines X-Y",
      "code": "code snippet",
      "explanation": "sequential breakdown of variables, state, condition"
    }}
  ],
  "debugger": {{
    "status": "Errors Detected or Clean / Optimized",
    "summary": "Summary of flaws and health",
    "issues": [
      {{
        "severity": "Critical or Warning or Optimization",
        "title": "Issue title",
        "description": "What went wrong",
        "fix": "How to resolve"
      }}
    ],
    "corrected_code": "Full corrected, copy-pasteable code"
  }},
  "complexity": {{
    "score": 4,
    "badge": "Medium Complexity",
    "badge_color": "#f59e0b",
    "time_complexity": "O(n)",
    "space_complexity": "O(1)",
    "cyclomatic_complexity": "Branching depth explanation",
    "bottlenecks": "Hotspot identification",
    "architecture_critique": "Architectural and design evaluation"
  }}
}}

Source Code ({language}):
```{language}
{code}
```
"""

def get_translation_prompt(code: str, source_lang: str, target_lang: str) -> str:
    return f"""Rewrite the following {source_lang} logic into idiomatic, modern {target_lang}.
Ensure that language-specific paradigms (e.g. error handling, memory safety, types, async conventions) are properly respected.

Format your response as valid JSON with the following structure:
{{
  "target_language": "{target_lang}",
  "translated_code": "Complete, runnable idiomatic {target_lang} code",
  "notes": [
    "Key difference or idiom note 1",
    "Key difference or idiom note 2"
  ]
}}

Source Code ({source_lang}):
```{source_lang}
{code}
```
"""
