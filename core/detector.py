"""
Language Detection Engine for CodeXplain Hub.
Automatically identifies programming languages from file extensions or source code contents.
"""

import re
from typing import Tuple

EXTENSION_MAP = {
    "java": "java",
    "py": "python",
    "js": "javascript",
    "mjs": "javascript",
    "cjs": "javascript",
    "ts": "typescript",
    "tsx": "typescript",
    "jsx": "javascript",
    "cpp": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "hpp": "cpp",
    "h": "cpp",
    "c": "cpp",
    "cs": "csharp",
    "go": "go",
    "rs": "rust",
    "php": "php",
    "rb": "ruby",
    "kt": "kotlin",
    "kts": "kotlin",
    "swift": "swift",
    "sql": "sql",
    "sh": "shell",
    "bash": "shell",
    "html": "html",
    "css": "css"
}

LANGUAGE_NAMES = {
    "java": "Java",
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "cpp": "C++",
    "csharp": "C#",
    "go": "Go",
    "rust": "Rust",
    "php": "PHP",
    "ruby": "Ruby",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "sql": "SQL",
    "shell": "Shell / Bash"
}

def detect_language(code: str, filename: str = None) -> Tuple[str, str]:
    """
    Detects language from filename or code snippet content.
    Returns (lang_key, display_name).
    """
    if filename:
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext in EXTENSION_MAP:
            lang_key = EXTENSION_MAP[ext]
            return lang_key, LANGUAGE_NAMES.get(lang_key, lang_key.capitalize())

    content = code.strip()
    if not content:
        return "python", "Python"

    # Java patterns
    if re.search(r'\b(public|private|protected)\s+(class|interface|enum|void|int|String|boolean)\b', content) or \
       re.search(r'System\.(out|err)\.print', content) or \
       re.search(r'\b(extends|implements)\s+\w+', content) or \
       re.search(r'\bpackage\s+[a-z0-9_.]+\s*;', content):
        return "java", "Java"

    # C++ patterns
    if re.search(r'#include\s*<[a-z0-9_]+>', content) or \
       re.search(r'\bstd::(cout|cin|vector|string|map|shared_ptr)\b', content) or \
       re.search(r'cout\s*<<', content):
        return "cpp", "C++"

    # Go patterns
    if re.search(r'\bpackage\s+\w+\b', content) and re.search(r'\bfunc\s+\w+\s*\(', content):
        return "go", "Go"

    # Rust patterns
    if re.search(r'\bfn\s+\w+\s*\(', content) and (re.search(r'\blet\s+(mut\s+)?\w+', content) or 'impl' in content):
        return "rust", "Rust"

    # C# patterns
    if re.search(r'\busing\s+System(\.[a-zA-Z0-9_]+)?\s*;', content) or \
       re.search(r'\bnamespace\s+[A-Za-z0-9_.]+', content):
        return "csharp", "C#"

    # TypeScript / JavaScript patterns
    if re.search(r'\b(interface|type)\s+[A-Z]\w*\s*=', content) or re.search(r':\s*(string|number|boolean|any)\[\]?', content):
        return "typescript", "TypeScript"

    if re.search(r'\b(const|let|var)\s+\w+\s*=', content) or \
       re.search(r'console\.(log|error|warn)\(', content) or \
       re.search(r'=>\s*\{?', content):
        return "javascript", "JavaScript"

    # PHP patterns
    if "<?php" in content or re.search(r'\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*', content):
        return "php", "PHP"

    # Python patterns (default fallback or checked via indentation / keywords)
    if re.search(r'\bdef\s+\w+\s*\(', content) or \
       re.search(r'\b(import\s+\w+|from\s+\w+\s+import)', content) or \
       re.search(r'\b(elif|self|__init__|__name__)\b', content):
        return "python", "Python"

    # Default to Python if ambiguous
    return "python", "Python"
