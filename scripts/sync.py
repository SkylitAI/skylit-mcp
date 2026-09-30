#!/usr/bin/env python3
"""Keep this repo in step with the live Skylit API and MCP server.

Sources are Skylit's public docs, published from the same catalog the API is
built from:
  - the MCP tool catalog   https://www.skylit.ai/docs/mcp/tools.md
  - the REST specs         https://www.skylit.ai/docs/{openapi,flowseeker-openapi,atlas-openapi}.yaml

    python3 scripts/sync.py          # refresh reference/ and the README's generated block
    python3 scripts/sync.py --check  # fail if anything in the repo names a tool or path that no longer exists

Standard library only. On a fetch error nothing is written.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = "https://www.skylit.ai/docs"
SOURCES = {
    "reference/mcp-tools.md": f"{DOCS}/mcp/tools.md",
    "reference/openapi/heatseeker-tempest.yaml": f"{DOCS}/openapi.yaml",
    "reference/openapi/flowseeker.yaml": f"{DOCS}/flowseeker-openapi.yaml",
    "reference/openapi/atlas.yaml": f"{DOCS}/atlas-openapi.yaml",
}
# Where tool names and REST paths are written by hand; --check reads these.
CHECKED = ["README.md", "GEMINI.md", "llms-install.md", "skills", "plugins", "examples", "clients", "packages"]
TOOL_PREFIXES = ("heat_", "tempest_", "flow_", "dark_pool_", "top_", "unusual_", "underlying_",
                 "contract_", "market_", "chain_", "list_active_", "account_", "trade_", "sector_")
START, END = "<!-- sync:tools:start -->", "<!-- sync:tools:end -->"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "skylit-mcp-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status != 200:
            raise RuntimeError(f"{url}: HTTP {r.status}")
        return r.read().decode("utf-8")


def parse_tools(md: str) -> list[dict]:
    tools, section = [], ""
    for line in md.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"^\| `([a-z0-9_]+)` \| (.*?) \| (.*?) \| `?(GET|POST) ([^`|]+?)`? \| ([^|]+) \|\s*$", line)
        if m:
            name, returns, _args, method, path, credits = m.groups()
            tools.append({"name": name, "section": section, "returns": returns.strip(),
                          "endpoint": f"{method} {path.strip()}", "credits": credits.strip()})
    return tools


def spec_paths(yaml_text: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"^  (/v1/[^:\s]*):\s*$", yaml_text, re.M)}


def norm(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path.split("?")[0].rstrip("/"))


def path_known(path: str, known: set[str]) -> bool:
    """A literal path (/v1/flow/SPY) or template (/v1/vol/{}) matches a spec path
    segment by segment, `{}` on either side matching any one segment. A prefix of
    a spec path also counts (docs mention route families like /v1/vol)."""
    segs = path.split("/")
    for k in known:
        ks = k.split("/")
        if len(ks) < len(segs):
            continue
        if all(a == b or a == "{}" or b == "{}" for a, b in zip(segs, ks)):
            return True
    return False


def readme_block(tools: list[dict]) -> str:
    groups: dict[str, list[str]] = {}
    for t in tools:
        groups.setdefault(t["section"], []).append(f"`{t['name']}`")
    rows = "\n".join(f"| {s} | {', '.join(names)} |" for s, names in groups.items())
    return (f"{START}\n{len(tools)} tools, all read-only. Each wraps one Skylit REST endpoint with the same "
            "credit cost. Full catalog with arguments and prices: "
            "[www.skylit.ai/docs/mcp/tools](https://www.skylit.ai/docs/mcp/tools); machine-readable copy: "
            f"[reference/tools.json](reference/tools.json).\n\n| Group | Tools |\n| --- | --- |\n{rows}\n{END}")


def checked_files():
    for entry in CHECKED:
        p = ROOT / entry
        files = [p] if p.is_file() else sorted(p.rglob("*")) if p.is_dir() else []
        for f in files:
            if f.is_file() and f.suffix in {".md", ".py", ".ts", ".json", ".toml"} and "node_modules" not in f.parts \
                    and "dist" not in f.parts and "reference" not in f.parts:
                yield f


def check(tools: list[dict], paths: set[str]) -> list[str]:
    names = {t["name"] for t in tools}
    known = {norm(p) for p in paths}
    problems = []
    for f in checked_files():
        text = f.read_text(encoding="utf-8", errors="replace")
        rel = f.relative_to(ROOT)
        for n in set(re.findall(r"[`'\"]([a-z][a-z0-9]*(?:_[a-z0-9]+)+)[`'\"]", text)):
            if n.startswith(TOOL_PREFIXES) and n not in names and not n.endswith(("_key", "_url", "_id")):
                problems.append(f"{rel}: tool `{n}` is not in the live catalog")
        for p in set(re.findall(r"(/v1/[A-Za-z0-9_\-/{}.]+)", text)):
            p = p.rstrip(".")
            if p.endswith(".json") or p == "/v1" or "{" in p and p.count("{") != p.count("}"):
                continue
            if not path_known(norm(p), known):
                problems.append(f"{rel}: REST path {p} is not in the public specs")
    return sorted(set(problems))


def main() -> int:
    only_check = "--check" in sys.argv
    try:
        fetched = {dest: fetch(url) for dest, url in SOURCES.items()}
    except Exception as e:  # never write a half-refreshed tree
        print(f"fetch failed, nothing written: {e}", file=sys.stderr)
        return 2
    tools = parse_tools(fetched["reference/mcp-tools.md"])
    if len(tools) < 10:
        print(f"parsed only {len(tools)} tools; the catalog format changed, nothing written", file=sys.stderr)
        return 2
    paths = set().union(*(spec_paths(v) for k, v in fetched.items() if k.endswith(".yaml")))

    if not only_check:
        for dest, body in fetched.items():
            (ROOT / dest).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / dest).write_text(body, encoding="utf-8")
        (ROOT / "reference/tools.json").write_text(json.dumps(
            {"server": "https://mcp.skylit.ai/mcp", "count": len(tools), "tools": tools}, indent=2) + "\n", encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        if START in readme and END in readme:
            readme = readme[:readme.index(START)] + readme_block(tools) + readme[readme.index(END) + len(END):]
            (ROOT / "README.md").write_text(readme, encoding="utf-8")
        print(f"synced: {len(tools)} tools, {len(paths)} REST paths")

    problems = check(tools, paths)
    for p in problems:
        print(f"DRIFT {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
