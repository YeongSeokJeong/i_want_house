# Wiki Writing Checklist

Run this before finalizing any `docs/wiki/` edit.

## Routing
- [ ] I chose the file path based on document class, not convenience.
- [ ] Domain knowledge went under `domains/`.
- [ ] Human decisions went under `decisions/` and were surfaced in `decisions.md`.
- [ ] Shared principles went under `rules/common/`.
- [ ] Repeatable procedures/checklists went under `rules/workflow/`.

## Schema compliance
- [ ] I checked `docs/wiki/SCHEMA.md` before writing.
- [ ] If `SCHEMA.md` conflicts with this skill's resource files, I followed `SCHEMA.md`.
- [ ] File and directory names use lowercase kebab-case.
- [ ] I did not create `raw/`, `queries/`, `progress/`, or `sessions/`.
- [ ] New domain directories include `overview.md`.
- [ ] Agent decisions, if any, stay inside a relevant page as `Agent note`.

## Content quality
- [ ] The document has a clear purpose.
- [ ] The structure is concise and scannable.
- [ ] Related docs are linked.
- [ ] The writing is specific, not generic filler.
- [ ] The content language matches the local wiki style unless there is a reason not to.

## Navigation sync
- [ ] I updated `index.md` if discoverability changed.
- [ ] I updated `decisions.md` if a human decision was added or changed.
- [ ] I updated `init.md` and `SCHEMA.md` if the structure or rules changed.
- [ ] I updated the relevant `overview.md` when adding or reorganizing subtopic pages.
- [ ] I updated `Last updated` fields on navigation/index pages that changed (format: `YYYY-MM-DD`).

## Final sanity check
- [ ] A future reader can find this document from an obvious entry point.
- [ ] Newly referenced wikilinks point to real or intentionally planned docs.
- [ ] The page belongs in this wiki and not in a transient progress log.
- [ ] The artifact is the smallest sufficient document for the request.
