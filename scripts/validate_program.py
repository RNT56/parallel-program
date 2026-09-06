#!/usr/bin/env python3
"""Validate a parallel-program registry, board, roster and handoffs. Fails closed.

Installed by the parallel-program skill at Docs/Execution/validate_program.py. It checks, against
the tracked file tree, that:

* no tracked file is owned by two lanes (a file in ``sharedFiles`` belongs to its declared owner);
* every owner glob matches at least one tracked file unless it is declared in ``plannedPaths``;
* every task ID a lane carries exists in a task source and is carried by exactly one lane;
* exactly one lane coordinates and exactly one integrates; the coordinator carries no task and
  owns nothing outside the programme directory, because an arbiter with a stake is not one;
* every agent name is one unique upper-case word, upstream references resolve, the roster names
  every agent and lane, and every handoff file is named for its lane's agent;
* every board row parses, names a known lane, checkpoint and state, and every shared-claim path
  exists.

It promotes no task state and reads no evidence. An unreadable registry, an unknown task ID or a
row it cannot parse is an error, never a skipped check. ``--self-test`` builds a fixture repository
and proves that each of those failures is actually caught.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_REGISTRY = "Docs/Execution/lanes.json"
BOARD_ROW = re.compile(r"^\|\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*(?P<lane>[^|]+?)\s*\|\s*(?P<cp>[^|]+?)\s*\|\s*(?P<state>[^|]+?)\s*\|\s*(?P<ref>[^|]*?)\s*\|\s*(?P<note>[^|]*?)\s*\|\s*$")
CLAIM_ROW = re.compile(r"^\|\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*(?P<lane>[^|]+?)\s*\|\s*(?P<path>[^|]+?)\s*\|\s*(?P<reason>[^|]*?)\s*\|\s*(?P<ack>[^|]*?)\s*\|\s*$")
OWNER_ROW = re.compile(r"^\|\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*(?P<lane>[^|]+?)\s*\|\s*(?P<needed>[^|]+?)\s*\|\s*(?P<entry>[^|]*?)\s*\|\s*(?P<status>[^|]*?)\s*\|\s*$")
SESSION = re.compile(r"^(?P<agent>[A-Z]+)-(?P<phase>\d+)(?P<cont>[a-z]?)\.md$")


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    out = "^"
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
            continue
        if pattern.startswith("**", i):
            out += ".*"
            i += 2
            continue
        ch = pattern[i]
        if ch == "*":
            out += "[^/]*"
        elif ch == "?":
            out += "[^/]"
        else:
            out += re.escape(ch)
        i += 1
    return re.compile(out + "$")


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", "replace").strip() or "git ls-files failed")
    return [entry for entry in result.stdout.decode("utf-8").split("\0") if entry]


def load_known_tasks(root: Path, registry: dict) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    known: set[str] = set()
    sources = registry.get("taskSources")
    if not isinstance(sources, list) or not sources:
        return known, ["taskSources must be a non-empty list of {path, pattern} or {path, tasksKey}"]
    for source in sources:
        rel = source.get("path") if isinstance(source, dict) else None
        if not rel or not (root / rel).is_file():
            errors.append(f"taskSources: missing file {rel!r}")
            continue
        text = (root / rel).read_text(encoding="utf-8")
        if rel.endswith(".json"):
            key = source.get("tasksKey", "tasks")
            try:
                tasks = json.loads(text)[key]
                ids = list(tasks.keys()) if isinstance(tasks, dict) else [t["id"] for t in tasks]
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"taskSources: {rel} has no readable {key!r}: {exc}")
                continue
        else:
            pattern = source.get("pattern")
            if not pattern:
                errors.append(f"taskSources: {rel} needs a pattern with one capture group")
                continue
            try:
                ids = re.findall(pattern, text, re.MULTILINE)
            except re.error as exc:
                errors.append(f"taskSources: bad pattern for {rel}: {exc}")
                continue
        if not ids:
            errors.append(f"taskSources: {rel} yielded no task IDs; the format or pattern is wrong")
        known.update(ids)
    return known, errors


def validate_registry(root: Path, registry: dict, files: list[str]) -> list[str]:
    errors: list[str] = []
    lanes = registry.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        return ["registry has no lanes"]
    keys = [lane.get("key") for lane in lanes]
    if len(set(keys)) != len(keys) or any(not k for k in keys):
        errors.append(f"lane keys must be unique and non-empty: {keys}")
    checkpoints = registry.get("checkpoints", [])
    checkpoint_ids = [cp.get("id") for cp in checkpoints]
    if not checkpoint_ids or len(set(checkpoint_ids)) != len(checkpoint_ids):
        errors.append("checkpoints must exist and have unique ids")
    states = registry.get("boardStates")
    if not isinstance(states, list) or not states:
        errors.append("boardStates must be a non-empty list")
    for path_key in ("roadmap", "board", "checkpoints", "roster", "coordination", "decisions", "changelog", "validator"):
        rel = registry.get("authority", {}).get(path_key)
        if not rel or not (root / rel).is_file():
            errors.append(f"authority.{path_key} does not point to an existing file: {rel}")
    if registry.get("buildPolicy") not in ("integrator-only", "lanes-focused"):
        errors.append(f"buildPolicy must be integrator-only or lanes-focused, found {registry.get('buildPolicy')!r}")

    planned = set(registry.get("plannedPaths", []))
    shared_owner: dict[str, str] = {}
    for entry in registry.get("sharedFiles", []):
        shared_owner[entry["path"]] = entry["owner"]
        if entry["path"] not in files:
            errors.append(f"sharedFiles: {entry['path']} is not a tracked file")
        if entry["owner"] not in keys:
            errors.append(f"sharedFiles: owner {entry['owner']} of {entry['path']} is not a lane")
        for claimant in entry.get("claimants", []):
            if claimant not in keys:
                errors.append(f"sharedFiles: claimant {claimant} of {entry['path']} is not a lane")

    ownership: dict[str, set[str]] = {}
    for lane in lanes:
        key = lane.get("key", "?")
        brief = lane.get("brief")
        if not brief or not (root / brief).is_file():
            errors.append(f"{key}: brief does not exist: {brief}")
        for cp in lane.get("checkpointDeliverables", {}):
            if cp not in checkpoint_ids:
                errors.append(f"{key}: checkpointDeliverables names unknown checkpoint {cp}")
        excluded = [glob_to_regex(p) for p in lane.get("excludedPaths", [])]
        owner_paths = lane.get("ownerPaths", [])
        if not owner_paths:
            errors.append(f"{key}: ownerPaths is empty; a lane that owns nothing cannot write anything")
        for pattern in owner_paths:
            regex = glob_to_regex(pattern)
            matched = [f for f in files if regex.match(f) and not any(x.match(f) for x in excluded)]
            if not matched and pattern not in planned:
                errors.append(f"{key}: owner path {pattern!r} matches no tracked file (declare it under plannedPaths if it is future work)")
            for f in matched:
                ownership.setdefault(f, set()).add(key)
    for f, owners in sorted(ownership.items()):
        if len(owners) > 1 and not (f in shared_owner and shared_owner[f] in owners):
            errors.append(f"path owned by more than one lane: {f} -> {sorted(owners)}")
    for f, owner in shared_owner.items():
        if f in ownership and owner not in ownership[f]:
            errors.append(f"sharedFiles: {f} declares owner {owner} but that lane's ownerPaths do not cover it")

    known, task_errors = load_known_tasks(root, registry)
    errors.extend(task_errors)
    carried: dict[str, list[str]] = {}
    for lane in lanes:
        for task in lane.get("tasks", []):
            if task not in known:
                errors.append(f"{lane['key']}: task {task} does not exist in any task source")
            carried.setdefault(task, []).append(lane["key"])
        for team in lane.get("subTeams", []):
            for task in team.get("tasks", []):
                if task not in lane.get("tasks", []):
                    errors.append(f"{lane['key']}: sub-team {team.get('name')} carries {task}, which the lane does not list")
    for task, owners in sorted(carried.items()):
        if len(owners) > 1:
            errors.append(f"task carried by more than one lane: {task} -> {owners}")
    for dep in registry.get("dependencies", []):
        for field in ("neededBy", "from"):
            who = dep.get(field)
            if who not in keys and who != "owner":
                errors.append(f"dependencies: {field} {who!r} is not a lane or 'owner'")
    return errors


def validate_agents(root: Path, registry: dict, program_dir: str) -> list[str]:
    errors: list[str] = []
    lanes = registry.get("lanes", [])
    names: dict[str, str] = {}
    for lane in lanes:
        key = lane.get("key", "?")
        name = lane.get("agentName")
        if not name or not name.isupper() or not name.isalpha():
            errors.append(f"{key}: agentName must be a single upper-case word, found {name!r}")
            continue
        if name in names:
            errors.append(f"agent name {name} is used by both {names[name]} and {key}")
        names[name] = key
        if not isinstance(lane.get("phases"), list):
            errors.append(f"{key}: phases must be a list")
    for lane in lanes:
        for upstream in lane.get("upstreamAgents", []):
            if upstream not in names:
                errors.append(f"{lane.get('key')}: upstreamAgents names {upstream}, which is not an agent")
            elif names[upstream] == lane.get("key"):
                errors.append(f"{lane.get('key')}: lists itself as an upstream agent")

    roles: dict[str, list[str]] = {}
    for lane in lanes:
        roles.setdefault(lane.get("role", "delivery"), []).append(lane.get("key", "?"))
    for role in ("coordination", "integration"):
        holders = roles.get(role, [])
        if len(holders) != 1:
            errors.append(f"exactly one lane must have role {role!r}, found {holders}")
    for key in roles.get("coordination", []):
        lane = next(lane for lane in lanes if lane.get("key") == key)
        if lane.get("tasks"):
            errors.append(f"{key}: the coordinating lane must carry no task, found {lane['tasks']}")
        stray = [p for p in lane.get("ownerPaths", []) if not p.startswith(program_dir)]
        if stray:
            errors.append(f"{key}: the coordinating lane may own only the plan and the record under {program_dir}, found {stray}")

    naming = registry.get("agentNaming")
    if not isinstance(naming, dict) or not naming.get("handoffPath") or not naming.get("sessionName"):
        errors.append("agentNaming must declare sessionName and handoffPath")

    rel = registry.get("authority", {}).get("roster")
    if rel and (root / rel).is_file():
        roster = (root / rel).read_text(encoding="utf-8")
        for name, key in sorted(names.items()):
            if name not in roster:
                errors.append(f"{rel}: does not name agent {name}")
            if key not in roster:
                errors.append(f"{rel}: does not name lane {key}")
        for word in re.findall(r"\*\*([A-Z]{3,})\*\*", roster):
            if word not in names:
                errors.append(f"{rel}: names agent {word}, which no lane declares")

    handoffs = root / program_dir / "Handoffs"
    for lane in lanes:
        directory = handoffs / lane.get("key", "?")
        if not directory.is_dir():
            errors.append(f"{lane.get('key')}: handoff directory missing: {directory.relative_to(root)}")
            continue
        for entry in sorted(directory.iterdir()):
            if entry.suffix != ".md" or entry.name == "README.md":
                continue
            match = SESSION.match(entry.name)
            if not match:
                errors.append(f"{entry.relative_to(root)}: handoff name must be <AGENT>-<phase>[letter].md")
            elif match["agent"] != lane.get("agentName"):
                errors.append(f"{entry.relative_to(root)}: named for {match['agent']}, but this lane's agent is {lane.get('agentName')}")
    return errors


def validate_board(root: Path, registry: dict) -> list[str]:
    errors: list[str] = []
    rel = registry.get("authority", {}).get("board")
    if not rel or not (root / rel).is_file():
        return [f"board file missing: {rel}"]
    lines = (root / rel).read_text(encoding="utf-8").splitlines()
    lane_keys = {lane["key"] for lane in registry["lanes"]}
    checkpoint_ids = {cp["id"] for cp in registry.get("checkpoints", [])}
    states = set(registry.get("boardStates", []))
    section = None
    board_rows = 0
    for number, line in enumerate(lines, start=1):
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not line.startswith("|") or set(line.strip()) <= {"|", "-", " ", ":"}:
            continue
        if line.lstrip("| ").lower().startswith("date"):
            continue
        if section == "board":
            match = BOARD_ROW.match(line)
            if not match:
                errors.append(f"{rel}:{number}: board row does not parse: {line.strip()}")
                continue
            board_rows += 1
            if match["lane"] not in lane_keys:
                errors.append(f"{rel}:{number}: unknown lane {match['lane']!r}")
            if match["cp"] not in checkpoint_ids:
                errors.append(f"{rel}:{number}: unknown checkpoint {match['cp']!r}")
            if match["state"] not in states:
                errors.append(f"{rel}:{number}: unknown state {match['state']!r}; allowed: {sorted(states)}")
        elif section == "shared claims":
            match = CLAIM_ROW.match(line)
            if not match:
                errors.append(f"{rel}:{number}: shared-claim row does not parse: {line.strip()}")
                continue
            if match["lane"] not in lane_keys:
                errors.append(f"{rel}:{number}: unknown lane {match['lane']!r}")
            if not (root / match["path"]).exists():
                errors.append(f"{rel}:{number}: claimed path does not exist: {match['path']}")
        elif section and section.startswith("owner decisions"):
            match = OWNER_ROW.match(line)
            if not match:
                errors.append(f"{rel}:{number}: owner-decision row does not parse: {line.strip()}")
            elif match["lane"] not in lane_keys:
                errors.append(f"{rel}:{number}: unknown lane {match['lane']!r}")
    if board_rows == 0:
        errors.append(f"{rel}: the Board section has no rows; a board that records nothing cannot prove the programme started")
    return errors


def run(root: Path, registry_rel: str = DEFAULT_REGISTRY) -> list[str]:
    registry_path = root / registry_rel
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"cannot read {registry_rel}: {exc}"]
    try:
        files = tracked_files(root)
    except RuntimeError as exc:
        return [f"cannot list tracked files: {exc}"]
    if not files:
        return ["git ls-files returned no paths; refusing to validate ownership against an empty tree"]
    program_dir = str(Path(registry_rel).parent) + "/"
    errors = validate_registry(root, registry, files)
    errors.extend(validate_agents(root, registry, program_dir))
    errors.extend(validate_board(root, registry))
    return errors


# --- self-test -------------------------------------------------------------------------------

def _fixture(directory: str) -> tuple[Path, dict]:
    root = Path(directory)
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    board = (
        "# board\n\n## Board\n\n| Date | Lane | Checkpoint | State | Ref | Note |\n| --- | --- | --- | --- | --- | --- |\n"
        "| 2026-01-01 | LC-coordination | CP0 | CLAIMED | ALPHA-1 | start |\n\n"
        "## Shared claims\n\n| Date | Lane | Path | Reason | Owner ack |\n| --- | --- | --- | --- | --- |\n"
        "| 2026-01-01 | L1-one | src/two/b.py | hunk | pending |\n\n"
        "## Owner decisions and facts requested\n\n| Date | Lane | Needed | Register or plan entry | Status |\n| --- | --- | --- | --- | --- |\n"
    )
    files = {
        "Docs/Execution/ROADMAP.md": "# roadmap\n",
        "Docs/Execution/PROGRESS.md": board,
        "Docs/Execution/CHECKPOINTS.md": "# cps\n",
        "Docs/Execution/COORDINATION.md": "# c\n",
        "Docs/Execution/DECISIONS.md": "# d\n",
        "Docs/Execution/CHANGELOG.md": "# cl\n",
        "Docs/Execution/ROSTER.md": "**ALPHA** LC-coordination **BRAVO** L0-integrator **CHARLIE** L1-one **DELTA** L2-two\n",
        "Docs/Execution/TASKS.md": "### EX-001 — one\n### EX-002 — two\n",
        "Docs/Execution/validate_program.py": "pass\n",
        "Docs/Execution/Lanes/LC-coordination.md": "\n",
        "Docs/Execution/Lanes/L0-integrator.md": "\n",
        "Docs/Execution/Lanes/L1-one.md": "\n",
        "Docs/Execution/Lanes/L2-two.md": "\n",
        "Docs/Execution/Handoffs/LC-coordination/ALPHA-1.md": "\n",
        "Docs/Execution/Handoffs/L0-integrator/.gitkeep": "",
        "Docs/Execution/Handoffs/L1-one/CHARLIE-1b.md": "\n",
        "Docs/Execution/Handoffs/L2-two/.gitkeep": "",
        "src/one/a.py": "", "src/two/b.py": "", "app/main.py": "", "ci/run.sh": "",
    }
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    registry = {
        "authority": {k: f"Docs/Execution/{v}" for k, v in {
            "roadmap": "ROADMAP.md", "board": "PROGRESS.md", "checkpoints": "CHECKPOINTS.md", "roster": "ROSTER.md",
            "coordination": "COORDINATION.md", "decisions": "DECISIONS.md", "changelog": "CHANGELOG.md", "validator": "validate_program.py"}.items()},
        "taskSources": [{"path": "Docs/Execution/TASKS.md", "pattern": r"^### ([A-Z]{2}-\d{3}) — "}],
        "buildPolicy": "integrator-only",
        "boardStates": ["CLAIMED", "VERIFIED"],
        "checkpoints": [{"id": "CP0"}, {"id": "CP1"}],
        "agentNaming": {"sessionName": "<AGENT>-<phase>", "handoffPath": "Docs/Execution/Handoffs/<lane-key>/<SESSION-NAME>.md"},
        "sharedFiles": [{"path": "app/main.py", "owner": "L0-integrator", "claimants": ["L1-one"]}],
        "plannedPaths": [],
        "lanes": [
            {"key": "LC-coordination", "role": "coordination", "agentName": "ALPHA", "phases": [1], "brief": "Docs/Execution/Lanes/LC-coordination.md",
             "ownerPaths": ["Docs/Execution/ROADMAP.md", "Docs/Execution/Lanes/**"], "tasks": []},
            {"key": "L0-integrator", "role": "integration", "agentName": "BRAVO", "phases": [1], "brief": "Docs/Execution/Lanes/L0-integrator.md",
             "ownerPaths": ["app/**", "ci/**"], "tasks": []},
            {"key": "L1-one", "role": "delivery", "agentName": "CHARLIE", "phases": [1], "brief": "Docs/Execution/Lanes/L1-one.md",
             "ownerPaths": ["src/one/**"], "tasks": ["EX-001"], "upstreamAgents": ["DELTA"]},
            {"key": "L2-two", "role": "delivery", "agentName": "DELTA", "phases": [1], "brief": "Docs/Execution/Lanes/L2-two.md",
             "ownerPaths": ["src/two/**"], "tasks": ["EX-002"]},
        ],
    }
    return root, registry


def _write(root: Path, registry: dict) -> None:
    (root / DEFAULT_REGISTRY).write_text(json.dumps(registry), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)


def self_test() -> int:
    import copy
    failures: list[str] = []

    def expect(label: str, mutate, needle: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, registry = _fixture(directory)
            mutate(root, registry)
            _write(root, registry)
            errors = run(root)
            if not any(needle in e for e in errors):
                failures.append(f"{label}: expected an error containing {needle!r}, got {errors}")

    with tempfile.TemporaryDirectory() as directory:
        root, registry = _fixture(directory)
        _write(root, registry)
        errors = run(root)
        if errors:
            failures.append(f"clean fixture should pass, got {errors}")

    expect("overlap", lambda r, g: g["lanes"][3]["ownerPaths"].append("src/one/**"), "owned by more than one lane")
    expect("coordinator owns source", lambda r, g: g["lanes"][0]["ownerPaths"].append("src/one/a.py"), "may own only the plan")
    expect("coordinator carries task", lambda r, g: g["lanes"][0].update(tasks=["EX-001"]), "must carry no task")
    expect("two coordinators", lambda r, g: g["lanes"][3].update(role="coordination"), "exactly one lane must have role 'coordination'")
    expect("unknown task", lambda r, g: g["lanes"][2].update(tasks=["EX-999"]), "does not exist in any task source")
    expect("task twice", lambda r, g: g["lanes"][3].update(tasks=["EX-001"]), "carried by more than one lane")
    expect("dead owner glob", lambda r, g: g["lanes"][2]["ownerPaths"].append("src/nothing/**"), "matches no tracked file")
    def board_row(row: str):
        def mutate(r, g):
            path = r / "Docs/Execution/PROGRESS.md"
            path.write_text(path.read_text().replace("| start |\n", "| start |\n" + row + "\n"))
        return mutate

    expect("bad board row", board_row("| 2026-01-01 | L1-one | CP0 | CLAIMED |"), "board row does not parse")
    expect("unknown state", board_row("| 2026-01-01 | L1-one | CP0 | DONE | x | y |"), "unknown state")
    expect("unknown lane", board_row("| 2026-01-01 | L9-ghost | CP0 | CLAIMED | x | y |"), "unknown lane")
    expect("unknown checkpoint", board_row("| 2026-01-01 | L1-one | CP7 | CLAIMED | x | y |"), "unknown checkpoint")
    expect("claim path missing", lambda r, g: (r / "Docs/Execution/PROGRESS.md").write_text((r / "Docs/Execution/PROGRESS.md").read_text().replace("src/two/b.py", "src/gone.py")), "claimed path does not exist")
    expect("handoff misnamed", lambda r, g: (r / "Docs/Execution/Handoffs/L1-one/DELTA-1.md").write_text("\n"), "named for DELTA")
    expect("roster missing agent", lambda r, g: (r / "Docs/Execution/ROSTER.md").write_text("**ALPHA** LC-coordination\n"), "does not name agent")
    expect("bad build policy", lambda r, g: g.update(buildPolicy="whatever"), "buildPolicy must be")
    expect("empty board", lambda r, g: (r / "Docs/Execution/PROGRESS.md").write_text("## Board\n\n| Date | Lane | Checkpoint | State | Ref | Note |\n| --- | --- | --- | --- | --- | --- |\n"), "has no rows")
    expect("bad agent name", lambda r, g: g["lanes"][2].update(agentName="Charlie2"), "single upper-case word")

    if failures:
        print("Self-test FAILED: the validator does not fail closed.", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Self-test OK: 17 mutations caught, clean fixture passes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=None, help="repository root (default: derived from this file's location)")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY, help="registry path relative to root")
    parser.add_argument("--self-test", action="store_true", help="prove the validator catches each failure it claims to")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    errors = run(root, args.registry)
    if errors:
        print("Programme validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    registry = json.loads((root / args.registry).read_text(encoding="utf-8"))
    lanes = registry["lanes"]
    print(f"Programme OK: {len(lanes)} lanes, {sum(len(l.get('tasks', [])) for l in lanes)} carried tasks, {len(registry['checkpoints'])} checkpoints, no owner-path overlap.")
    print("Agents: " + ", ".join(lane["agentName"] for lane in lanes) + ".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
