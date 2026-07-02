import gzip
import json
import os
import re
import shutil
import sys
import time
from collections import defaultdict

from .config import INDEX_PATH, STREE_DIR, load_config

# virtual / pseudo filesystems that are pointless (and often huge/looping) to index
SKIP_DIRS = {"/proc", "/sys", "/dev", "/run"}

_DIGIT_RE = re.compile(r"\d+")


def _pattern_of(name):
    """Collapse digit runs so lc001.dat and lc002.dat map to the same pattern."""
    return _DIGIT_RE.sub("#", name)


def _group_similar(files, threshold, keep):
    """Group files by name pattern; collapse large groups to `keep` entries + a note."""
    groups = defaultdict(list)
    for name in files:
        groups[_pattern_of(name)].append(name)

    kept_files = []
    notes = []
    for pattern, names in groups.items():
        names.sort()
        if len(names) > threshold:
            kept_files.extend(names[:keep])
            notes.append(f"{len(names) - keep}+ more similar files like '{pattern}'")
        else:
            kept_files.extend(names)
    return kept_files, notes


def _make_file_node(dirpath, name, large_bytes):
    node = {"name": name, "type": "f"}
    try:
        size = os.path.getsize(os.path.join(dirpath, name))
        if size > large_bytes:
            node["size"] = size
    except OSError:
        pass
    return node


def _report(path, stats):
    width = shutil.get_terminal_size((100, 20)).columns - 1
    line = f"[{stats['dirs']} dirs, {stats['files']} files] {path}"
    sys.stdout.write("\r" + line[:width].ljust(width))
    sys.stdout.flush()


def _build_node(path, cfg, large_bytes, verbose, stats):
    if verbose:
        stats["dirs"] += 1
        _report(path, stats)

    try:
        entries = list(os.scandir(path))
    except (PermissionError, FileNotFoundError, NotADirectoryError, OSError):
        return {"children": []}

    dirs, files = [], []
    for e in entries:
        try:
            if e.is_symlink():
                continue
            if e.is_dir(follow_symlinks=False):
                dirs.append(e.name)
            elif e.is_file(follow_symlinks=False):
                files.append(e.name)
        except OSError:
            continue

    if verbose:
        stats["files"] += len(files)

    children = []
    kept_files, notes = _group_similar(
        files, cfg["similar_group_threshold"], cfg["similar_group_keep"]
    )
    for name in sorted(kept_files):
        children.append(_make_file_node(path, name, large_bytes))
    for note in notes:
        children.append({"type": "note", "text": note})

    for d in sorted(dirs):
        dpath = os.path.join(path, d)
        if dpath in SKIP_DIRS:
            continue
        child = _build_node(dpath, cfg, large_bytes, verbose, stats)
        child["name"] = d
        child["type"] = "d"
        children.append(child)

    return {"children": children}


def build_index(root="/", quiet=False, verbose=False):
    cfg = load_config()
    large_bytes = cfg["large_file_mb"] * 1024 * 1024
    sys.setrecursionlimit(10000)

    root = os.path.abspath(root)
    if not quiet:
        print(f"Indexing {root} ...")
    t0 = time.time()

    stats = {"dirs": 0, "files": 0}
    tree = _build_node(root, cfg, large_bytes, verbose, stats)
    tree["name"] = root
    tree["type"] = "d"

    if verbose:
        sys.stdout.write("\n")

    os.makedirs(STREE_DIR, exist_ok=True)
    with gzip.open(INDEX_PATH, "wt", encoding="utf-8") as f:
        json.dump(tree, f)

    if not quiet:
        print(f"Done in {time.time() - t0:.1f}s. Index saved to {INDEX_PATH}")
    return tree
