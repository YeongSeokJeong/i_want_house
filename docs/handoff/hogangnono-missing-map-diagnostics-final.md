# Hogangnono Missing Map Diagnostics Handoff

## Summary
- Completed backlog item `BL-20260615-005`.
- Missing Hogangnono apt hash mapping failures now tell the operator which watchlist complexes need configuration and what JSON entry shape to add.

## Delivered
- Improved `HogangnonoListingSourceClient._apt_hash_for` error text.
- Added `required_env` and `missing_mapping_targets[]` to collector diagnostics for Hogangnono mapping failures.
- Preserved the existing collector failure behavior and previous JSON state safety.
- Added reliability tests for direct source error and loop diagnostics.
- Updated the JeonseLoop domain wiki.

## Verification
- Targeted reliability tests for Hogangnono missing mapping and zero-listing diagnostics.
- `python -m unittest discover -s tests -v`

## Follow-up
- The task does not discover or validate Hogangnono hashes automatically; operators still need to provide the real hash values.
