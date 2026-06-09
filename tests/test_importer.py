import textwrap
from pathlib import Path
import json
import pytest
from caseinsight.importer import load_csv, load_json, load_file


def write_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "prospects.csv"
    p.write_text(textwrap.dedent(content))
    return p


def test_standard_headers(tmp_path):
    p = write_csv(tmp_path, """\
        first_name,last_name,email,title,company,industry
        Jane,Doe,jane@acme.com,CMO,Acme,retail
    """)
    prospects = load_csv(p)
    assert len(prospects) == 1
    assert prospects[0].first_name == "Jane"
    assert prospects[0].email == "jane@acme.com"
    assert prospects[0].industry == "retail"


def test_alias_headers(tmp_path):
    p = write_csv(tmp_path, """\
        First Name,Last Name,Email Address,Job Title,Company Name,Employees
        John,Smith,john@corp.com,VP Marketing,Corp Inc,500
    """)
    prospects = load_csv(p)
    assert prospects[0].title == "VP Marketing"
    assert prospects[0].employee_count == 500


def test_full_name_split(tmp_path):
    p = write_csv(tmp_path, """\
        Name,Email,Title
        Alice Wonderland,alice@w.com,CMO
    """)
    prospects = load_csv(p)
    assert prospects[0].first_name == "Alice"
    assert prospects[0].last_name == "Wonderland"


def test_blank_rows_skipped(tmp_path):
    p = write_csv(tmp_path, """\
        first_name,last_name,email
        ,,,
        Bob,Jones,bob@j.com
    """)
    prospects = load_csv(p)
    assert len(prospects) == 1


def test_load_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps([{"first_name": "X", "last_name": "Y", "email": "x@y.com"}]))
    prospects = load_json(p)
    assert prospects[0].email == "x@y.com"


def test_load_file_detects_csv(tmp_path):
    p = write_csv(tmp_path, "first_name,last_name\nA,B\n")
    prospects = load_file(p)
    assert prospects[0].first_name == "A"


def test_employee_count_parsing(tmp_path):
    p = write_csv(tmp_path, 'first_name,last_name,employees\nA,B,"1,000"\n')
    prospects = load_csv(p)
    assert prospects[0].employee_count == 1000
