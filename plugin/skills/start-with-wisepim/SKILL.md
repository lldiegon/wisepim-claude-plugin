---
name: start-with-wisepim
description: Help a new or returning user create a WISEPIM account, finish initial setup, connect an agent with or without an installed plugin, and reach a verified first catalog result.
---

# Get started with WISEPIM

This workflow works before any WISEPIM connection exists. Do not require an installed plugin or an API key just to help someone sign up. Read https://wisepim.com/onboarding.md for current account and connection guidance; https://wisepim.com/llms.txt and https://wisepim.com/auth.md cover standalone agent discovery and REST authentication.

## Create or resume the account

1. Establish whether the user already has a WISEPIM account and their first goal: import a catalog, improve product content, translate, or explore. Reuse an existing account and project when available.
2. For a new account, open or share https://wisepim.com/onboarding. Help with requested non-secret company/store information in the native form. The user controls credentials or social sign-in, verification, CAPTCHA when presented, legal acceptance and permissions. Keep passwords, login codes, API keys and store credentials out of chat, URLs, logs and skill files. Preserve newsletter choices; signup is not marketing consent.
3. Complete the existing setup wizard with the user. Confirm the intended company/project, source catalog and source/target languages. A new project can take time to appear after signup: retry the native project selector rather than creating duplicate accounts or projects. If signup times out, check whether it succeeded before repeating it. A submitted form is not proof of account creation.

## Connect an agent, with or without a plugin

- **Installed plugin or direct remote MCP:** use the host's connection flow for https://wisepim.com/mcp when available. Sign in and explicitly authorize the intended project and only the permissions needed. Continue the exact host-issued OAuth request; never invent a client ID, callback, grant, account or token. When this connection flow is enabled, WISEPIM resumes an in-progress connection after native signup/setup. If the request expired, restart the host connection. Installing a plugin does not establish authentication or service deployment.
- **Standalone agent using REST:** no plugin installation is needed. Read https://wisepim.com/auth.md and https://wisepim.com/openapi.json. A permitted owner/admin creates a project API key in WISEPIM Settings > API access if the plan supports it, and configures it in the agent's secure credential store. Validate the connection with `GET https://wisepim.com/api/public/v1/me`; confirm the project and scopes. The public REST API provides its documented catalog operations, not the full MCP workflow catalog. Never send browser session or MCP tokens as REST API keys.
- **No connected tools:** the agent can still guide signup and native browser setup. Report this state accurately rather than inventing tool results or asking for credentials in chat.

## Reach the first useful result

When authenticated MCP tools are available, call `wisepim_get_setup_status`, confirm the returned project and observed next steps, and read `wisepim_list_projects` for authorized locales. Never reuse another project's IDs. Missing permissions produce unknown/unavailable evidence, not an incomplete setup verdict.

Guide the user through the next relevant native setup link: import a small representative sample in Settings > Import, configure languages and brand instructions, and connect the intended store only when requested. Store connection and import do not imply export or publication. REST agents inspect the current OpenAPI contract and read back the exact products they create/update; they do not call undocumented signup, internal setup or paid-job APIs.

For the first content improvement through MCP, inspect a small exact product selection, settings and source facts. Prepare a native enrichment or translation preview only when requested, explain scope and estimated credits, and inspect `execution_policy.require_approval` in setup status and `require_approval`/`can_apply` on the preview. New connections default to approval off, configurable by the owner in WISEPIM connected apps settings. With approval off, an authorized execution request may proceed from the preview; with approval required, share its exact WISEPIM review URL and wait for recorded approval. Then check the task and saved product before reporting a result. Keep publication, billing, bulk imports and wider jobs within the user's requested scope.

Finish with observed account/connection state, the exact project, what setup is verified, the first saved result if any, and one concrete next step. Do not claim account creation, configuration, import, credits, task completion or publication from instructions alone. Always spell the product name WISEPIM.
