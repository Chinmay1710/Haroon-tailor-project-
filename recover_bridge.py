import json

transcript_path = "/Users/chinmay/.gemini/antigravity-ide/brain/d3e57774-4874-47d3-af74-ca41ea131621/.system_generated/logs/transcript_full.jsonl"

best_content = ""
max_len = 0

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
            if entry.get("type") == "PLANNER_RESPONSE" and "tool_calls" in entry:
                for tc in entry["tool_calls"]:
                    # Maybe I wrote to it?
                    if tc["name"] == "write_to_file" and "web_bridge.py" in tc["args"].get("TargetFile", ""):
                        content = tc["args"].get("CodeContent", "")
                        if len(content) > max_len:
                            max_len = len(content)
                            best_content = content
                            
                    # Or my python script re-wrote it?
                    if tc["name"] == "run_command" and "web_bridge.py" in tc["args"].get("CommandLine", ""):
                        cmd = tc["args"]["CommandLine"]
                        if "missing_handlers = " in cmd:
                            pass # This was the truncation bug script
                            
        except Exception as e:
            pass
            
print(f"Found {max_len} bytes")
if best_content:
    with open("app/ui/web_bridge.py.recovered", "w") as f:
        f.write(best_content)
