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

# Schema dump
schema_lines = []
for r in cur.execute("SELECT type, name, sql FROM sqlite_master"):
    schema_lines.append(f"{r['type']}|{r['name']}|{r['sql']}")
(OUT / "schema.txt").write_text("\n".join(schema_lines), encoding="utf-8")

for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    name = r["name"]
    try:
        n = cur.execute(f"SELECT COUNT(*) AS c FROM [{name}]").fetchone()["c"]
    except Exception as e:
        n = str(e)
    schema_lines.append(f"COUNT {name}={n}")
(OUT / "schema.txt").write_text("\n".join(schema_lines), encoding="utf-8")

# Peek columns for each table
for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    name = r["name"]
    info = list(cur.execute(f"PRAGMA table_info([{name}])"))
    cols = [i["name"] for i in info]
    (OUT / f"cols_{name}.txt").write_text("\n".join(cols), encoding="utf-8")
    # sample rows
    try:
        rows = cur.execute(f"SELECT * FROM [{name}] LIMIT 3").fetchall()
        sample = []
        for row in rows:
            d = {k: (str(row[k])[:500] if row[k] is not None else None) for k in row.keys()}
            sample.append(json.dumps(d, ensure_ascii=False))
        (OUT / f"sample_{name}.txt").write_text("\n\n".join(sample), encoding="utf-8")
    except Exception as e:
        (OUT / f"sample_{name}.txt").write_text(str(e), encoding="utf-8")

print("schema written")
print((OUT / "schema.txt").read_text(encoding="utf-8")[:3000])
