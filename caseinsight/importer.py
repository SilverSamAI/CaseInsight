from __future__ import annotations
import csv
import json
from pathlib import Path
from .models import Prospect

# Column aliases — handles different header spellings from Salesforce / HubSpot exports
_ALIASES: dict[str, str] = {
    # email
    "email address": "email",
    "e-mail": "email",
    # name
    "first name": "first_name",
    "firstname": "first_name",
    "last name": "last_name",
    "lastname": "last_name",
    "full name": "_full_name",
    "name": "_full_name",
    # title
    "job title": "title",
    "position": "title",
    "role": "title",
    # company
    "company name": "company",
    "organization": "company",
    "account name": "company",
    # misc
    "linkedin": "linkedin_url",
    "linkedin url": "linkedin_url",
    "linkedin profile": "linkedin_url",
    "industry": "industry",
    "employees": "employee_count",
    "num employees": "employee_count",
    "number of employees": "employee_count",
}


def _norm_header(h: str) -> str:
    return _ALIASES.get(h.strip().lower(), h.strip().lower())


def _split_name(full: str) -> tuple[str, str]:
    parts = full.strip().split(" ", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def load_csv(path: str | Path) -> list[Prospect]:
    """Parse a CSV file into Prospect objects. Handles common export formats."""
    prospects: list[Prospect] = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            normed = {
                _norm_header(k): v.strip()
                for k, v in row.items()
                if k is not None and isinstance(v, str) and v.strip()
            }

            first = normed.get("first_name", "")
            last = normed.get("last_name", "")
            if not first and not last and "_full_name" in normed:
                first, last = _split_name(normed["_full_name"])

            if not first and not last:
                continue  # skip blank rows

            emp_raw = normed.get("employee_count", "")
            employee_count: int | None = None
            if emp_raw:
                try:
                    employee_count = int(emp_raw.replace(",", "").replace("+", "").split("-")[0].strip())
                except ValueError:
                    pass

            prospects.append(
                Prospect(
                    first_name=first,
                    last_name=last,
                    email=normed.get("email"),
                    title=normed.get("title"),
                    company=normed.get("company"),
                    linkedin_url=normed.get("linkedin_url"),
                    industry=normed.get("industry"),
                    employee_count=employee_count,
                )
            )
    return prospects


def load_json(path: str | Path) -> list[Prospect]:
    data = json.loads(Path(path).read_text())
    return [Prospect.from_dict(p) for p in data]


def load_file(path: str | Path) -> list[Prospect]:
    """Auto-detect CSV or JSON based on file extension."""
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return load_csv(p)
    return load_json(p)
