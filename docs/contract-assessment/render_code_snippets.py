"""Render the article's code examples as syntax-highlighted Rich SVGs."""

from io import StringIO
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax
from rich.terminal_theme import MONOKAI


HERE = Path(__file__).resolve().parent

ASSESSMENT_CODE = '''\
def commit_action(*, precondition_met: bool) -> dict:
    # NoUnsafeCommit
    if not precondition_met:
        return refusal(
            "precondition_required",
            "precondition_met",
            "The precondition must hold.",
        )

    apply_change()
    return ok(committed=True)
'''

TEST_CODE = '''\
def test_no_unsafe_commit():
    result = commit_action(precondition_met=False)
    assert result["ok"] is False
    assert result["unmet"] == "precondition_met"
    assert authoritative_state_unchanged()
'''

FIZZBEE_CODE = '''\
action CommitAction:
    require precondition_met
    committed = True
always assertion NoUnsafeCommit:
    return (not committed) or precondition_met
'''

PROMISES_XML = '''\
<promises>
  <tool name="commit_action"/>
  <offer id="safe_action">
    <condition ref="precondition_met"/>
  </offer>
  <use id="evidence" from="provider"
       quenches="precondition_met"/>
</promises>
'''

ENFORCEMENT_XML = '''\
<enforcement>
  <rule id="NoUnsafeCommit">
    Refuse unless precondition_met.</rule>
</enforcement>
'''


def render(filename: str, title: str, code: str, width: int, lexer: str) -> None:
    console = Console(
        record=True,
        width=width,
        color_system="truecolor",
        file=StringIO(),
    )
    console.print(
        Syntax(
            code.rstrip(),
            lexer,
            theme="monokai",
            line_numbers=True,
            padding=(1, 2),
            word_wrap=False,
        )
    )
    console.save_svg(
        str(HERE / filename),
        title=title,
        theme=MONOKAI,
        clear=True,
        unique_id=Path(filename).stem.replace("-", "_"),
    )


if __name__ == "__main__":
    render(
        "python-assessment-boundary.svg",
        "service.py - authoritative boundary",
        ASSESSMENT_CODE,
        width=64,
        lexer="python",
    )
    render(
        "python-enforcement-test.svg",
        "test_service.py - enforcement twin",
        TEST_CODE,
        width=64,
        lexer="python",
    )
    render(
        "contract-intent-fizzbee.svg",
        "<verifiable-behavior>",
        FIZZBEE_CODE,
        width=58,
        lexer="python",
    )
    render(
        "contract-intent-promises.svg",
        "<promises>",
        PROMISES_XML,
        width=64,
        lexer="xml",
    )
    render(
        "contract-intent-enforcement.svg",
        "<enforcement>",
        ENFORCEMENT_XML,
        width=52,
        lexer="xml",
    )
