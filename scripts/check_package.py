#!/usr/bin/env python3
"""Check packaged entrypoints, skill metadata, Python syntax and private-path leaks."""
import ast
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
errors=[]
required=["README.md","BOOTSTRAP.md","runtime.md","docs/TRAINING.md",
          "scripts/install.py","scripts/inventory.py","scripts/prompt_gate.py",
          "scripts/claude_bridge.py","templates/personal/START-HERE.md"]
for name in required:
    if not (root/name).is_file(): errors.append("Missing "+name)
for path in root.rglob("*"):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts: continue
    if path.suffix not in (".md",".py",".json",".yml"): continue
    text=path.read_text()
    if path.suffix==".py":
        try: ast.parse(text)
        except SyntaxError as exc: errors.append(str(exc))
    if path.name=="SKILL.md" and not re.match(r"---\nname: .+\ndescription: .+", text):
        errors.append("Missing skill frontmatter "+str(path.relative_to(root)))
    if "/Users/"+"tylereg" in text or "second "+"brain" in text:
        errors.append("Private author path/reference "+str(path.relative_to(root)))
    if path.suffix==".md":
        for target in re.findall(r"\]\(([^)]+)\)",text):
            if "://" in target or target.startswith("#"): continue
            target=target.split("#")[0]
            if target and not (path.parent/target).exists():
                errors.append("Broken link "+str(path.relative_to(root))+": "+target)
if errors:
    print("\n".join(errors))
    raise SystemExit(1)
print("Package structure, links, skill metadata and Python syntax pass.")

