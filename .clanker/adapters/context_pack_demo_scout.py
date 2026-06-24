import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
context_pack = payload["context_pack"]
pack = json.loads(Path(context_pack["json_path"]).read_text(encoding="utf-8"))
top_files = [item["path"] for item in pack.get("ranked_files", [])[:3]]
if not top_files:
    top_files = ["agent_os/context_pack.py"]
expected_schema = payload["delegation"]["expected_output_schema"]
structured = {
    "options": [
        {
            "title": "Inspect context-pack surfaces",
            "files": top_files,
            "reason": "Selected from context_pack ranked_files.",
        }
    ]
}
if expected_schema == "file_relevance_report":
    structured = {
        "files": top_files,
        "findings": ["Context pack produced ranked candidate files."],
        "relevant_files": top_files,
    }
print(json.dumps({"result_summary": "Context pack scout demo completed.", "structured_output": structured}))
