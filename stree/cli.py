import argparse
import sys

from .config import load_config, save_config
from .indexer import build_index
from .printer import print_tree
from .search import find


def mktree_main():
    ap = argparse.ArgumentParser(
        prog="mktree", description="Index filenames on disk into ~/.stree/stree"
    )
    ap.add_argument("root", nargs="?", default="/", help="root path to index (default: /)")
    ap.add_argument("-q", "--quiet", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true", help="show current directory being scanned")
    args = ap.parse_args()
    build_index(args.root, quiet=args.quiet, verbose=args.verbose)


def sfind_main():
    ap = argparse.ArgumentParser(
        prog="sfind", description="Find files by name pattern in the stree index"
    )
    ap.add_argument("pattern", help="glob-like pattern, e.g. '*abc?[1-3].dat'")
    args = ap.parse_args()
    try:
        for p in find(args.pattern, "f"):
            print(p)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def dfind_main():
    ap = argparse.ArgumentParser(
        prog="dfind", description="Find directories by name pattern in the stree index"
    )
    ap.add_argument("pattern", help="glob-like pattern, e.g. 'build*'")
    args = ap.parse_args()
    try:
        for p in find(args.pattern, "d"):
            print(p)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def ptree_main():
    ap = argparse.ArgumentParser(
        prog="ptree", description="Print a tree view from the stree index (like `tree`)"
    )
    ap.add_argument(
        "path", nargs="?", default=None, help="path to root the view at (default: index root)"
    )
    args = ap.parse_args()
    try:
        print_tree(args.path)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def config_main():
    ap = argparse.ArgumentParser(
        prog="streeconfig", description="View or edit stree configuration (~/.stree/config.json)"
    )
    ap.add_argument(
        "--set",
        nargs=2,
        metavar=("KEY", "VALUE"),
        action="append",
        default=[],
        help="set a config key, e.g. --set similar_group_threshold 100",
    )
    args = ap.parse_args()
    cfg = load_config()

    for k, v in args.set:
        if k not in cfg:
            print(f"Unknown key: {k}. Valid keys: {list(cfg.keys())}", file=sys.stderr)
            sys.exit(1)
        cfg[k] = int(v)
    if args.set:
        save_config(cfg)

    for k, v in cfg.items():
        print(f"{k} = {v}")
