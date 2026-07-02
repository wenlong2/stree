# stree (smart tree)

Fast filename indexing and search for large disks. `stree` walks the
filesystem once, saves a compact index of *names only* (no file
contents), then lets you search or browse that index instantly instead
of re-walking the disk every time.

To keep the index small and fast, directories with a lot of
similarly-named files (e.g. `lc001.dat`, `lc002.dat`, ... `lc199.dat`)
are collapsed: only a handful of representative files are kept, plus a
note like `144+ more similar files like 'lc###.dat'`.

## Install

```bash
pip install .
# or, for development:
pip install -e .
```

## Commands

### `mktree` — build the index

```bash
mktree            # index the whole disk (from /) into ~/.stree/stree
mktree /home/me    # index only a subtree
```

### `sfind` — find files by name

```bash
sfind '*abc?[1-3].dat'
```

Prints the full path of every matching file. Patterns are shell-glob
style (`*`, `?`, `[...]`); a leading `^` or trailing `$` is tolerated
and ignored, since matching is already against the whole filename.

### `dfind` — find directories by name

Same as `sfind`, but matches directory names instead of file names.

```bash
dfind 'build*'
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
```

Config lives at `~/.stree/config.json`:

| key                       | meaning                                                        | default |
|---------------------------|------------------------------------------------------------------|---------|
| `similar_group_threshold` | group size (N) above which similar filenames get collapsed       | 50      |
| `similar_group_keep`      | how many files (N2) to keep per collapsed group                  | 5       |
| `large_file_mb`           | file size in MB (N3) above which the size is recorded            | 5       |

## Files

- `~/.stree/config.json` — settings above
- `~/.stree/stree` — the gzip-compressed JSON index

## License

MIT
