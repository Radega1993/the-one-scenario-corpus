# Wiki backup information

- **Date (UTC):** 2026-05-20 11:38 UTC
- **Source:** `/home/raul/Documents/the-one/scenarios/.wiki-clone`
- **Destination:** `/home/raul/Documents/the-one/scenarios/wiki_backup_20260520_133832`
- **Method:** `cp -a` (full tree); `.git` removed from backup copy
- **Status:** **COMPLETED OK**

## Counts

| Type | Count |
|------|------:|
| Total files | 223 |
| Markdown (`.md`) | 223 |
| Non-markdown | 0 |

## Size

Approximate source size: ~5.8 MB (wiki content without `.git` objects in active clone).

## Notes

- Original `.wiki-clone` may still contain a `.git` directory for GitHub wiki sync; this backup excludes `.git` intentionally.
- Full page list: see `scenarios/analysis/reports/wiki_old_audit.md`.
- Do not delete this backup before the new wiki is reviewed and accepted.

## Verification

```bash
test -d /home/raul/Documents/the-one/scenarios/wiki_backup_20260520_133832/01-home/Home.md && echo OK
```

Expected: backup contains `01-home/Home.md` and `05-corpus/Corpus-overview.md`.
