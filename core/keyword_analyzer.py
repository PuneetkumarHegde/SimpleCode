"""
Keyword & Scope Visualizer / Simulator.
Analyzes OOP keywords like 'this', 'super', 'self', 'cls', 'base', and pointer references.
Simulates memory bindings and scope resolution with visual arrow diagrams.
"""

import re
from typing import Dict, Any, List

def analyze_scope_keywords(code: str, language: str) -> Dict[str, Any]:
    """Detects and generates simulated visual scope mappings for this, super, self, etc."""
    lang = language.lower()
    keywords_found = []
    explanations = []
    
    # Check for Java/JS/C++ 'this' and 'super'
    has_this = bool(re.search(r'\bthis\b', code))
    has_super = bool(re.search(r'\bsuper\b', code))
    has_self = bool(re.search(r'\bself\b', code))
    has_cls = bool(re.search(r'\bcls\b', code))
    has_pointers = bool(re.search(r'->|\*\w+|&\w+', code)) and lang in ["cpp", "c", "go", "rust"]

    if has_this:
        keywords_found.append("this")
        # Find specific usages like this.field or this(...)
        this_usages = re.findall(r'this\.(\w+)|this\((.*?)\)', code)
        examples = [f"this.{u[0]}" if u[0] else f"this({u[1]})" for u in this_usages[:4]]
        explanations.append({
            "keyword": "this",
            "arrow_target": "Current Object Instance [Heap: this ──► 0x7F...]",
            "role": "Instance Self-Reference",
            "description": "Binds explicitly to the current active instance of the class in memory. It prevents variable shadowing between method parameters and instance fields.",
            "usages": examples or ["this.field"]
        })

    if has_super:
        keywords_found.append("super")
        super_usages = re.findall(r'super\.(\w+)|super\((.*?)\)', code)
        examples = [f"super.{u[0]}" if u[0] else f"super({u[1]})" for u in super_usages[:4]]
        explanations.append({
            "keyword": "super",
            "arrow_target": "Parent Superclass Context [Inheritance: super ──► Base Class]",
            "role": "Superclass Delegation",
            "description": "Bypasses the current class method or field overrides to access the immediate parent class constructor, methods, or shadowed properties.",
            "usages": examples or ["super.method()", "super(...)"]
        })

    if has_self:
        keywords_found.append("self")
        explanations.append({
            "keyword": "self",
            "arrow_target": "Instance State [self ──► Current Instance Namespace]",
            "role": "Explicit Instance Pointer (Python)",
            "description": "Represents the specific instance on which a method is invoked, allowing direct access to instance attributes and methods.",
            "usages": ["self.attribute", "self.method()"]
        })

    if has_cls:
        keywords_found.append("cls")
        explanations.append({
            "keyword": "cls",
            "arrow_target": "Class Object Factory [cls ──► Metaclass / Class Definition]",
            "role": "Class-Level Pointer (Python @classmethod)",
            "description": "Binds to the class definition itself rather than a single instance, typically used in class factory methods.",
            "usages": ["cls(...)"]
        })

    # Generate ASCII Arrow simulation diagram
    arrow_diagram = []
    if has_this and has_super:
        arrow_diagram = [
            "┌────────────────────────────────────────────────────────┐",
            "│                     BASE SUPERCLASS                    │",
            "│  [Constructors, Methods, and Inherited Fields]         │",
            "└───────────────────────────▲────────────────────────────┘",
            "                            │",
            "           super(...)       │  Delegates to Parent",
            "        ┌───────────────────┘",
            "        │",
            "┌───────┴────────────────────────────────────────────────┐",
            "│                    CURRENT SUBCLASS                    │",
            "│                                                        │",
            "│   this.field  ──────►  [Current Instance Heap: @0x4A]  │",
            "│   super.field ──────►  [Parent Superclass Heap: @0x10] │",
            "└────────────────────────────────────────────────────────┘"
        ]
    elif has_this:
        arrow_diagram = [
            "┌────────────────────────────────────────────────────────┐",
            "│                 LOCAL METHOD FRAME                     │",
            "│   Parameter: (x, y)                                    │",
            "└───────────────────────────┬────────────────────────────┘",
            "                            │",
            "              this.x = x    │  Assigns to Heap Instance",
            "        ┌───────────────────┘",
            "        ▼",
            "┌────────────────────────────────────────────────────────┐",
            "│               CURRENT OBJECT HEAP MEMORY               │",
            "│   this.x ────────► [Instance Field Storage: x]         │",
            "│   this.y ────────► [Instance Field Storage: y]         │",
            "└────────────────────────────────────────────────────────┘"
        ]
    elif has_self:
        arrow_diagram = [
            "┌────────────────────────────────────────────────────────┐",
            "│                     CALL CONTEXT                       │",
            "│   obj.do_something()                                   │",
            "└───────────────────────────┬────────────────────────────┘",
            "                            │ passes 'obj' as first arg",
            "        ┌───────────────────┘",
            "        ▼",
            "┌────────────────────────────────────────────────────────┐",
            "│                 METHOD FRAME (self)                    │",
            "│   self.data ─────► Points to obj's dictionary (__dict__)│",
            "└────────────────────────────────────────────────────────┘"
        ]

    # Mermaid Scope Flowchart
    mermaid_lines = ["graph TD"]
    if has_super:
        mermaid_lines.append("    ParentClass[\"🏛️ Parent Superclass (Base)\"]")
        mermaid_lines.append("    SubClass[\"🚗 Current Subclass (Derived)\"]")
        mermaid_lines.append("    SubClass -- \"super(...) / super.method()\" -->|Resolves to Parent| ParentClass")
    if has_this:
        mermaid_lines.append("    Instance[\"📦 Current Instance in Heap (@0x7F2A)\"]")
        mermaid_lines.append("    SubClass -- \"this.field\" -->|Binds to Instance| Instance")
        mermaid_lines.append("    LocalParams[\"📝 Local Method Parameters (shadowed)\"]")
        mermaid_lines.append("    SubClass -. \"disambiguates from\" .-> LocalParams")
    if has_self:
        mermaid_lines.append("    PyInstance[\"🐍 Current Instance Object (__dict__)\"]")
        mermaid_lines.append("    PyMethod[\"def method(self)\"]")
        mermaid_lines.append("    PyMethod -- \"self.attribute\" -->|Mutates State| PyInstance")

    return {
        "has_keywords": bool(keywords_found),
        "keywords": keywords_found,
        "explanations": explanations,
        "arrow_diagram": "\n".join(arrow_diagram) if arrow_diagram else None,
        "mermaid_diagram": "\n".join(mermaid_lines) if len(mermaid_lines) > 1 else None
    }
