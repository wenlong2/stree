import json
import os

STREE_DIR = os.path.expanduser("~/.stree")
CONFIG_PATH = os.path.join(STREE_DIR, "config.json")
INDEX_PATH = os.path.join(STREE_DIR, "stree")

# N: group size above which similar filenames get collapsed
# N2: how many files to keep from each collapsed group
# N3: file size (MB) above which size is recorded in the index
DEFAULT_CONFIG = {
    "similar_group_threshold": 50,  # N
    "similar_group_keep": 5,        # N2
    "large_file_mb": 5,             # N3
    "ignore_dot_dirs": True,        # skip recursing into folders starting with "."
    "ignore_dot_files": False,      # keep (do not skip) files starting with "."
}

# keys that hold booleans rather than ints, so the CLI knows how to parse --set
BOOL_KEYS = {"ignore_dot_dirs", "ignore_dot_files"}


def load_config():
    os.makedirs(STREE_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    return merged


def save_config(cfg):
    os.makedirs(STREE_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
