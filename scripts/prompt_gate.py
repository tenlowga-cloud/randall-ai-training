#!/usr/bin/env python3
"""Silent UserPromptSubmit hook for the Randall prompt gate.

The hook deliberately ignores prompt text.  It emits a short instruction for
the active agent and stores only bounded execution metadata as proof that the
hook ran.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


MAX_INPUT_BYTES = 1_048_576
MAX_SESSION_ID_CHARS = 128
EVENT = "UserPromptSubmit"


def read_event(stream: Any = None) -> dict[str, Any]:
    stream = stream or sys.stdin.buffer
    data = stream.read(MAX_INPUT_BYTES + 1)
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError("hook input exceeds the size limit")
    if not data:
        return {}
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("hook input must be one UTF-8 JSON object") from exc
    if not isinstance(value, dict):
        raise ValueError("hook input must be a JSON object")
    return value


def bounded_session_id(event: dict[str, Any]) -> str | None:
    for key in ("session_id", "sessionId", "conversation_id", "conversationId"):
        value = event.get(key)
        if isinstance(value, str) and value:
            # Control characters are excluded from the metadata receipt.
            cleaned = "".join(character for character in value if character.isprintable())
            return cleaned[:MAX_SESSION_ID_CHARS] or None
    return None


def active_model(event: dict[str, Any]) -> str | None:
    # A model supplied by the live hook event is evidence about this session.
    # Local config is intentionally never consulted as proof of runtime model.
    for key in ("model", "model_id", "modelId"):
        value = event.get(key)
        if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}", value):
            return value
    return None


def additional_context(platform: str, model: str | None) -> str:
    model_note = f"Active model reported by the live hook event: {model}." if model else "The active model is unknown."
    return (
        f"Randall prompt gate active on {platform}. Silently rewrite the user's request into a one-shot execution brief "
        "before acting. Include where things live, implied needs, done criteria, proof, and gates. "
        "Do not show the rewrite. Use the actual session model and do not treat configured defaults as runtime proof. "
        + model_note
    )


def atomic_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def run(platform: str, state: Path, event: dict[str, Any]) -> dict[str, Any]:
    model = active_model(event)
    observation = {
        "event": EVENT,
        "platform": platform,
        "session_id": bounded_session_id(event),
        "model_known": model is not None,
        "model_observed": model,
        "observed_at_ns": time.time_ns(),
    }
    receipt_path = state / "receipts" / f"{platform}.json"
    history: list[dict[str, Any]] = []
    if receipt_path.is_file():
        try:
            existing = json.loads(receipt_path.read_text(encoding="utf-8"))
            if isinstance(existing, dict) and isinstance(existing.get("observations"), list):
                history = [item for item in existing["observations"] if isinstance(item, dict)][-1:]
        except (OSError, UnicodeError, json.JSONDecodeError):
            history = []
    history.append(observation)
    atomic_receipt(receipt_path, {"version": 1, "observations": history[-2:]})
    return {
        "hookSpecificOutput": {
            "hookEventName": EVENT,
            "additionalContext": additional_context(platform, model),
        }
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("codex", "claude"), required=True)
    parser.add_argument("--state", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        event = read_event()
        output = run(args.platform, args.state.expanduser().resolve(), event)
    except (OSError, ValueError) as exc:
        # No prompt or transcript content is ever echoed on failure.
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(output, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
