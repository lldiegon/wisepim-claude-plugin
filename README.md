# WisePIM for Claude

Connect your WisePIM catalog to Claude to inspect product content, prepare product
translations, and review readiness against channel requirements you supply.
The plugin combines a remote MCP connection with three reusable skills maintained
in the [public WisePIM skills repository](https://github.com/lldiegon/wisepim-skills).

## Release status

This source package targets `https://wisepim.com/mcp`. The URL is a deployment
contract, not evidence that the service is live or that this plugin has been
approved by Anthropic. Live connection, OAuth, end-to-end workflow, and directory
review must pass the [submission checklist](submission/README.md) before release.

## What you can do

- Ask which products in your connected project need attention, with evidence
  from their current fields and quality analysis.
- Prepare translations for a named locale and a bounded product selection.
- Compare current product data with explicitly supplied channel requirements.
  This produces a gap review, not channel certification or automatic publishing.

Examples: “Audit these ten products for missing descriptions”; “Prepare Dutch
translations for these products”; “Check these products against these channel
requirements.” Start with an explicit project and product selection.

## Connect and use

Install through the directory after approval, or test a local checkout with:

```sh
claude --plugin-dir /absolute/path/to/wisepim-claude-plugin
```

Authenticate to WisePIM when Claude requests it and select the project for the
connection. The hosted service requires a registered OAuth client. Directory
setup uses **Use your own OAuth client**; a server-side client registration with
the exact Claude callback is required. Automatic client registration is not
currently implemented. There is no API key to paste into this package.

Invoke a skill by name or describe your task. The skills are
`catalog-quality-audit`, `prepare-product-translations`, and
`channel-readiness-review`. Availability depends on the installed Claude surface
and your account and connector permissions.

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
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
claude plugin validate .
```

`skills.lock.json` pins the canonical Git revision and each copied file's SHA256.
The sync command rejects a dirty source, symlinks, and unexpected file types.
`--allow-uncommitted` permits a local preview, which fails release validation.
`python3 scripts/build.py` creates a deterministic, allowlisted ZIP under
`dist/` for inspection or manual installation. Claude directory submission uses
the committed GitHub repository root, including the generated skills and lock,
not that ZIP. Tests and build tooling are not runtime entry points.

Use Claude Code 2.1.281 or later for the latest MCP manifest checks. Local
validation is distinct from portal validation and live workflow tests. See
[submission/README.md](submission/README.md) for the connector and plugin
submission sequence and known deployment prerequisites.

## Support and license

Report package issues in this repository without credentials or customer records.
WisePIM account and product information is available at [wisepim.com](https://wisepim.com).
The package and bundled skills are MIT licensed; access to the hosted WisePIM
service remains subject to the account's service agreement.

The bundled 1024×1024 listing icon is rendered from the existing public
[WisePIM brand SVG](https://wisepim.com/brand-assets/wisepim-logo.svg).
