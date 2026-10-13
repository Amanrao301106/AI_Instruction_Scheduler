import sqlite3
import re
from pathlib import Path

DB = Path(r"C:\Users\AMAN\AppData\Roaming\Cursor\User\globalStorage\conversation-search.db")
OUT = Path(r"C:\Users\AMAN\OneDrive\Apps\Desktop\AI_Instruction_Scheduler\_spec_extract")
OUT.mkdir(exist_ok=True)

con = sqlite3.connect(str(DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

targets = [
    "bc-fd306617-554e-4309-8da7-fffce395f32a",
    "bc-f99abb1c-c376-401a-af09-326bbc63057d",
]

# Dump full bodies
for tid in targets:
    row = cur.execute("""
        SELECT c.id, c.title, f.body, f.branches
        FROM conversations c
        JOIN conversation_fts f ON f.rowid = c.fts_rowid
        WHERE c.id = ?
    """, (tid,)).fetchone()
    if not row:
        print("MISSING", tid)
        continue
    path = OUT / f"{tid}_body.txt"
    path.write_text(row["body"] or "", encoding="utf-8")
    (OUT / f"{tid}_branches.txt").write_text(row["branches"] or "", encoding="utf-8")
    print(f"Wrote {path} len={len(row['body'] or '')}")

# Many FTS keyword queries - dump snippets with context
queries = [
    "PROJECT GOAL",
    "FOLDER STRUCTURE",
    "DEPENDENCY_ANALYZER",
    "dependency_analyzer",
    "PERFORMANCE.PY",
    "performance.py",
    "EXAMPLES.PY",
    "examples.py",
    "README",
    "APP.PY",
    "app.py",
    "Streamlit",
    "pipeline",
    "AI scoring",
    "score",
    "LOAD STORE ADD SUB MUL DIV",
    "supported instructions",
    "instruction",
    "RAW",
    "hazard",
    "stall",
    "IPC",
    "speedup",
    "requirements",
    "main.py",
    "ai_scheduler",
    "scheduler",
    "UI",
    "section 1",
    "1.",
    "2.",
    "3.",
    "4.",
    "5.",
    "6.",
    "7.",
    "8.",
    "9.",
    "10.",
    "folder",
    "module",
    "IF ID EX MEM WB",
    "five-stage",
    "priority",
    "heuristic",
    "latency",
    "example",
    "demo",
    "matplotlib",
    "networkx",
    "graph",
    "cycles",
    "throughput",
    "traditional",
    "out-of-order",
]

# Restrict FTS to instruction scheduling conversations by joining
fts_ids = [r["fts_rowid"] for r in cur.execute(
    "SELECT fts_rowid FROM conversations WHERE title LIKE '%instruction scheduling%' OR id IN (?, ?)",
    targets,
)]
print("FTS ids for scheduling:", fts_ids)

# Extract unique snippets from the two main bodies using keyword presence
for tid in targets:
    body = (OUT / f"{tid}_body.txt").read_text(encoding="utf-8")
    print(f"\n===== {tid} first 2000 chars =====")
    print(body[:2000])
    print(f"\n===== {tid} SECTION HEADERS =====")
    for m in re.finditer(r"(?m)^(?:#{1,6}\s+.*|(?:\d+\.)+\s+.*|[A-Z][A-Z0-9 _/\.-]{3,80})$", body):
        line = m.group(0).strip()
        if len(line) < 120:
            print(line)
