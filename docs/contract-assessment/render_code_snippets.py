"""Render the article's Python examples as syntax-highlighted Rich SVGs."""

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


def render(filename: str, title: str, code: str, width: int) -> None:
    console = Console(
        record=True,
        width=width,
        color_system="truecolor",
        file=StringIO(),
    )
    console.print(
        Syntax(
            code.rstrip(),
            "python",
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
    )
    render(
        "python-enforcement-test.svg",
        "test_service.py - enforcement twin",
        TEST_CODE,
        width=64,
    )
