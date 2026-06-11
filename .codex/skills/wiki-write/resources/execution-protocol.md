# Wiki Writing Execution Protocol

Follow this sequence whenever you create or update `docs/wiki/` content.

## 1. Inspect the local wiki context first

### If `docs/wiki/` does not exist yet (fresh start)
Before anything else, create the four foundation files in this order:
1. `docs/wiki/SCHEMA.md` — routing and naming rules
2. `docs/wiki/init.md` — structure guide
3. `docs/wiki/index.md` — document catalog
4. `docs/wiki/decisions.md` — decision list

Use the templates in `resources/document-templates.md` (sections 6–9) as the starting shape. Then proceed with the user's original request.

### If `docs/wiki/` already exists
Read the relevant current files before writing:
- always: `docs/wiki/SCHEMA.md`
- usually: `docs/wiki/init.md`, `docs/wiki/index.md`
- if working on decisions: `docs/wiki/decisions.md`
- if updating a domain: the target `overview.md` and nearby subtopic pages

Do not rely on memory alone if the file exists.

If `docs/wiki/SCHEMA.md` conflicts with this skill's resource files, follow `SCHEMA.md`. If the task includes maintaining this skill, update the stale resource file in the same change.

## 2. Classify the request before choosing a file
Route the content by intent:
- domain/topic knowledge -> `domains/<domain>/...`
- durable human decision -> `decisions/<name>.md` + update `decisions.md`
- common rule/principle -> `rules/common/<name>.md`
- repeatable procedure/checklist -> `rules/workflow/<name>.md`
- structure/navigation change -> `init.md`, `index.md`, `SCHEMA.md`

If the request mixes multiple classes, split the result across multiple files instead of overloading one page.

If the ambiguity changes which file or folder will be edited, ask a short multiple-choice clarification before writing. Use at most 4 choices: domain knowledge, common rule, workflow/checklist, or human decision. Do not ask if the route is obvious from the user's wording.

## 3. Reuse the existing schema, do not redesign it implicitly
Assume the current wiki structure is intentional unless the user explicitly asks to change it.

Specifically:
- keep everything under `docs/wiki/`
- use kebab-case file names
- prefer business-domain folders under `domains/`
- keep human decisions first-class and visible
- keep agent decisions inside relevant pages, not in separate docs
- do not introduce `raw/`, `queries/`, `progress/`, or `sessions/`

## 4. Write the smallest correct artifact
Pick the lightest sufficient document shape.

Examples:
- One focused concept -> one subtopic page
- New big topic -> create `domains/<domain>/overview.md` and optionally one or two subtopic pages
- One major human decision -> one decision file, not a giant omnibus page
- One rule/checklist -> one rule or workflow document

## 5. Use concise, scannable structure
Default page pattern:
1. 목적
2. 핵심 내용
3. 관련 문서
4. `Agent note` if genuinely useful

Prefer:
- short sections
- bullets over long prose when possible
- explicit links to related pages
- concrete names over abstract placeholders

## 6. Keep navigation pages in sync
When you add or materially move content, update discovery pages in the same task.

Required sync rules:
- new domain or subtopic -> update `index.md`, and often the domain `overview.md`
- new human decision -> update `decisions.md`, and usually `index.md`
- structural rule change -> update `SCHEMA.md` and likely `init.md`
- top-level structure change -> update `init.md`, `index.md`, and `SCHEMA.md` together
- when editing navigation/index pages with `Last updated`, update the date in the same edit

## 7. Decision handling rule
### Human decisions
Create a dedicated file under `docs/wiki/decisions/` when the decision:
- affects project direction, policy, structure, or operation
- is worth revisiting later
- needs explicit rationale and alternatives

### Agent decisions
Do not create a separate decision document.
If useful, add an `Agent note` section in the closest relevant page.

## 8. Language and tone
Unless the surrounding section suggests otherwise:
- write wiki content in concise Korean
- keep headers literal and practical
- avoid marketing language and vague summary filler

## 9. Verify before finalizing
Check:
- correct folder and file path
- naming matches schema
- links point to real or intentionally planned docs
- every newly created page is reachable from `index.md`, `decisions.md`, or a domain `overview.md`
- `Last updated` fields changed when navigation/index pages changed
- no forbidden extra folders were introduced
- the page is easy to scan without hidden assumptions
