#!/usr/bin/env python3
"""Render the article's code snippets to styled PNG "cards" with syntax
highlighting, so the Medium pieces show crafted code that matches the diagrams.

Every card is generated from source here, so the images stay in sync with the
contracts and enforcement code — regenerate whenever those change:

    python3 tools/codecard.py

Outputs land in ../images/ (code-*.png). Requires: pygments, pillow, and a
DejaVu Sans Mono font (set FONT_DIR env var if it's not auto-found).

Pygments only tokenizes and classifies; we lay tokens out with Pillow directly,
because Pygments' bundled ImageFormatter is broken on Pillow >= 10 (getsize).
"""
import os

from PIL import Image, ImageDraw, ImageFont
from pygments.lexer import RegexLexer, words
from pygments.lexers import XmlLexer, PythonLexer
from pygments.token import (Keyword, Comment, Name, Number, Operator, String,
                            Text, Punctuation, Token, Generic)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images") + os.sep


def _find_font_dir():
    candidates = [
        os.environ.get("FONT_DIR", ""),
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/dejavu/",
        "/opt/homebrew/share/fonts/",           # macOS (Homebrew fonts)
        "/Library/Fonts/", os.path.expanduser("~/Library/Fonts/"),
    ]
    for d in candidates:
        if d and os.path.exists(os.path.join(d, "DejaVuSansMono.ttf")):
            return d
    raise SystemExit(
        "DejaVu Sans Mono not found. Install it (e.g. `apt install fonts-dejavu` "
        "or `brew install --cask font-dejavu`) or set FONT_DIR to its folder.")


FONT = _find_font_dir()
FS = 30
LINE_PAD = 8
PAD = 26
HEADER_H = 56
RADIUS = 18

f_norm = ImageFont.truetype(FONT + "DejaVuSansMono.ttf", FS)
f_bold = ImageFont.truetype(FONT + "DejaVuSansMono-Bold.ttf", FS)
f_ital = ImageFont.truetype(FONT + "DejaVuSansMono-Oblique.ttf", FS)
f_bi = ImageFont.truetype(FONT + "DejaVuSansMono-BoldOblique.ttf", FS)
f_label = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 24)

CHAR_W = f_norm.getlength("M")
ASC, DESC = f_norm.getmetrics()
LINE_H = ASC + DESC + LINE_PAD

C_TEXT = "#1f2937"
C_KW = "#7c3aed"
C_CONST = "#b45309"
C_CLASS = "#1e3a8a"
C_NAME = "#1f2937"
C_STR = "#047857"
C_COMMENT = "#94a3b8"
C_OP = "#475569"
C_ATTR = "#0d9488"
C_PASS = "#059669"
C_FAIL = "#dc2626"


class FizzLexer(RegexLexer):
    """Minimal highlighter for FizzBee (no upstream Pygments lexer exists)."""
    name = "Fizz"
    tokens = {
        "root": [
            (r"#.*$", Comment.Single),
            (words(("atomic", "action", "always", "assertion", "require",
                    "return", "if", "else", "elif", "for", "while", "in",
                    "and", "or", "not", "func", "role"), suffix=r"\b"), Keyword),
            (words(("oneof", "True", "False", "None"), suffix=r"\b"), Keyword.Constant),
            (r'"[^"]*"', String),
            (r"[A-Z][A-Za-z0-9_]*", Name.Class),
            (r"[a-z_][A-Za-z0-9_]*", Name),
            (r"\d+", Number),
            (r"==|!=|<=|>=|=|<|>|\+|-|\*|/", Operator),
            (r"[\[\](){}:,.]", Punctuation),
            (r"\s+", Text),
            (r".", Text),
        ]
    }


class ConsoleLexer(RegexLexer):
    name = "Console"
    tokens = {
        "root": [
            (r"\[PASS\]", Generic.Inserted),
            (r"\[FAIL\]", Generic.Error),
            (r"\s+", Text),
            (r"\S+", Text),
        ]
    }


def color_for(tok):
    t = tok
    while t is not Token:
        if t in (Generic.Inserted,):
            return C_PASS, "b"
        if t in (Generic.Error,):
            return C_FAIL, "b"
        if str(t).startswith("Token.Comment"):
            return C_COMMENT, "i"
        if t in (Keyword.Constant,):
            return C_CONST, "b"
        if str(t).startswith("Token.Keyword"):
            return C_KW, "b"
        if str(t).startswith("Token.Literal.String"):
            return C_STR, ""
        if str(t).startswith("Token.Literal.Number"):
            return C_CONST, ""
        if t in (Name.Tag,):
            return C_CLASS, "b"
        if t in (Name.Class,):
            return C_CLASS, ""
        if t in (Name.Attribute,):
            return C_ATTR, ""
        if str(t).startswith("Token.Operator") or str(t).startswith("Token.Punctuation"):
            return C_OP, ""
        if str(t).startswith("Token.Name"):
            return C_NAME, ""
        t = t.parent
    return C_TEXT, ""


