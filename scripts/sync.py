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
import urllib.parse
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

# Every human-facing skylit.ai link carries UTMs so visits, signups and
# free-to-paid conversions from each surface are attributable.
# Machine-read files (specs, llms.txt, skill.md) are left untagged.
SITE_LINK = re.compile(r"https://(?:www\.|app\.)?skylit\.ai(?:[/?][^\s)\"'<>`\]]*)?")
UTM_FILES = (".md", ".json", ".toml")
UTM_SKIP_EXT = (".yaml", ".yml", ".json", ".txt", ".md")


def utm_source(rel: Path) -> str:
    parts = rel.parts
    if parts[:2] == ("packages", "python"):
        return "pypi"
    if parts[:2] == ("packages", "typescript"):
        return "npm"
    if rel.name == "server.json":
        return "mcp_registry"
    return "github"


def tag_url(url: str, rel: Path) -> str:
    trail = ""
    while url and url[-1] in ".,;:":
        trail, url = url[-1] + trail, url[:-1]
    parts = urllib.parse.urlsplit(url)
    if not parts.path:
        parts = parts._replace(path="/")
    if parts.path.lower().endswith(UTM_SKIP_EXT):
        return url + trail
    query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query) if not k.startswith("utm_")]
    slug = re.sub(r"[^a-z0-9]+", "-", str(rel.with_suffix("")).lower()).strip("-")
    query += [("utm_source", utm_source(rel)), ("utm_medium", "developer"),
              ("utm_campaign", "api_distribution"), ("utm_content", slug)]
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query))) + trail


def utm_files():
    for f in sorted(ROOT.rglob("*")):
        rel = f.relative_to(ROOT)
        if f.is_file() and f.suffix in UTM_FILES and not set(rel.parts) & {"reference", "node_modules", ".git", "dist"} \
                and f.name != "package-lock.json":
            yield f, rel


def tag_links(write: bool) -> list[str]:
    untagged = []
    for f, rel in utm_files():
        text = f.read_text(encoding="utf-8")
        new = SITE_LINK.sub(lambda m: tag_url(m.group(0), rel), text)
        if new != text:
            untagged.append(f"{rel}: skylit.ai link without the standard UTMs")
            if write:
                f.write_text(new, encoding="utf-8")
    return untagged


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
        m = re.match(r"^\| `([a-z0-9_]+)` \| (.*?) \| (.*?) \| ((?:`?(?:GET|POST) [^`|]+`?(?: \+ )?)+) \| ([^|]+) \|\s*$", line)
        if m:
            name, returns, _args, endpoints, credits = m.groups()
            eps = [e.strip().strip("`") for e in endpoints.split(" + ")]
            tools.append({"name": name, "section": section, "returns": returns.strip(),
                          "endpoint": eps[0] if len(eps) == 1 else eps, "credits": credits.strip()})
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
    return (f"{START}\n{len(tools)} tools, all read-only. Most wrap one Skylit REST endpoint with the same "
            "credit cost; the intelligence tools combine several and are served on their own list "
            "(`/mcp?toolset=intelligence`). Full catalog with arguments and prices: "
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

    utm_missing = tag_links(write=not only_check)
    problems = check(tools, paths) + (utm_missing if only_check else [])
    for p in problems:
        print(f"DRIFT {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
