from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from .config import load_config
from .facts.loader import load_facts
from .models import EmailDraft, Prospect
from .outreach.generator import generate_batch
from .research.apollo_client import ApolloClient
from .research.prospect import filter_prospects, search_prospects
from .sequencing.apollo_sequences import enroll_batch
from .crm.hubspot_sync import build_hubspot_client, sync_batch
from .utils.state import ContactState

app = typer.Typer(
    name="caseinsight",
    help="Silverside AI sales automation platform",
    add_completion=False,
)
console = Console()


def _load_prospects(path: Path) -> list[Prospect]:
    data = json.loads(path.read_text())
    return [Prospect.from_dict(p) for p in data]


def _save(items: list, path: Path) -> None:
    path.write_text(json.dumps([asdict(i) for i in items], indent=2))
    console.print(f"[green]Saved {len(items)} records to {path}[/green]")


@app.command()
def research(
    title: list[str] = typer.Option(..., "--title", "-t", help="Job title to target (repeatable)"),
    industry: list[str] = typer.Option([], "--industry", "-i", help="Industry filter (repeatable)"),
    company: list[str] = typer.Option([], "--company", "-c", help="Target company name (repeatable)"),
    limit: int = typer.Option(25, "--limit", "-n", help="Max prospects to return"),
    require_email: bool = typer.Option(True, "--require-email/--no-require-email"),
    skip_contacted: bool = typer.Option(
        True, "--skip-contacted/--include-contacted",
        help="Exclude prospects already recorded in the local contact state",
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save to JSON file"),
) -> None:
    """Search and enrich prospects via Apollo."""
    config = load_config()
    client = ApolloClient(config.apollo_api_key)

    with console.status("Searching Apollo..."):
        prospects = search_prospects(
            client,
            titles=title,
            companies=company or None,
            industries=industry or None,
            limit=limit,
        )
    prospects = filter_prospects(prospects, require_email=require_email)
    if skip_contacted:
        state = ContactState()
        before = len(prospects)
        prospects = [p for p in prospects if not state.seen(p.email)]
        skipped = before - len(prospects)
        if skipped:
            console.print(f"[dim]Skipped {skipped} already-contacted prospects[/dim]")
    console.print(f"Found [bold]{len(prospects)}[/bold] prospects")

    table = Table(title="Prospects")
    for col in ["Name", "Title", "Company", "Email", "Industry"]:
        table.add_column(col)
    for p in prospects:
        table.add_row(
            p.full_name,
            p.title or "",
            p.company or "",
            p.email or "[dim]none[/dim]",
            p.industry or "",
        )
    console.print(table)

    if output:
        _save(prospects, output)
    else:
        console.print(json.dumps([asdict(p) for p in prospects], indent=2))


@app.command()
def draft(
    input_file: Path = typer.Argument(..., help="JSON file from `research` command"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    context: str = typer.Option("", "--context", help="Extra context injected into every prompt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print prompts without calling Claude"),
) -> None:
    """Generate personalized cold emails for a list of prospects."""
    config = load_config()
    facts = load_facts(config.silverside_facts_path)
    prospects = _load_prospects(input_file)

    if dry_run:
        from .outreach.prompt_builder import build_system_prompt, build_user_prompt
        console.rule("System Prompt")
        console.print(build_system_prompt(facts))
        if prospects:
            console.rule("Sample User Prompt (first prospect)")
            console.print(build_user_prompt(prospects[0], context))
        return

    drafts: list[EmailDraft] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Generating emails...", total=len(prospects))
        drafts = generate_batch(
            prospects,
            facts,
            config,
            context_notes=context,
            on_progress=lambda done, _total: progress.update(task, completed=done),
        )

    passed = sum(1 for d in drafts if d.passed_guardrail)
    console.print(f"\n[green]{passed}/{len(drafts)}[/green] drafts passed guardrail")

    for d in drafts:
        status = "[green]PASS[/green]" if d.passed_guardrail else "[red]FAIL[/red]"
        console.print(f"\n{status} [bold]{d.prospect.full_name}[/bold] ({d.prospect.company})")
        console.print(f"Subject: {d.subject}")
        console.print(d.body[:300] + "..." if len(d.body) > 300 else d.body)
        for v in d.violations:
            console.print(f"  [yellow]! {v}[/yellow]")

    if output:
        _save(drafts, output)


@app.command()
def enroll(
    input_file: Path = typer.Argument(..., help="JSON file from `research` command"),
    sequence_id: Optional[str] = typer.Option(None, "--sequence-id"),
    email_account_id: Optional[str] = typer.Option(None, "--email-account"),
) -> None:
    """Enroll prospects in an Apollo email sequence."""
    config = load_config()
    seq_id = sequence_id or config.apollo_default_sequence_id
    acct_id = email_account_id or config.apollo_email_account_id
    if not seq_id:
        console.print("[red]--sequence-id required (or set APOLLO_DEFAULT_SEQUENCE_ID)[/red]")
        raise typer.Exit(1)
    if not acct_id:
        console.print("[red]--email-account required (or set APOLLO_EMAIL_ACCOUNT_ID)[/red]")
        raise typer.Exit(1)

    client = ApolloClient(config.apollo_api_key)
    prospects = _load_prospects(input_file)
    results = enroll_batch(client, prospects, seq_id, acct_id, console)
    enrolled = sum(1 for v in results.values() if v)
    state = ContactState()
    for p in prospects:
        if results.get(p.email or p.full_name):
            state.mark(p.email, "enrolled")
    state.save()
    console.print(f"\n[green]{enrolled}/{len(prospects)}[/green] prospects enrolled")


@app.command()
def sync(
    input_file: Path = typer.Argument(..., help="JSON file from `research` command"),
    pipeline_id: Optional[str] = typer.Option(None, "--pipeline"),
    no_deals: bool = typer.Option(False, "--no-deals"),
) -> None:
    """Sync prospects to HubSpot CRM."""
    config = load_config()
    pipeline = pipeline_id or config.hubspot_pipeline_id
    hs = build_hubspot_client(config.hubspot_access_token)
    prospects = _load_prospects(input_file)
    results = sync_batch(hs, prospects, pipeline, console, with_deal=not no_deals)
    synced = sum(1 for r in results if r.hubspot_contact_id)
    state = ContactState()
    for r in results:
        if r.hubspot_contact_id:
            state.mark(r.prospect_email, "synced")
    state.save()
    console.print(f"\n[green]{synced}/{len(prospects)}[/green] contacts synced to HubSpot")
    for err in [e for r in results for e in r.errors]:
        console.print(f"[red]{err}[/red]")


@app.command()
def run_all(
    title: list[str] = typer.Option(..., "--title", "-t", help="Job title to target (repeatable)"),
    industry: list[str] = typer.Option([], "--industry", "-i"),
    company: list[str] = typer.Option([], "--company", "-c"),
    sequence_id: Optional[str] = typer.Option(None, "--sequence-id"),
    email_account_id: Optional[str] = typer.Option(None, "--email-account"),
    pipeline_id: Optional[str] = typer.Option(None, "--pipeline"),
    limit: int = typer.Option(25, "--limit", "-n"),
    output_dir: Path = typer.Option(Path("."), "--output-dir", help="Directory for output JSON files"),
) -> None:
    """Full pipeline: research -> draft emails -> enroll in Apollo -> sync to HubSpot."""
    config = load_config()
    facts = load_facts(config.silverside_facts_path)
    apollo = ApolloClient(config.apollo_api_key)
    seq_id = sequence_id or config.apollo_default_sequence_id
    acct_id = email_account_id or config.apollo_email_account_id
    pipe_id = pipeline_id or config.hubspot_pipeline_id
    output_dir.mkdir(parents=True, exist_ok=True)

    console.rule("[bold]1 / Research[/bold]")
    with console.status("Searching Apollo..."):
        prospects = search_prospects(
            apollo,
            titles=title,
            companies=company or None,
            industries=industry or None,
            limit=limit,
        )
    prospects = filter_prospects(prospects, require_email=True)
    console.print(f"Found [bold]{len(prospects)}[/bold] qualified prospects")
    _save(prospects, output_dir / "prospects.json")

    console.rule("[bold]2 / Draft Emails[/bold]")
    drafts: list[EmailDraft] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as prog:
        task = prog.add_task("Generating emails...", total=len(prospects))
        drafts = generate_batch(
            prospects,
            facts,
            config,
            on_progress=lambda done, _t: prog.update(task, completed=done),
        )
    _save(drafts, output_dir / "drafts.json")
    passed = sum(1 for d in drafts if d.passed_guardrail)
    console.print(f"[green]{passed}/{len(drafts)}[/green] drafts passed guardrail")

    if seq_id and acct_id:
        console.rule("[bold]3 / Enroll in Sequence[/bold]")
        enroll_batch(apollo, prospects, seq_id, acct_id, console)
    else:
        console.print("[yellow]Skipping sequence enrollment (no sequence-id or email-account configured)[/yellow]")

    console.rule("[bold]4 / HubSpot Sync[/bold]")
    hs = build_hubspot_client(config.hubspot_access_token)
    sync_batch(hs, prospects, pipe_id, console)

    console.rule("[bold]Done[/bold]")
    console.print(f"[green]Pipeline complete. {passed}/{len(drafts)} emails passed guardrail.[/green]")


if __name__ == "__main__":
    app()
