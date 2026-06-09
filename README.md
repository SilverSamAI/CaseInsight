# CaseInsight

Full sales automation platform for **Silverside AI**. It researches prospects,
writes personalized cold outreach with Claude, enrolls contacts in Apollo
sequences, and syncs everything to HubSpot. Every outbound claim is constrained
by `silverside_facts.yaml`, the single source of truth for approved copy.

## Pipeline

```
Apollo search  ->  Claude draft  ->  Apollo sequence  ->  HubSpot CRM
  (research)        (guardrailed)       (enroll)            (sync)
```

## Install

```bash
cp .env.example .env   # fill in your API keys
pip install -e .
caseinsight --help
```

Required environment variables (see `.env.example`):

| Variable | Purpose |
|---|---|
| `APOLLO_API_KEY` | Apollo.io REST API key |
| `ANTHROPIC_API_KEY` | Claude API key |
| `HUBSPOT_ACCESS_TOKEN` | HubSpot private app token |
| `HUBSPOT_PIPELINE_ID` | Target deal pipeline |
| `APOLLO_DEFAULT_SEQUENCE_ID` | Sequence to enroll into |
| `APOLLO_EMAIL_ACCOUNT_ID` | Apollo email account that sends |
| `CLAUDE_MODEL` | Defaults to `claude-sonnet-4-6` |

## Commands

```bash
# Full pipeline in one shot
caseinsight run-all -t "VP Marketing" -t "CMO" -i "consumer goods" -n 20

# Or run each stage independently (JSON flows between steps)
caseinsight research -t "VP Marketing" -n 25 -o prospects.json
caseinsight draft prospects.json -o drafts.json
caseinsight enroll prospects.json --sequence-id abc123 --email-account xyz
caseinsight sync prospects.json
```

Use `caseinsight draft --dry-run prospects.json` to inspect the exact prompt
(with only approved facts) without calling Claude.

## Copy guardrails

`silverside_facts.yaml` carries a `usage` / `outbound_use` flag on every claim,
client, and metric. CaseInsight enforces it in two layers:

1. **Prompt layer** — only `approved_for_outbound` facts are injected into the
   Claude system prompt, so the model cannot cite anything else.
2. **Validation layer** — every generated email is scanned for forbidden terms,
   `needs_verification` client names, em dashes, and unverified numeric claims.
   Drafts that fail are flagged (`passed_guardrail = false`).

## Other behavior

- **Dedup** — contacted prospects are tracked in `.caseinsight_state.json`;
  `research` skips them by default (`--include-contacted` to override).
- **Resilience** — Apollo calls retry with exponential backoff on 429/5xx.
- **Prompt caching** — the facts system prompt is cached across a batch run.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Package layout

```
caseinsight/
  cli.py              Typer app (research / draft / enroll / sync / run-all)
  config.py           env loading
  models.py           Prospect, EmailDraft, SyncResult
  facts/              YAML loader + guardrail logic
  research/           Apollo client + prospect mapping
  outreach/           prompt builder, Claude generator, validator
  sequencing/         Apollo sequence enrollment
  crm/                HubSpot sync
  utils/              retry + contact-state tracker
```