def font_for(flags):
    if "b" in flags and "i" in flags:
        return f_bi
    if "b" in flags:
        return f_bold
    if "i" in flags:
        return f_ital
    return f_norm


def render(code, lexer, label, accent, outfile):
    code = code.rstrip("\n")
    lines = code.split("\n")
    ncols = max(len(l) for l in lines)
    body_w = int(PAD * 2 + ncols * CHAR_W)
    lbl_w = int(f_label.getlength(label)) + PAD * 2
    W = max(body_w, lbl_w, 520)
    H = HEADER_H + PAD + len(lines) * LINE_H + PAD

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1, 1, W - 2, H - 2], RADIUS, fill=(255, 255, 255, 255))
    d.rounded_rectangle([1, 1, W - 2, HEADER_H], RADIUS, fill=accent,
                        corners=(True, True, False, False))
    d.text((PAD, HEADER_H / 2), label, font=f_label, fill="#ffffff", anchor="lm")

    y = HEADER_H + PAD
    col = 0
    for tok, val in lexer.get_tokens(code):
        color, flags = color_for(tok)
        fnt = font_for(flags)
        for i, piece in enumerate(val.split("\n")):
            if i > 0:
                y += LINE_H
                col = 0
            if piece:
                d.text((PAD + col * CHAR_W, y), piece, font=fnt, fill=color)
                col += len(piece)
    d.rounded_rectangle([1, 1, W - 2, H - 2], RADIUS, outline="#e2e8f0", width=2)
    img.save(OUT + outfile)
    print("wrote", OUT + outfile, img.size)


BLUE, GREEN, INDIGO, AMBER = "#2563eb", "#059669", "#4338ca", "#d97706"

BLOCKS = [
    # ---- Part 2 ----
    ('''atomic action VerifyPatient:
    require not patient_verified
    require active_workflow == NO_WORKFLOW
    patient_verified = oneof [True, False]

always assertion PatientVerifiedBeforeWorkflow:
    return active_workflow == NO_WORKFLOW or patient_verified''',
     FizzLexer(), "FizzBee · clinic_orchestrator", BLUE, "code-fizz-verify.png"),

    ('''[PASS] book_appointment
[PASS] clinic_orchestrator
[PASS] manage_appointment
3/3 contract(s) passed model checking.''',
     ConsoleLexer(), "fizz — model check", GREEN, "code-check-pass.png"),

    ('''<offer id="relay_to_matching_offer" type="workflow" to="patient">
  <body>Relay a booking, cancel, or reschedule request to the subagent whose
    published offer matches.</body>
  <condition ref="patient_verified"/>
</offer>''',
     XmlLexer(), "XML · <promises>", INDIGO, "code-offer-relay.png"),

    ('''always assertion NoDoubleBook:
    return (not appointment_booked) or slot_available''',
     FizzLexer(), "FizzBee · book_appointment", BLUE, "code-fizz-nodoublebook.png"),

    ('''# NoDoubleBook — kept in code, no matter what the model says
slot = self._store.slots.get(slot_id)
if slot is None or slot.provider_id != provider_id:
    return refusal("unknown_slot", "slot_available", "That slot does not exist.")
if slot.status != "open":
    return refusal("slot_taken", "slot_available",
                   "That slot was taken since it was offered. Choose another.")
slot.status = "booked"''',
     PythonLexer(), "Python · services/schedule.py", AMBER, "code-py-enforce.png"),

    # ---- Part 3 ----
    ('''<offer id="never_double_book" type="invariant" to="patient clinic-compliance">
  <body>A slot is never booked twice; the commit is refused by the provider
    schedule if the slot was taken since it was offered (NoDoubleBook, kept in
    code regardless of the model).</body>
</offer>''',
     XmlLexer(), "XML · <promises>", INDIGO, "code-offer-neverdoublebook.png"),

    ('''<!-- provider_schedule publishes (+) -->
<offer id="open_slots" type="session-state" to="book_appointment manage_appointment clinic_orchestrator">
  <body>The currently open slots per provider. A slot is bookable only while
    it appears here.</body>
  <condition ref="slots_exist" assessed="self"/>
</offer>

<!-- book_appointment declares it relies on them (−) -->
<use id="open_slots" from="provider_schedule" quenches="slot_available">
  <body>The provider's currently open slots; a slot is only bookable while
    it appears here.</body>
</use>''',
     XmlLexer(), "XML · <promises>", INDIGO, "code-openslots-pair.png"),
]

if __name__ == "__main__":
    for code, lexer, label, accent, fn in BLOCKS:
        render(code, lexer, label, accent, fn)
