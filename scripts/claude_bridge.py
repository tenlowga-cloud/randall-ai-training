#!/usr/bin/env python3
"""Preview a bounded Claude task. Execution is explicit; no automatic login."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

def prepare(packet):
    if not isinstance(packet, dict):
        raise ValueError("Task packet must be a JSON object")
    if packet.get("classification") not in ("public", "cloud-approved"):
        raise ValueError("Only approved cloud material can use this bridge")
    if packet.get("cloud_approved") is not True:
        raise ValueError("Record approval for this task's cloud transfer")
    if packet.get("customizations_reviewed") is not True:
        raise ValueError("Review user hooks, plugins, instructions and managed policy first")
    if not isinstance(packet.get("workspace"), str):
        raise ValueError("workspace must be an absolute path string")
    workspace = Path(packet["workspace"])
    if not workspace.is_absolute() or not workspace.is_dir():
        raise ValueError("workspace must be an existing absolute directory")
    mode = packet.get("mode", "review")
    if mode not in ("review", "author"):
        raise ValueError("mode must be review or author")
    model = packet.get("model")
    brief = packet.get("brief")
    if not isinstance(model, str) or not model or model.startswith("-"):
        raise ValueError("Select a verified available model")
    if not isinstance(brief, str) or not brief.strip() or len(brief) > 50000:
        raise ValueError("Provide a bounded, approved brief up to 50000 characters")
    turns = packet.get("max_turns", 4)
    timeout = packet.get("timeout_seconds", 180)
    budget = packet.get("max_budget_usd")
    if type(budget) not in (int, float) or not 0 < budget <= 20:
        raise ValueError("Set an approved max_budget_usd greater than zero and at most 20")
    if type(turns) is not int or not 1 <= turns <= 10:
        raise ValueError("max_turns must be 1..10")
    if type(timeout) is not int or not 10 <= timeout <= 600:
        raise ValueError("timeout_seconds must be 10..600")
    command = ["claude", "-p", "--model", model, "--output-format", "json",
               "--max-turns", str(turns), "--permission-mode",
               "dontAsk" if mode == "review" else "acceptEdits",
               "--tools", "" if mode == "review" else "Read,Glob,Grep,Edit,Write",
               "--setting-sources", "user", "--strict-mcp-config",
               "--mcp-config", '{"mcpServers":{}}', "--disallowedTools", "mcp__*",
               "--no-session-persistence", "--max-budget-usd", str(budget)]
    prompt = ("Silently clarify this bounded task while preserving intent, examples and unknowns. "
              "Do only this assignment. Do not delegate or call another orchestrator. "
              "Return result, evidence, limitations and next action. File ownership in the brief "
              "is an instruction, not an operating-system sandbox.\n\n" + brief)
    return command, prompt, workspace, timeout

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text())
        command, prompt, workspace, timeout = prepare(packet)
        if not args.execute:
            print(json.dumps({"status":"preview-only", "command":command,
                              "workspace":str(workspace), "prompt_characters":len(prompt),
                              "timeout_seconds":timeout}, indent=2))
            return 0
        executable = shutil.which("claude")
        if not executable:
            raise ValueError("Claude CLI missing; follow official installation and login")
        command[0] = executable
        result = subprocess.run(command, input=prompt, text=True, cwd=workspace,
                                capture_output=True, timeout=timeout, check=False)
        if result.returncode:
            raise ValueError("Claude failed; inspect CLI auth/version/permissions locally. No automatic retry.")
        value = json.loads(result.stdout)
        if not isinstance(value, dict) or value.get("is_error") or value.get("subtype") not in (None,"success"):
            raise ValueError("Claude reported an incomplete or failed task")
        print(json.dumps({"status":"response-received-artifact-unverified",
                          "result":value.get("result"), "usage":value.get("usage"),
                          "modelUsage":value.get("modelUsage")}, indent=2))
        return 0
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status":"blocked", "reason":str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
