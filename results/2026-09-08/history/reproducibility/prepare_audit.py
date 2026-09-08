#!/usr/bin/env python3
"""Select completed retry outputs and assemble cited source pages; never assign scores."""
import pathlib,json,re
R=pathlib.Path(__file__).resolve().parent
pages=json.loads((R/"source/pages.json").read_text())
for folder in (R/"runs").glob("*"):
 p=folder/"book-final-summary.json"
 if not p.exists():continue
 d=json.loads(p.read_text());seen=set()
 while d.get("superseded_by") and d["name"] not in seen:
  seen.add(d["name"]);p=folder/(d["superseded_by"]+".json");d=json.loads(p.read_text())
 if d.get("status")!="ok" or d.get("output_limit_reached"):continue
 text=d["output"];cited=set()
 for group in re.findall(r"\[PDF[^\]]+\]",text):
  for a,b in re.findall(r"(\d+)\s*[-–]\s*(\d+)",group):cited.update(range(int(a),int(b)+1))
  cited.update(int(n) for n in re.findall(r"\d+",group))
 cited=sorted(n for n in cited if 1<=n<=len(pages))
 (folder/"accepted-final-summary.md").write_text(text+"\n")
 (folder/"accepted-final-record.json").write_text(json.dumps({"request":d["name"],"fingerprint":d["fingerprint"],"fidelity":"Not established by completion"},indent=2))
 out=["# Source-check packet",f"Accepted request: {d['name']}",text,"\n# Cited pages"]
 for n in cited:out.append(f"\n## Physical PDF p. {n}\n"+pages[n-1]["text"])
 (folder/"final-source-check-packet.md").write_text("\n\n".join(out))
 print(folder.name,d["name"],len(cited))
