import sqlite3
import json
import re
from pathlib import Path

DB = Path(r"C:\Users\AMAN\AppData\Roaming\Cursor\User\globalStorage\conversation-search.db")
OUT = Path(r"C:\Users\AMAN\OneDrive\Apps\Desktop\AI_Instruction_Scheduler\_spec_extract")
OUT.mkdir(exist_ok=True)

con = sqlite3.connect(str(DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

# List all conversations
convs = []
for r in cur.execute("SELECT source, scope, id, title, updated_at, is_archived, length(branches) as blen FROM conversations ORDER BY updated_at DESC"):
    convs.append(dict(r))
(OUT / "all_conversations.json").write_text(json.dumps(convs, indent=2), encoding="utf-8")
print("CONVERSATIONS:")
for c in convs:
    print(f"  {c['id']} | {c['title'][:80]} | src={c['source']} | blen={c['blen']}")

# Target IDs
targets = [
    "bc-fd306617-554e-4309-8da7-fffce395f32a",
    "bc-f99abb1c-c376-401a-af09-326bbc63057d",
    "fd306617",
    "f99abb1c",
]

print("\nTARGET MATCHES:")
for t in targets:
    rows = cur.execute(
        "SELECT source, scope, id, title FROM conversations WHERE id LIKE ?",
        (f"%{t}%",),
    ).fetchall()
    for r in rows:
        print(dict(r))

# Dump full bodies for target conversations via join with fts
print("\nFTS rowids linked:")
for r in cur.execute("SELECT fts_rowid, id, title FROM conversations"):
    print(r["fts_rowid"], r["id"][:50], r["title"][:60])

# For each conversation, dump body length from fts
for r in cur.execute("""
    SELECT c.id, c.title, length(f.body) as body_len, length(f.branches) as br_len
    FROM conversations c
    JOIN conversation_fts f ON f.rowid = c.fts_rowid
"""):
    print(f"BODY {r['id'][:40]} | {r['title'][:50]} | body={r['body_len']} br={r['br_len']}")
