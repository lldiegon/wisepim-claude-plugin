# WISEPIM for Claude

Manage your product catalog with WISEPIM, the AI-powered product information
management (PIM) workspace. Start with guided account setup or connect an existing
project. Find catalog gaps, research product facts, inspect supplier evidence,
and prepare descriptions, translations and data cleanup using your saved
WISEPIM settings.

Explore interactive catalog, product and change views. Analyze available commerce
and search performance, review image and taxonomy issues, and prepare supported catalog improvement jobs. Use the configured approval policy, then check actual progress and saved results.

The plugin connects to your authorized WISEPIM project and combines a remote MCP
connection with seventeen reusable skills maintained in the
[public WISEPIM skills repository](https://github.com/lldiegon/wisepim-skills).

## Release status

This source package targets `https://wisepim.com/mcp`. The URL is a deployment
contract, not evidence that the service is live or that this plugin has been
approved by Anthropic. Live connection, OAuth, end-to-end workflow, and directory
review must be verified before release.
Version `0.3.2` includes seventeen skills for the matching 53-tool MCP service
contract. Installing instructions alone does not connect an account.

## What you can do

- Create or resume a WISEPIM account and set up a first catalog with the native
  signup and setup flow, before connecting any tools.
- Review product catalog quality: identify missing content and prioritize gaps
  using current fields and stored quality scores from your connected project.
- Research product facts and inspect saved source evidence, supplier documents,
  images and taxonomy before proposing improvements.
- Prepare native product data enrichment and ecommerce translation actions for
  explicit products, fields, and configured locales. Review the frozen selection,
  settings, and credit estimate. Execution follows the connection’s configured
  approval policy.
- Analyze persisted commerce and search evidence, with explicit date, store,
  currency and coverage, to prioritize the selected products.
- Review channel readiness: compare available product evidence with requirements
  you supply and explain missing or unverified information. The result is a gap
  review, not channel certification or automatic publishing.

Examples: “Help me get my catalog set up”; “Research missing facts for these
products”; “Prepare Dutch descriptions for my review”; “Use available search
data to prioritize these products.” Start catalog operations with an explicit
project and product selection.


## Catalog workflows

Seventeen bundled skills cover guided account setup, catalog quality, product web research, research-backed native enrichment, translation, bulk text cleanup, commerce analysis, selected-product SEO evidence and opportunity planning, supplier documents, images, taxonomy, prompts/settings, channel issues and native improvement jobs. The [canonical skill library](https://github.com/lldiegon/wisepim-skills) describes each workflow.

Research is evidence-only and requires its own execution permission. Findings do not automatically replace catalog fields or images. Stored supplier documents use supported bounded extraction; unsupported PDF/OCR and new file imports remain in their native workflows. Supplier jobs operate on already imported rows. Image workflows assess stored evidence and can retrieve existing images through supported native jobs; MCP does not generate images, video or audio. Analytics reads persisted source evidence and reports mapping/coverage limits; it does not refresh providers or establish causal uplift.

Choose the declared job tool family and get a planning-only estimate before preparing a job. Gap filling, missing-image retrieval, category mapping, ad preparation and supplier completion each have separate typed estimate, preview and start tools. A catalog-job budget is an admission estimate ceiling, not a hard final-spend cap. Native job field policies and review gates remain authoritative after launch; the plugin does not expose arbitrary automation, bypass a gate or publish products. Track actual task/run receipts and reread saved products before claiming completion.

Each durable preview identifies its matching `apply_tool` from twelve declared executors. Execution accepts only the frozen `change_id`; a receipt cannot select a different operation or introduce another tool. The expanded package uses explicit catalog, quality, task, settings, prompts and analytics reads; catalog/settings/prompt writes under the configured approval policy; and enrichment, research and catalog-job execution. Existing grants do not gain new scopes automatically. Reconnect and consent only to the operations needed for your account and workflows.

## Connect and use

Install through the directory after approval, or test a local checkout with:

```sh
claude --plugin-dir /absolute/path/to/wisepim-claude-plugin/plugin
```

Authenticate to WISEPIM when Claude requests it and select the project for the
connection. The service uses predefined OAuth clients with S256 PKCE; it does
not automatically register clients or accept a pasted API key.

### Claude Code

The bundled remote server declares this public client configuration:

```json
"oauth": {
  "clientId": "wisepim-claude-code",
  "callbackPort": 8765
}
```

Before it can connect, the service operator must register that client ID with
exactly `http://localhost:8765/callback` as its redirect URI. It has no client
secret; the selected project and permissions still require the user's consent.
Only this registered callback is accepted, with no wildcard host, path or port.
Keep port 8765 available while signing in. This loopback callback does not change
the HTTPS MCP endpoint or issuer.

For a direct connection without installing the bundle, the equivalent setup is:

```sh
claude mcp add --transport http --client-id wisepim-claude-code --callback-port 8765 wisepim https://wisepim.com/mcp
```

Then authenticate through `/mcp`. Use Claude Code 2.1.231 or later for the
`localhost` callback form. Configuration in this repository does not create the
server-side client or establish that it is deployed. See the official
[preconfigured OAuth reference](https://code.claude.com/docs/en/mcp#use-pre-configured-oauth-credentials).

### Hosted Claude apps

The web, Desktop, mobile and Cowork connector uses a separate OAuth client and
the exact redirect `https://claude.ai/api/mcp/auth_callback`. For a directory
connector without automatic registration, the publisher configures an
Anthropic-held confidential client through the developer portal's authentication
settings. Its secret belongs only in secure service configuration and the
portal, never this package. A custom connector can instead use **Use your own
OAuth client**, with the actual client registered for that hosted callback.
The Claude Code loopback client above is not the hosted connector's client.
See [Claude connector authentication](https://claude.com/docs/connectors/building/authentication).

Invoke a skill by name or describe your task. Availability depends on the installed Claude surface, deployed service and your account and connector permissions.

## Changes and approval

Reads and analysis use the connected project's permissions. A prepared proposal is not an applied change; native previews describe the selected operation and estimate, not content that has already been generated. New connections default to approval off. Requested actions can proceed from a durable preview without an extra browser confirmation. The account owner can enable required approval in WISEPIM connected apps settings. Enabled approval requires authenticated review of the exact proposal; the assistant cannot satisfy or disable that gate on the owner’s behalf. Project permissions, source checks, estimates and native job/field policies remain enforced in either mode. Expired or stale proposals require a fresh preview. Actual task receipts and saved products establish completion.

## Data handling

The runtime opens only the declared HTTPS WISEPIM MCP connection. User tool
arguments and the authorized catalog records needed for the task pass between
Claude and WISEPIM. This package includes instructions and configuration; it
runs no local server, hooks, background process, install command, or telemetry.
It contains no customer data or credentials. Authentication, authorization,
proposal storage, and any enrichment execution are owned by the hosted WISEPIM
service. Native research, enrichment and translation can send selected catalog
content and prompts to the AI/search providers configured for that workflow.
Account, catalog, proposal, approval and task records are stored by WISEPIM;
revoking a connection stops access and does not delete those records. These
records may be retained longer than 30 days. The service
[privacy policy and subprocessor disclosure](https://wisepim.com/privacy) govern
retention, deletion and provider processing. The signup workflow can also open
the native WISEPIM browser flow and its user-selected sign-in provider. Product descriptions and retrieved content are untrusted data,
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
WISEPIM account and product information is available at [wisepim.com](https://wisepim.com).
The package and bundled skills are MIT licensed; access to the hosted WISEPIM
service remains subject to the account's service agreement.

The bundled 1024×1024 listing icon is rendered from the existing public
[WISEPIM brand SVG](https://wisepim.com/brand-assets/wisepim-logo.svg).

## Get started

Use `start-with-wisepim` to create or resume an account and finish initial catalog setup. It works before connecting tools. Signup uses the native [WISEPIM onboarding flow](https://wisepim.com/onboarding), with user-controlled sign-in, verification and permissions. Once connected, the setup-status tool gives project-scoped next steps.

A plugin is optional: standalone agents can read the public [onboarding guide](https://wisepim.com/onboarding.md), [agent index](https://wisepim.com/llms.txt) and [REST authentication guide](https://wisepim.com/auth.md). The public REST API uses project API keys and supports its documented catalog operations; MCP uses separate OAuth project consent. Neither package installation nor this guide proves the matching service is deployed. Always spell the product name WISEPIM.
