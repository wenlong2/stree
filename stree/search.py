import fnmatch
import gzip
import json
import os

from .config import INDEX_PATH


def load_index():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            f"No index found at {INDEX_PATH}. Run 'mktree' first."
        )
    with gzip.open(INDEX_PATH, "rt", encoding="utf-8") as f:
        return json.load(f)


def _normalize_pattern(pattern):
    # allow loose regex-style anchors ^...$ on top of glob patterns, since
    # fnmatch already matches the whole name anyway
    p = pattern
    if p.startswith("^"):
        p = p[1:]
    if p.endswith("$"):
        p = p[:-1]
    return p


def _walk(node, path):
    yield path, node
    for child in node.get("children", []):
        if child.get("type") == "note":
            continue
        yield from _walk(child, os.path.join(path, child["name"]))


def find(pattern, kind, tree=None):
    """kind is 'f' for files or 'd' for directories."""
    tree = tree if tree is not None else load_index()
    pat = _normalize_pattern(pattern)
    results = []
    for path, node in _walk(tree, tree["name"]):
        if path == tree["name"]:
            continue
        if node.get("type") != kind:
            continue
        if fnmatch.fnmatchcase(os.path.basename(path), pat):
            results.append(path)
    return results
