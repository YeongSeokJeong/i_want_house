# Wiki Error Playbook

## Problem: Routing ambiguity affects document structure

If the ambiguity changes which file or folder will be edited, ask a short multiple-choice clarification before writing.

Use at most 4 choices:
1. 도메인 지식 문서로 저장
2. 공통 규칙으로 저장
3. 반복 절차/체크리스트로 저장
4. 사람 의사결정으로 저장

Do not ask if the route is obvious from the user's wording.

## Problem: The request does not fit one folder cleanly

Approach:
1. Decide the primary artifact first.
2. Put durable supporting content in secondary pages.
3. Link the pages together.

Example:
- policy explanation -> `rules/common/...`
- domain-specific application details -> `domains/<domain>/...`

## Problem: The user asks for a new top-level folder implicitly

Default response inside the skill:
- do not invent the folder automatically
- fit the request into the existing structure if reasonably possible
- only create a new top-level area if the user explicitly changes the schema

## Problem: A document mixes human decisions and agent notes

Rule:
- keep the human decision as the primary document under `decisions/`
- keep any agent-specific context brief and inside related domain pages when helpful
- do not create parallel human/agent decision trees

## Problem: The requested page is too broad

Signals:
- more than one major concept
- too many unrelated headings
- difficult to link from overview pages cleanly

Fix:
- create or update `overview.md`
- split large content into focused subtopic pages
- add links between them

## Problem: The user asks for a temporary work log

Rule:
- this wiki currently does not use `progress/` or `sessions/`
- convert the request into one of these if possible:
  - a durable workflow
  - a durable rule
  - a domain knowledge summary
  - a human decision record
- if it is truly ephemeral and cannot be made durable, question whether it belongs in `docs/wiki/`

## Problem: Unsure whether something is a domain page or a rule page

Heuristic:
- if it explains a business concept, behavior, interface, or flow in the product -> domain page
- if it states a reusable standard, constraint, or expectation across work -> common rule
- if it describes a repeatable sequence of actions -> workflow page

## Problem: Index pages become stale

Fix:
- whenever adding a page, immediately update its nearest discovery page
- minimum expectation:
  - domain page -> domain overview and/or `index.md`
  - human decision -> `decisions.md` and often `index.md`
  - rule/workflow -> `index.md`

## Problem: `docs/wiki/SCHEMA.md` does not exist

This means the wiki has not been initialized yet.

Fix:
1. Create the four foundation files first (see execution-protocol.md step 1).
2. Then proceed with the original request.

Do not skip foundation file creation — every other step in this skill depends on `SCHEMA.md` existing.

## Problem: The target file already exists and the user did not say to overwrite

Do not overwrite silently.

Fix:
1. Read the existing file first.
2. Merge or update the relevant sections.
3. Preserve any content that the user did not ask to change.

If the existing content conflicts with the new request, ask the user before replacing.

## Problem: The user provides content in English but the wiki is in Korean

Default fix:
- Translate the content to Korean before writing.
- Keep proper nouns, technical terms, and code identifiers in their original form.

If the surrounding section is already in English, match that language instead of translating.
If unsure, write in Korean and note the original English term in parentheses on first use.
