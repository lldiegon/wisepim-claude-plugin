# Public Claude plugin repository

This repository contains public packaging, copied skills, documentation, and
local build tooling. Never add credentials, customer records, private reviewer
accounts, backend source, or deployment secrets. Preserve concurrent edits and
do not commit or publish unless the user requests it.

Canonical skills live in `lldiegon/wisepim-skills`. Edit them in that repository,
then run `python3 scripts/sync_skills.py --source ../wisepim-skills` from a clean
reviewed source commit. Do not hand-edit copied `skills/` files or their lock.
Use ordinary committed files, never submodules, Git LFS, or symlinks for runtime
components. The Claude directory reads the generated, committed `plugin/` subfolder.
Keep developer code, CI, and tests outside it. Do not hand-edit that output.

Before handing off a change, run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
python3 scripts/build.py
python3 scripts/validate.py --installable
claude plugin validate ./plugin
git diff --check
```

Use Claude Code 2.1.281 or later for the newest MCP validation checks and report
any older installed version explicitly. Local structure, source-integrity, and
packaging checks do not prove live OAuth, tenant isolation in production, task
completion, directory submission, approval, or publication. Keep those evidence
scopes distinct. See `submission/README.md` for deployment and release gates.
