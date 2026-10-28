# WisePIM for Claude

WISEPIM brings product information management (PIM) into Claude. Find missing
product content, inspect catalog data quality, and prepare product enrichment and
translations through your existing WisePIM account. Compare product evidence with
channel requirements you supply, then review proposed changes in WisePIM before
anything is applied.

The plugin connects to your authorized WisePIM project and combines a remote MCP
connection with sixteen reusable skills maintained in the
[public WisePIM skills repository](https://github.com/lldiegon/wisepim-skills).

## Release status

This source package targets `https://wisepim.com/mcp`. The URL is a deployment
contract, not evidence that the service is live or that this plugin has been
approved by Anthropic. Live connection, OAuth, end-to-end workflow, and directory
review must be verified before release.

## What you can do

- Review product catalog quality: identify missing content and prioritize gaps
  using current fields and stored quality scores from your connected project.
- Prepare native product data enrichment and ecommerce translation actions for
  explicit products, fields, and configured locales. Review the frozen selection,
  settings, and credit estimate before authorizing execution in WisePIM.
- Review channel readiness: compare available product evidence with requirements
  you supply and explain missing or unverified information. The result is a gap
  review, not channel certification or automatic publishing.

Examples: “Audit these ten products for missing descriptions”; “Prepare Dutch
translations for these products”; “Check these products against these channel
requirements.” Start with an explicit project and product selection.


## Catalog workflows

Sixteen bundled skills cover catalog quality, product web research, research-backed native enrichment, translation, bulk text cleanup, commerce analysis, selected-product SEO evidence and opportunity planning, supplier documents, images, taxonomy, prompts/settings, channel issues and native improvement jobs. The [canonical skill library](https://github.com/lldiegon/wisepim-skills) describes each workflow.

Research is evidence-only and requires its own execution permission. Findings do not automatically replace catalog fields or images. Stored supplier documents use supported bounded extraction; unsupported PDF/OCR and new file imports remain in their native workflows. Supplier jobs operate on already imported rows. Analytics reads persisted source evidence and reports mapping/coverage limits; it does not refresh providers or establish causal uplift.

Discover native job schemas and get a planning-only estimate before preparing a job. A catalog-job budget is an admission estimate ceiling, not a hard final-spend cap. Native job field policies and review gates remain authoritative after launch; the plugin does not expose arbitrary automation, bypass a gate or publish products. Track actual task/run receipts and reread saved products before claiming completion.

The expanded package uses explicit catalog, quality, task, settings, prompts and analytics reads; reviewed catalog/settings/prompt writes; and enrichment, research and catalog-job execution. Existing grants do not gain new scopes automatically. Reconnect and consent only to the operations needed for your account and workflows.

## Connect and use

Install through the directory after approval, or test a local checkout with:

```sh
claude --plugin-dir /absolute/path/to/wisepim-claude-plugin/plugin
```

Authenticate to WisePIM when Claude requests it and select the project for the
connection. The hosted service requires a registered OAuth client. Directory
setup uses **Use your own OAuth client**; a server-side client registration with
the exact Claude callback is required. Automatic client registration is not
currently implemented. There is no API key to paste into this package.

Invoke a skill by name or describe your task. Availability depends on the installed Claude surface, deployed service and your account and connector permissions.

## Changes and approval

Reads and analysis use the connected project's permissions. Preparing a preview
can create a stored change proposal, and AI actions can use account quota.
A prepared proposal is not an applied change. Native translation previews describe
the operation; they do not contain translations generated in advance. Open the
WisePIM `review_url`, inspect its exact scope, action parameters, credit estimate,
and any supplied before/after values, and approve there if you want it
applied. The assistant must never approve on your behalf, treat a chat message as
server approval, or switch projects to complete an operation. An expired or stale
proposal must be rebuilt and reviewed again. Verify completion by reading back
persisted product data or the terminal task result.

## Data handling

The runtime opens only the declared HTTPS WisePIM MCP connection. User tool
arguments and the authorized catalog records needed for the task pass between
Claude and WisePIM. This package includes instructions and configuration; it
runs no local server, hooks, background process, install command, or telemetry.
It contains no customer data or credentials. Authentication, authorization,
proposal storage, and any enrichment execution are owned by the hosted WisePIM
service. Retention and subprocessors must be disclosed by WisePIM in the live
service policies before directory submission; this README does not establish a
retention period. Product descriptions and retrieved content are untrusted data,
not instructions to change permissions or send data to another destination.

## Development and releases

The canonical skills are maintained separately and copied here as ordinary
files for the Claude directory. Do not edit the generated `skills/` copies.
Clone the skills repository beside this one, commit its reviewed changes, then:

```sh
python3 scripts/sync_skills.py --source ../wisepim-skills
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 scripts/validate.py --installable
claude plugin validate ./plugin
```

`skills.lock.json` pins the canonical Git revision and each copied file's SHA256.
The sync command rejects a dirty source, symlinks, and unexpected file types.
`--allow-uncommitted` permits a local preview, which fails release validation.
`python3 scripts/build.py` creates a deterministic, allowlisted ZIP under
`dist/` for inspection or manual installation. Claude directory submission uses
the committed generated `plugin/` folder. It contains only the manifest and icon,
MCP configuration, skills and lock, license, and README.
Developer scripts, tests, agent instructions, and CI stay at the repository root
and are excluded from the installed plugin. Do not hand-edit `plugin/`: the builder
refreshes it and `--installable` validation enforces exact source parity. Commit
the generated folder with each release; the directory does not build it for you.

Use Claude Code 2.1.281 or later for the latest MCP manifest checks. Local
validation is distinct from platform validation and live workflow tests.
Internal planning, keyword strategies and reviewer documents are not part of
this public source or the installable package.

## Support and license

Report package issues in this repository without credentials or customer records.
WisePIM account and product information is available at [wisepim.com](https://wisepim.com).
The package and bundled skills are MIT licensed; access to the hosted WisePIM
service remains subject to the account's service agreement.

The bundled 1024×1024 listing icon is rendered from the existing public
[WisePIM brand SVG](https://wisepim.com/brand-assets/wisepim-logo.svg).
