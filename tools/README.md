# Documentation tooling

| Script | Purpose |
|--------|---------|
| `readme_maximize.py` | Inserts chapter blocks from `readme_blocks/{ru,en,pl}/` into root `README*.md` (incl. **N3** risk-based inventory) |
| `_write_deep_blocks.py` | Regenerates `l1_deep_blocks/` and `module_deep_blocks/` source files |
| `_write_full_pl.py` | Rewrites complete Polish L1 + module block sources (UTF-8) |
| `_write_full_en.py` | Rewrites complete English module block sources (UTF-8) |
| `expand_l1_and_modules.py` | Applies L1 mini-chapters (9×3) and module README expansions |

**Refresh after editing blocks:**

```bash
python tools/_write_deep_blocks.py    # optional: regenerate block sources
python tools/readme_maximize.py       # root README chapter intros
python tools/expand_l1_and_modules.py # L1 deep + api/reporting/mocks_lab
```

Markers (`<!-- readme-chapter:… -->`, `<!-- l1-deep:N -->`, `<!-- mod-deep:… -->`) make re-runs safe.
