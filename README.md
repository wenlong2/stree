# 🌲 stree — smart tree

**Index your entire disk in minutes, then search or browse it instantly — forever.**

`stree` walks the filesystem once, records just the *names* (no file
contents), and saves a compact index. From then on, finding a file or
browsing a directory tree is instant — no more waiting on `find` or
`du` to crawl millions of files every single time.

```
$ mktree -v
[482,193 dirs, 3,910,204 files] /Users/me/Library/Caches/...
Done in 94.3s. Index saved to ~/.stree/stree

$ sfind '*invoice*2024*.pdf'
/Users/me/Documents/Finance/invoice_march_2024.pdf
/Users/me/Downloads/invoice-2024-11.pdf

$ ptree ~/projects/stree
/Users/me/projects/stree
├── stree
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── indexer.py
│   ├── printer.py
│   └── search.py
├── LICENSE
├── README.md
└── pyproject.toml

3 directories, 8 files
```

## Why

Running `find / -name "*.dat"` on a disk with millions of files takes
forever, every time. `stree` pays that cost once, then every search
after that is just a lookup against a small local index.

## Features

- ⚡ **Fast repeat searches** — index once, search instantly afterward
- 🗂️ **Smart deduplication** — directories with hundreds of similarly
  named files (`lc001.dat` ... `lc199.dat`) get collapsed to a handful
  of samples plus a note, so the index stays small
- 📦 **Size-aware** — large files are flagged with their size right in
  the index
- 🙈 **Dotfile-aware** — ignores noisy folders like `.git`/`.cache` by
  default, but still tracks dotfiles like `.gitignore`
- 🔎 **Glob search** for files (`sfind`) and directories (`dfind`),
  with optional case-insensitive matching
- 🌳 **`tree`-style browsing** of the saved index via `ptree`
- ⚙️ **Fully configurable** thresholds, all stored in one JSON file

## Install

```bash
pip install git+https://github.com/wenlong2/stree.git
```

Or clone and install locally:

```bash
git clone https://github.com/wenlong2/stree.git
cd stree
pip install -e .
```

## Commands

### `mktree` — build the index

```bash
mktree             # index the whole disk (from /) into ~/.stree/stree
mktree /home/me     # index only a subtree
mktree -v           # show live progress (current dir, dirs/files scanned)
mktree -q           # suppress the banner/summary lines
```

### `sfind` — find files by name

```bash
sfind '*abc?[1-3].dat'
sfind -i '*ABC?[1-3].DAT'   # case-insensitive
```

Prints the full path of every matching file. Patterns are shell-glob
style (`*`, `?`, `[...]`); a leading `^` or trailing `$` is tolerated
and ignored, since matching is already against the whole filename.
Matching is case-sensitive by default; pass `-i`/`--ignore-case` for
case-insensitive matching.

### `dfind` — find directories by name

Same as `sfind`, but matches directory names instead of file names.

```bash
dfind 'build*'
dfind -i 'BUILD*'   # case-insensitive
```

### `ptree` — browse the index like `tree`

```bash
ptree              # print from the indexed root
ptree /home/me/src  # print a subtree
```

Reads only the saved index, so it's fast even on huge disks, though it
won't show files skipped during indexing.

### `streeconfig` — view/edit settings

```bash
streeconfig
streeconfig --set similar_group_threshold 100
streeconfig --set ignore_dot_dirs false
streeconfig --set ignore_dot_files true
```

Config lives at `~/.stree/config.json`:

| key                       | meaning                                                           | default |
|---------------------------|--------------------------------------------------------------------|---------|
| `similar_group_threshold` | group size (N) above which similar filenames get collapsed         | 50      |
| `similar_group_keep`      | how many files (N2) to keep per collapsed group                    | 5       |
| `large_file_mb`           | file size in MB (N3) above which the size is recorded              | 5       |
| `ignore_dot_dirs`         | skip recursing into folders whose name starts with `.`             | true    |
| `ignore_dot_files`        | skip indexing files whose name starts with `.`                     | false   |

Boolean keys accept `true`/`false` (also `1`/`0`, `yes`/`no`, `on`/`off`).

## Files

- `~/.stree/config.json` — settings above
- `~/.stree/stree` — the gzip-compressed JSON index

## License

MIT
