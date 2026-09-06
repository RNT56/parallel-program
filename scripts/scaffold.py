#!/usr/bin/env python3
"""Render a parallel-program's documents into a repository from Docs/Execution/lanes.json.

    python3 scaffold.py --root <repo> --init                 # write a starter registry and task ledger
    python3 scaffold.py --root <repo>                        # render every missing document from the registry
    python3 scaffold.py --root <repo> --apply-instructions   # also append the programme block to AGENTS.md and CLAUDE.md

Never overwrites an existing file: a rendered document that already exists is skipped and listed,
so a live board or an edited brief is never clobbered. Re-run after editing the registry to render
briefs for new lanes. The validator is copied beside the registry.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL / "assets/templates"
DEFAULT_REGISTRY = "Docs/Execution/lanes.json"

BUILD_POLICY_TEXT = {
    "integrator-only": "Do not build, test, boot a simulator or touch a shared environment. Run only static validators and `git diff --check`.",
    "lanes-focused": "You may run focused unit tests inside your own worktree. Integration, UI, device and release suites are the integrator's; only its stage run counts as VERIFIED.",
}


def render(template: str, values: dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def bullets(items: list[str], empty: str = "none") -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {empty}"


def write(root: Path, rel: str, content: str, written: list[str], skipped: list[str]) -> None:
    path = root / rel
    if path.exists():
        skipped.append(rel)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    written.append(rel)


def init(root: Path, registry_rel: str, program: str) -> int:
    written: list[str] = []
    skipped: list[str] = []
    date = dt.date.today().isoformat()
    write(root, registry_rel, render((TEMPLATES / "lanes.json").read_text(), {"PROGRAM": program, "DATE": date}), written, skipped)
    write(root, str(Path(registry_rel).parent / "TASKS.md"), render((TEMPLATES / "TASKS.md").read_text(), {"PROGRAM": program}), written, skipped)
    print("written: " + ", ".join(written) if written else "nothing written")
    if skipped:
        print("already present, left alone: " + ", ".join(skipped))
    print("Edit the registry (lanes, owner paths, agents, checkpoints, machine, stages), then run scaffold.py without --init.")
    return 0


def scaffold(root: Path, registry_rel: str, apply_instructions: bool) -> int:
    registry_path = root / registry_rel
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"cannot read {registry_rel}: {exc}", file=sys.stderr)
        return 1
    program_dir = Path(registry_rel).parent
    lanes = registry.get("lanes", [])
    by_role = {lane.get("role", "delivery"): lane for lane in lanes}
    coordinator = by_role.get("coordination")
    integrator = by_role.get("integration")
    if not coordinator or not integrator:
        print("registry needs exactly one lane with role coordination and one with role integration", file=sys.stderr)
        return 1
    delivery = [lane for lane in lanes if lane.get("role", "delivery") == "delivery"]
    first_agent = (delivery[0] if delivery else coordinator)["agentName"]
    machine = registry.get("machine", {})
    date = registry.get("defined") or dt.date.today().isoformat()
    policy = registry.get("buildPolicy", "integrator-only")
    checkpoints = registry.get("checkpoints", [])
    stages = registry.get("stages", {})
    names = {lane["key"]: lane["agentName"] for lane in lanes}

    common = {
        "PROGRAM": registry.get("program", "programme"),
        "DATE": date,
        "GOAL": registry.get("goal", "(state the goal)"),
        "COORDINATOR": coordinator["agentName"],
        "COORDINATOR_LANE": coordinator["key"],
        "INTEGRATOR": integrator["agentName"],
        "INTEGRATOR_LANE": integrator["key"],
        "FIRST_AGENT": first_agent,
        "BUILD_POLICY": policy,
        "BUILD_POLICY_TEXT": BUILD_POLICY_TEXT.get(policy, ""),
        "WORKTREE_ROOT": machine.get("worktreeRoot", "<worktree root>"),
        "BUILD_ROOT": machine.get("buildRoot", "<build root>"),
        "MACHINE_NOTES": machine.get("notes", "none recorded."),
        "HAZARDS": " ".join(registry.get("hazards", [])) or "(list the repository's known traps here: isolation defaults, generated files, flaky suites, tools that go blind in worktrees).",
        "STAGES_TABLE": table(["Stage", "Command", "Needs"], [[name, f"`{cmd}`", ""] for name, cmd in stages.items()]),
        "MATRIX_TABLE": table(["Checkpoint"] + list(stages), [[cp["id"]] + ["yes" if s in cp.get("verification", []) else "no" for s in stages] for cp in checkpoints]),
        "ROSTER_TABLE": table(["Agent", "Lane", "Role", "Owns", "Phases"], [[f"**{l['agentName']}**", l["key"], l.get("role", "delivery"), l.get("name", ""), ", ".join(str(p) for p in l.get("phases", []))] for l in lanes]),
        "UPSTREAM_TABLE": table(["Agent", "Also reads", "For"], [[l["agentName"], ", ".join(l.get("upstreamAgents", [])), l.get("upstreamReason", "")] for l in lanes if l.get("upstreamAgents")] or [["(none declared)", "", ""]]),
        "START_MESSAGES": "\n".join(f"- `{l['agentName']}-<phase>`: \"You are {l['agentName']}-<phase>. Execute lane `{l['key']}` per `{l['brief']}`. Read `{program_dir}/Lanes/_COMMON.md` first.\"" for l in lanes),
        "LANE_TABLE": table(["Lane", "Agent", "Carries", "First deliverable", "Status"], [[f"[{l['key']}]({Path(l['brief']).relative_to(program_dir)})", l["agentName"], ", ".join(l.get("tasks", [])) or l.get("name", ""), next(iter(l.get("checkpointDeliverables", {}).values()), ""), l.get("status", "ACTIVE")] for l in lanes]),
        "CHECKPOINT_TABLE": table(["Checkpoint", "Verification stages", "Exit"], [[f"**{cp['id']} {cp.get('name', '')}**", ", ".join(cp.get("verification", [])), cp.get("exit", "")] for cp in checkpoints]),
        "DEPENDENCY_TABLE": table(["Needed by", "From", "What", "Why"], [[d.get("neededBy", ""), d.get("from", ""), d.get("what", ""), d.get("why", "")] for d in registry.get("dependencies", [])] or [["(none declared yet)", "", "", ""]]),
        "BOARD_ROWS": "\n".join(f"| {date} | {l['key']} | {checkpoints[0]['id'] if checkpoints else 'CP0'} | {'DEFERRED' if l.get('status') == 'DEFERRED' else 'CLAIMED'} | {l['brief']} | {'Owner decision: deferred; validators keep running' if l.get('status') == 'DEFERRED' else ('Standby until a later phase' if l.get('status') == 'STANDBY' else 'Unassigned until a session takes the brief')} |" for l in lanes),
    }

    written: list[str] = []
    skipped: list[str] = []
    P = str(program_dir)
    for name in ("ROADMAP.md", "PROGRESS.md", "ROSTER.md", "COORDINATION.md", "DECISIONS.md", "CHECKPOINTS.md", "CHANGELOG.md"):
        write(root, f"{P}/{name}", render((TEMPLATES / name).read_text(), common), written, skipped)
    write(root, f"{P}/Lanes/_COMMON.md", render((TEMPLATES / "Lanes/_COMMON.md").read_text(), common), written, skipped)
    write(root, f"{P}/Handoffs/README.md", render((TEMPLATES / "Handoffs/README.md").read_text(), common), written, skipped)
    write(root, f"{P}/Handoffs/TEMPLATE.md", (TEMPLATES / "Handoffs/TEMPLATE.md").read_text(), written, skipped)
    write(root, f"{P}/Manifests/README.md", render((TEMPLATES / "Manifests_README.md").read_text(), common), written, skipped)

    for lane in lanes:
        role = lane.get("role", "delivery")
        template = {"coordination": "COORDINATOR.md", "integration": "INTEGRATOR.md"}.get(role, "LANE.md")
        values = dict(common)
        values.update({
            "LANE_KEY": lane["key"],
            "LANE_NAME": lane.get("name", ""),
            "LANE_STATUS": lane.get("status", "ACTIVE"),
            "AGENT": lane["agentName"],
            "BRANCH": lane.get("branch", f"lane/{lane['key'].split('-', 1)[-1]}"),
            "PHASES": ", ".join(str(p) for p in lane.get("phases", [])) or "none",
            "OWNER_PATHS": bullets([f"`{p}`" for p in lane.get("ownerPaths", [])]),
            "EXCLUDED_PATHS": ", ".join(f"`{p}`" for p in lane.get("excludedPaths", [])) or "nothing carved out; everything not listed above belongs to another lane",
            "TASKS": ", ".join(f"`{t}`" for t in lane.get("tasks", [])) or "none",
            "SUBTEAMS": table(["Sub-team", "Files", "Tasks"], [[t.get("name", ""), f"`{t.get('files', '')}`", ", ".join(t.get("tasks", []))] for t in lane.get("subTeams", [])]) if lane.get("subTeams") else "(split by file when you claim; record the split on the board)",
            "DELIVERABLES": bullets([f"**{cp}:** {text}" for cp, text in lane.get("checkpointDeliverables", {}).items()], "to be written"),
            "UPSTREAM": bullets([f"**{a}** ({next((k for k, n in names.items() if n == a), '?')})" for a in lane.get("upstreamAgents", [])], "no upstream agents; read the coordinator's and integrator's newest handoffs"),
            "MUTEXES": bullets(lane.get("mutexes", []), "none beyond _COMMON.md"),
        })
        write(root, lane["brief"], render((TEMPLATES / "Lanes" / template).read_text(), values), written, skipped)
        keep = root / P / "Handoffs" / lane["key"] / ".gitkeep"
        if not keep.parent.exists():
            keep.parent.mkdir(parents=True)
            keep.write_text("")
            written.append(str(keep.relative_to(root)))

    validator_rel = registry.get("authority", {}).get("validator", f"{P}/validate_program.py")
    if not (root / validator_rel).exists():
        (root / validator_rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SKILL / "scripts/validate_program.py", root / validator_rel)
        written.append(validator_rel)
    else:
        skipped.append(validator_rel)

    block = render((TEMPLATES / "AGENT_INSTRUCTIONS_BLOCK.md").read_text(), common)
    if apply_instructions:
        for name in ("AGENTS.md", "CLAUDE.md"):
            path = root / name
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            if "<!-- parallel-program:begin -->" in existing:
                skipped.append(f"{name} (block present)")
                continue
            path.write_text((existing.rstrip("\n") + "\n\n" if existing else "") + block, encoding="utf-8")
            written.append(f"{name} (block appended)")

    print("written:\n" + "\n".join(f"  {w}" for w in written) if written else "nothing written")
    if skipped:
        print("already present, left alone:\n" + "\n".join(f"  {s}" for s in skipped))
    if not apply_instructions:
        print("\nAppend this block to AGENTS.md and CLAUDE.md (or re-run with --apply-instructions):\n")
        print(block)
    print(f"\nNext: edit every brief under {P}/Lanes/, fill ROADMAP.md sections 1, 3 and 5, then run:\n  python3 {validator_rel}\n  python3 {validator_rel} --self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--init", action="store_true", help="write a starter registry and task ledger, then stop")
    parser.add_argument("--program", default=None, help="programme name for --init (default: <repo-dir>-parallel-<date>)")
    parser.add_argument("--apply-instructions", action="store_true", help="append the programme block to AGENTS.md and CLAUDE.md")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.init:
        return init(root, args.registry, args.program or f"{root.name}-parallel-{dt.date.today().isoformat()}")
    return scaffold(root, args.registry, args.apply_instructions)


if __name__ == "__main__":
    raise SystemExit(main())
