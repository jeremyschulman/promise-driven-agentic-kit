"""Every contract document validates against its XSD schema."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from clinic.contracts.contract_doc import find_docs_dir

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_DIR = _REPO_ROOT / "schema"


def _schema(name: str) -> etree.XMLSchema:
    # Parsing from the file path lets lxml resolve <xs:include> relative to it.
    return etree.XMLSchema(etree.parse(str(_SCHEMA_DIR / name)))


def test_agent_contracts_validate() -> None:
    schema = _schema("agent-contract.xsd")
    files = sorted(find_docs_dir().glob("agent_*.xml"))
    assert files, "expected at least one agent_*.xml contract"
    for path in files:
        schema.assertValid(etree.parse(str(path)))


def test_manifests_validate() -> None:
    schema = _schema("agent-manifest.xsd")
    files = sorted(find_docs_dir().glob("manifest_*.xml"))
    assert files, "expected at least one manifest_*.xml"
    for path in files:
        schema.assertValid(etree.parse(str(path)))
