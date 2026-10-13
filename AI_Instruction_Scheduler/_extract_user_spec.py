import sqlite3
import re
from pathlib import Path

OUT = Path(r"C:\Users\AMAN\OneDrive\Apps\Desktop\AI_Instruction_Scheduler\_spec_extract")
DB = Path(r"C:\Users\AMAN\AppData\Roaming\Cursor\User\globalStorage\conversation-search.db")

# Prefer the longer / more complete user prompt across both convos
bodies = {}
for p in OUT.glob("bc-*_body.txt"):
    bodies[p.name] = p.read_text(encoding="utf-8")

# Extract user: blocks that contain PROJECT OBJECTIVE
def extract_user_specs(text: str):
    # Split by role markers commonly used in FTS indexing
    parts = re.split(r"(?m)^(user:|assistant:|system:)\s*", text)
    specs = []
    i = 0
    while i < len(parts):
        if parts[i] == "user:" and i + 1 < len(parts):
            content = parts[i + 1]
            if "PROJECT OBJECTIVE" in content or "AI-Accelerated Instruction Scheduling" in content:
                specs.append(content)
            i += 2
        else:
            i += 1
    return specs

all_specs = []
for name, body in bodies.items():
    specs = extract_user_specs(body)
    print(f"{name}: found {len(specs)} user spec blocks, body_len={len(body)}")
    for idx, s in enumerate(specs):
        outp = OUT / f"user_spec_{name}_{idx}.txt"
        outp.write_text(s, encoding="utf-8")
        print(f"  wrote {outp.name} len={len(s)}")
        all_specs.append((len(s), name, idx, s))

# Also dump entire bodies cleaned for reading
for name, body in bodies.items():
    # Keep only the first/longest user project prompt if embedded
    pass

# Pick longest spec
if all_specs:
    all_specs.sort(reverse=True)
    best = all_specs[0][3]
    (OUT / "BEST_USER_SPEC.txt").write_text(best, encoding="utf-8")
    print("BEST len", len(best))
else:
    # fallback: find start marker in each body
    for name, body in bodies.items():
        m = re.search(r"I want you to build a complete practical", body)
        if m:
            chunk = body[m.start():]
            # cut at next assistant: if present after a long stretch
            m2 = re.search(r"(?m)^assistant:", chunk[500:])
            if m2:
                chunk = chunk[: 500 + m2.start()]
            (OUT / f"fallback_{name}").write_text(chunk, encoding="utf-8")
            print("fallback", name, len(chunk))

# Also dump assistant responses that may restate the full spec / folder structure
con = sqlite3.connect(str(DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

# FTS searches for section content snippets
queries = [
    '"PROJECT OBJECTIVE"',
    '"TECHNOLOGY STACK"',
    '"PROJECT ARCHITECTURE"',
    '"SUPPORTED CPU"',
    '"DEPENDENCY ANALYZER"',
    '"PIPELINE MODEL"',
    '"AI-ACCELERATED SCHEDULER"',
    '"PERFORMANCE METRICS"',
    '"USER INTERFACE"',
    '"EXAMPLES.PY"',
    '"README.MD"',
    '"VIVA DEMONSTRATION"',
    '"FINAL DELIVERABLE"',
    "dependency_analyzer.py",
    "performance.py",
    "examples.py",
    "folder structure",
    "streamlit",
    "IF ID EX MEM WB",
]
snippet_out = []
for q in queries:
    try:
        rows = cur.execute("""
            SELECT c.id, c.title, snippet(conversation_fts, 1, '>>>', '<<<', '…', 64) AS snip
            FROM conversation_fts
            JOIN conversations c ON c.fts_rowid = conversation_fts.rowid
            WHERE conversation_fts MATCH ?
              AND c.title LIKE '%instruction scheduling%'
            LIMIT 5
        """, (q,)).fetchall()
        snippet_out.append(f"\n### QUERY: {q}\n")
        for r in rows:
            snippet_out.append(f"[{r['id']}]\n{r['snip']}\n")
    except Exception as e:
        snippet_out.append(f"\n### QUERY: {q} ERROR {e}\n")

(OUT / "fts_snippets.txt").write_text("\n".join(snippet_out), encoding="utf-8")
print("snippets written", len(snippet_out))
