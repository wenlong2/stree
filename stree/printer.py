import os

from .search import load_index


def _human_size(n):
    size = float(n)
    for unit in ["B", "K", "M", "G", "T"]:
        if size < 1024:
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}P"


def _find_node(root, target):
    target = os.path.abspath(target)
    root_path = root["name"]

    if target.rstrip("/") == root_path.rstrip("/"):
        return root, root_path

    root_norm = root_path.rstrip("/") + "/"
    if not (target + "/").startswith(root_norm):
        return None, None

    rel = os.path.relpath(target, root_path)
    parts = [p for p in rel.split(os.sep) if p not in ("", ".")]

    node, cur = root, root_path
    for part in parts:
        nxt = None
        for c in node.get("children", []):
            if c.get("type") in ("d", "f") and c.get("name") == part:
                nxt = c
                break
        if nxt is None:
            return None, None
        node, cur = nxt, os.path.join(cur, part)
    return node, cur


def _print(node, prefix, counts):
    children = node.get("children", [])
    for i, c in enumerate(children):
        last = i == len(children) - 1
        connector = "└── " if last else "├── "

        if c.get("type") == "note":
            print(prefix + connector + c["text"])
            continue

        label = c["name"]
        if c.get("type") == "f":
            counts[0] += 1
            if "size" in c:
                label += f" [{_human_size(c['size'])}]"
        else:
            counts[1] += 1

        print(prefix + connector + label)
        if c.get("type") == "d":
            ext = "    " if last else "│   "
            _print(c, prefix + ext, counts)


def print_tree(path=None):
    root = load_index()
    target = path or root["name"]
    node, resolved = _find_node(root, target)
    if node is None:
        print(f"'{target}' not found in index.")
        return

    print(resolved)
    counts = [0, 0]
    _print(node, "", counts)
    print(f"\n{counts[1]} directories, {counts[0]} files")
