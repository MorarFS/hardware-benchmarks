#!/usr/bin/env python3
"""Wait for the current sequential comparison, then resume stale checkpoints and capped outputs."""
import pathlib,subprocess,time,sys,json
R=pathlib.Path(__file__).resolve().parent
while subprocess.run(["systemctl","--user","is-active","--quiet","evo-history-benchmark.service"]).returncode==0:time.sleep(20)
if not (R/"book.complete").exists():
 (R/"repair-status.json").write_text(json.dumps({"state":"Main run failed; repair held for review"}));sys.exit(1)
(R/"book.complete").unlink()
(R/"repair-status.json").write_text(json.dumps({"state":"Completing capped source summaries sequentially","started":time.time()}))
ret=subprocess.run([sys.executable,str(R/"controller.py")]).returncode
(R/"repair-status.json").write_text(json.dumps({"state":"Finished" if ret==0 else "Error","returncode":ret,"finished":time.time()}))

if ret==0:(R/'completion.complete').write_text(str(time.time()))
sys.exit(ret)
