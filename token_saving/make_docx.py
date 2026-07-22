from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ───────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Cm(21)
section.page_height = Cm(29.7)
section.left_margin   = Cm(3.2)
section.right_margin  = Cm(3.2)
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)

# ── Colours ─────────────────────────────────────────────────────────────
INK       = RGBColor(0x0F, 0x0F, 0x1E)
INK_SOFT  = RGBColor(0x2C, 0x2C, 0x42)
MID       = RGBColor(0x6B, 0x6B, 0x8A)
AMBER     = RGBColor(0xF5, 0x9E, 0x0B)
GREEN     = RGBColor(0x05, 0x96, 0x69)
RED       = RGBColor(0xDC, 0x26, 0x26)
RULE_BG   = RGBColor(0xF7, 0xF8, 0xFA)
TH_BG     = RGBColor(0xEC, 0xED, 0xF7)
HL_BG     = RGBColor(0xFF, 0xFB, 0xEB)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)

# ── Helpers ────────────────────────────────────────────────────────────────
def set_font(run, size=10, bold=False, color=None, italic=False, mono=False):
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color or INK_SOFT
    if mono:
        run.font.name = "Courier New"

def heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24 if level == 1 else 16)
    p.paragraph_format.space_after  = Pt(8)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(22 if level == 1 else 14)
    run.font.color.rgb = INK
    return p

def body(doc, text, space_after=8):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run(text)
    set_font(run, size=10, color=INK_SOFT)
    return p

def body_mixed(doc, parts, space_after=8):
    """parts: list of (text, bold, color, mono)"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    for text, bold, color, mono in parts:
        run = p.add_run(text)
        set_font(run, size=10, bold=bold, color=color or INK_SOFT, mono=mono)
    return p

def part_marker(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(28)
    p.paragraph_format.space_after  = Pt(12)
    run = p.add_run(text.upper())
    run.font.size = Pt(8)
    run.font.color.rgb = MID
    run.font.name = "Courier New"

def caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(14)
    run = p.add_run(text.upper())
    run.font.size = Pt(7.5)
    run.font.color.rgb = MID
    run.font.name = "Courier New"

def callout(doc, label, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(12)
    p.paragraph_format.left_indent  = Cm(0.4)
    r1 = p.add_run(label + " ")
    set_font(r1, size=9.5, bold=True, color=AMBER)
    r2 = p.add_run(text)
    set_font(r2, size=9.5, color=INK_SOFT)

def bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(4)
    if bold_prefix:
        rb = p.add_run(bold_prefix + " ")
        set_font(rb, size=10, bold=True, color=INK)
        rt = p.add_run(text)
        set_font(rt, size=10, color=INK_SOFT)
    else:
        run = p.add_run(text)
        set_font(run, size=10, color=INK_SOFT)

def shade_cell(cell, color_rgb):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    # RGBColor stores as a 3-tuple internally; convert via str representation
    hex_color = str(color_rgb).upper()  # already 6-char hex from docx
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_border(cell, border_color='E3E5EE'):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), border_color)
        tcBorders.append(border)
    tcPr.append(tcBorders)

def make_table(doc, headers, rows, highlight_rows=None, col_widths=None):
    """
    highlight_rows: set of row indices (0-based, not counting header) to tint amber
    Each cell in rows can be a string, or (text, color, bold)
    """
    highlight_rows = highlight_rows or set()
    n_cols = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = 'Table Grid'

    # header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        shade_cell(cell, TH_BG)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(h.upper())
        run.font.size = Pt(7.5)
        run.font.color.rgb = MID
        run.font.name = "Courier New"
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # data rows
    for ri, row_data in enumerate(rows):
        row = table.rows[ri + 1]
        bg = HL_BG if ri in highlight_rows else WHITE
        for ci, cell_data in enumerate(row_data):
            cell = row.cells[ci]
            shade_cell(cell, bg)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if isinstance(cell_data, tuple):
                text, color, bold = cell_data
            else:
                text, color, bold = cell_data, INK, False
            run = p.add_run(str(text))
            run.font.size = Pt(9)
            run.font.color.rgb = color
            run.bold = bold
            run.font.name = "Courier New"

    # col widths
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)

    doc.add_paragraph()  # spacing after table
    return table

def code_block(doc, lines):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(0)
        p.paragraph_format.left_indent  = Cm(0.5)
        run = p.add_run(line)
        run.font.name = "Courier New"
        run.font.size = Pt(9)
        run.font.color.rgb = INK_SOFT
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

def priority_item(doc, num, title, desc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    r1 = p.add_run(f"{num}  ")
    r1.font.name = "Courier New"
    r1.font.size = Pt(8)
    r1.font.color.rgb = AMBER
    r2 = p.add_run(title)
    r2.bold = True
    r2.font.size = Pt(10)
    r2.font.color.rgb = INK
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after  = Pt(4)
    p2.paragraph_format.left_indent  = Cm(0.85)
    run = p2.add_run(desc)
    set_font(run, size=9.5, color=MID)


# ════════════════════════════════════════════════════════════════════════════
#  CONTENT
# ════════════════════════════════════════════════════════════════════════════

# Eyebrow
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(4)
r = p.add_run("AI CODING AGENTS · COST & EFFICIENCY")
r.font.size = Pt(8)
r.font.color.rgb = AMBER
r.font.name = "Courier New"

# Title
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(6)
r = p.add_run("Stop Burning Money")
r.bold = True
r.font.size = Pt(32)
r.font.color.rgb = INK

# Deck
body(doc, "Token-saving practices for AI coding agents — from configuration basics to tools with actual benchmark data behind them.", space_after=20)

# ── Part 01 ────────────────────────────────────────────────────────────────
part_marker(doc, "Part 01 · Configuration")
heading(doc, "Most waste is a configuration problem.", level=1)

body(doc, "Token waste usually isn't a tooling deficit. The defaults are permissive — agents will retry indefinitely, load entire files when asked about one function, and narrate every step of their reasoning unprompted. Tightening those defaults costs nothing and tends to outperform any compression library.")

heading(doc, "The AGENT.md file: your first lever", level=2)

body(doc, "Most teams use AGENT.md (or CLAUDE.md, AGENTS.md) to document project context. It's also where you set behavioural constraints that run on every task.")

body_mixed(doc, [
    ("Iteration caps.  ", True, INK, False),
    ("The single highest-impact change is a hard limit on retry loops. An agent that has failed twice on the same approach is unlikely to succeed on the seventh attempt with the same strategy. Explicit rules prevent the compounding:", False, INK_SOFT, False),
])

code_block(doc, [
    "# In your AGENT.md / CLAUDE.md",
    "- Cap each debug loop at 2–3 attempts, then stop and report the blocker.",
    "- Do NOT retry the same approach more than once.",
    "  If something fails, form a new hypothesis first.",
    "- If an assumption cannot be verified with available tools, STOP and ask.",
])

body_mixed(doc, [
    ("Budget guardrails.  ", True, INK, False),
    ("Per-agent spend limits mean a runaway loop hits a ceiling rather than running until the end of the billing period. Tools like Airia have this built in; a token counter with a hard stop in the orchestration layer achieves the same result without the dependency.", False, INK_SOFT, False),
])

body_mixed(doc, [
    ("Error log preprocessing.  ", True, INK, False),
    ("A 4,000-line stack trace passed verbatim into context is mostly noise. Stripping it down before it reaches the agent — error type, failing command, last relevant stack frame — reduces token spend per call and tends to improve reasoning quality.", False, INK_SOFT, False),
])

for item in [
    "Error type only — not every repeated exception",
    "The failing command",
    "The last relevant stack frame",
]:
    bullet(doc, item)

heading(doc, "Skills: encode conventions once", level=2)
body(doc, "Re-explaining project structure and coding conventions at the start of every session is paid repetition. Most agent frameworks support reusable \"skills\" or instruction sets that load selectively — encoding conventions once and referencing them on demand rather than reconstructing them from scratch each time.")

# ── Part 02 ────────────────────────────────────────────────────────────────
part_marker(doc, "Part 02 · Tools (with receipts)")
heading(doc, "Tools that actually help.", level=1)

body(doc, "Three categories: being precise about what goes in, reducing what comes out, and being smarter about code retrieval. The data below comes from controlled A/B tests on the same codebase tasks.")

heading(doc, "Code search: Graphify and Semble", level=2)

body(doc, "Loading entire files to answer questions about one function is one of the most common sources of avoidable token spend. Smarter retrieval fixes this without requiring any changes to the model or the agent framework.")

body(doc, "Two rounds of testing compared Graphify and Semble against traditional grep+read across speed, token consumption, cost, and accuracy.")

body_mixed(doc, [("Round 1: Graphify vs. traditional search", True, INK, False)])

make_table(doc,
    headers=["Method", "Duration", "Tool calls", "Input tokens (est.)", "Output tokens (est.)", "Est. cost"],
    rows=[
        [("Graphify", INK, True), ("80.9s", GREEN, True), ("11", GREEN, False), ("~66k", GREEN, False), "~4,775", ("~$0.27", GREEN, False)],
        ["Traditional", "163.4s", "25", "~225k", "~5,300", "~$0.75"],
    ],
    highlight_rows={0},
)
caption(doc, "Round 1 — Graphify vs. traditional grep+read")

body(doc, "Graphify consumed roughly 3.4× fewer input tokens and ran at half the wall-clock time. The cost delta was ~$0.27 vs ~$0.75 per research session. The accuracy picture was more nuanced:")

make_table(doc,
    headers=["Question", "Graphify", "Traditional", "Winner"],
    rows=[
        ["Q1 — UserRejected handler", ("Missed user.unsubscribe() and exception guard", RED, False), "Found both + ticketOption.remove(user)", ("Traditional", GREEN, True)],
        ["Q2 — Booking flow", ("High-level only, missed AggregateHandlers / double-dispatch", RED, False), "Full chain incl. @Order(1)/@Order(2)", ("Traditional", GREEN, True)],
        ["Q3 — AxxesUserSynchronizer", "All 4 strategy implementations, correct", "Named 1, inferred rest; correct", ("Graphify (breadth)", GREEN, True)],
    ],
)

make_table(doc,
    headers=["Dimension", "Winner", "Delta"],
    rows=[
        ["Speed", ("Graphify", GREEN, True), "2× faster"],
        ["Input tokens", ("Graphify", GREEN, True), "~3.4× fewer"],
        ["Cost", ("Graphify", GREEN, True), "~2.8× cheaper"],
        ["Accuracy (method-level)", ("Traditional", GREEN, True), "Consistently deeper"],
        ["Accuracy (breadth / relationships)", ("Graphify", GREEN, True), "Better at enumerating cross-file structure"],
    ],
)
caption(doc, "Graphify wins on efficiency; traditional search wins on method-level behavioral detail")

body(doc, "Graphify's graph captures structural relationships well — \"what depends on what\", \"which classes implement this interface\". For questions that require reading what a method body actually does, traditional read still produces more complete answers.")

body_mixed(doc, [("Round 2: three-way comparison — Traditional, Graphify, Semble", True, INK, False)])

make_table(doc,
    headers=["Method", "Duration", "Tool calls", "Output chars", "Input tokens (est.)", "Output tokens (est.)", "Est. cost"],
    rows=[
        [("Traditional", INK, True), ("58.1s", GREEN, True), ("11", GREEN, False), "20,500", "~99k", "~5,125", "~$0.37"],
        ["Graphify", "62.1s", "17", "16,470", "~85k", "~4,117", ("~$0.32", GREEN, False)],
        ["Semble", "70.4s", "19", "28,000", ("~76k", GREEN, False), "~7,000", "~$0.33"],
    ],
    highlight_rows={2},
)
caption(doc, "Round 2 — Traditional, Graphify, Semble on the same task set")

body(doc, "Semble returns targeted snippets at the exact line rather than whole files, giving the lowest input token footprint while providing enough method-body context for accurate answers. It was the only tool to answer all behavioral questions fully correctly. Graphify was cheapest overall. Traditional search was fastest when the answer was in a known location.")

make_table(doc,
    headers=["Dimension", "Winner", "Notes"],
    rows=[
        ["Speed", ("Traditional", GREEN, True), "58s vs 62s vs 70s — close, all fast"],
        ["Input tokens", ("Semble", GREEN, True), "Snippet-level returns avoid large file reads"],
        ["Cost", ("Graphify", GREEN, True), "Lowest combined in+out cost"],
        ["Accuracy", ("Semble", GREEN, True), "Only tool to get Q1 and Q2 fully correct"],
        ["Breadth (cross-file)", ("Semble / Graphify", MID, False), "Both surface relationship structure well"],
    ],
)
caption(doc, "Overall verdict — each tool has a distinct profile")

callout(doc, "Recommended workflow:", "Semble for targeted behavioral questions → Graphify to map cross-file dependencies → traditional read only when you need the full file body.")

heading(doc, "Output compression: Caveman", level=2)

body(doc, "Caveman is a Claude Code plugin that forces the model into a compressed output mode — stripping responses to the functional minimum. The results are task-dependent, and the data is honest about that.")

body(doc, "On a code review task, standard Caveman mode added cost and significantly increased wall time. Caveman Ultra recovered the time advantage but didn't reduce spend:")

make_table(doc,
    headers=["Task", "Mode", "Cost", "Wall time"],
    rows=[
        ["Code review", "Regular", "$0.43", "20m 27s"],
        ["Code review", "Caveman", ("$0.46 ▲", RED, False), ("41m 46s ▲", RED, False)],
        ["Code review", "Caveman Ultra", "$0.44", ("3m 18s ↓", GREEN, False)],
        ["File summary", "Regular", "$0.26", "1m 20s"],
        ["File summary", ("Caveman Ultra", INK, True), ("$0.09  ↓ 64%", GREEN, True), ("39s", GREEN, False)],
    ],
    highlight_rows={4},
)

body(doc, "The pattern: Caveman performs poorly on tasks where the model's reasoning and code output is the value. On summarisation tasks — where verbosity is the problem — Caveman Ultra saves significantly. Savings of up to 75% have been reported in specific setups.")

heading(doc, "Output compression: Ponytail", level=2)

body(doc, "Ponytail constrains the scope of what gets built rather than compressing the output format. The claim is a 54% reduction in generated code without breaking functionality. The tests tell a more specific story.")

body(doc, "On concrete, well-scoped tasks, both modes produced nearly identical results — Ponytail wrote slightly more lines, and normal mode was more accurate on method names:")

make_table(doc,
    headers=["Method", "Task 1 lines", "Task 2 lines", "Task 3 lines", "Total lines", "New abstractions"],
    rows=[
        [("Normal", INK, True), "8", "5", "4", ("17", GREEN, True), "0"],
        ["Ponytail", "10", "4", "6", "20", "0"],
    ],
    highlight_rows={0},
)

make_table(doc,
    headers=["Dimension", "Winner", "Notes"],
    rows=[
        ["Line count", ("Normal", GREEN, True), "17 vs 20"],
        ["Correctness", ("Normal", GREEN, True), "Found the real method name; Ponytail guessed"],
        ["YAGNI reasoning", ("Ponytail", GREEN, True), "Explicitly surfaced what it chose not to do"],
        ["Abstraction discipline", ("Tie", MID, False), "Both: 0 new abstractions"],
    ],
)
caption(doc, "Small, concrete tasks — the methods converge")

body(doc, "Where the difference became dramatic was on a deliberately vague prompt: \"add a reporting system for sync stats.\"")

make_table(doc,
    headers=["Method", "Lines of code", "New abstractions", "Files created", "Files modified"],
    rows=[
        [("Ponytail", INK, True), ("3", GREEN, True), ("0", GREEN, False), ("0", GREEN, False), "1"],
        ["Normal", ("163", RED, True), ("4", RED, False), "4", "8"],
    ],
    highlight_rows={0},
)
caption(doc, '"Add a reporting system for sync stats" — scope interpretation diverges sharply')

body(doc, "\"Reporting system\" is a scope magnet. Ponytail's value is most visible on tasks where an unconstrained interpretation would pull in types, stores, endpoints, and interface changes. On small, already-scoped tasks, the modes are functionally equivalent — and normal mode tends to find real method names more reliably.")

# ── Part 03 ────────────────────────────────────────────────────────────────
part_marker(doc, "Part 03 · The meta-lesson")
heading(doc, "Loops are the biggest cost driver.", level=1)

body(doc, "The tools above all have genuine value in the right context. But the largest single lever — by a significant margin — is loop prevention.")

body(doc, "A debugging loop that runs fifteen iterations on a broken assumption doesn't only waste 15× the tokens on those calls. It fills the context window with failed attempts, which degrades subsequent reasoning, which produces more iterations. The failure compounds. No compression tool reverses that after the fact.")

body(doc, "What actually works, in rough order of impact:")

priority_item(doc, "01", "Hard iteration caps", "Two or three failed attempts at the same approach warrant a new hypothesis or a handoff to a human. This is the single largest source of runaway spend.")
priority_item(doc, "02", "Structured error preprocessing", "Summarise logs into structured facts before they enter the context window. Error type + immediate context only — the full dump adds noise without adding signal.")
priority_item(doc, "03", "Surgical code retrieval", "Semble or Graphify rather than whole-file reads. Retrieve what the task actually requires, not the entire module it lives in.")
priority_item(doc, "04", "Output compression on the right tasks", "Caveman Ultra for summarisation-heavy work where verbosity is the bottleneck. Ponytail for open-ended prompts where scope creep is the risk.")

doc.add_paragraph().paragraph_format.space_after = Pt(8)
body(doc, "The model itself is rarely the bottleneck. Token spend scales with how the agent is orchestrated — how often it retries, how much context it loads, how much it produces per call.")

# ── Conclusion ─────────────────────────────────────────────────────────────
heading(doc, "Your token budget is a resource, not a tax.", level=1)

body(doc, "Most of the waste described here is preventable with changes that range from free (configuration) to inexpensive (most of these tools). The difficulty isn't technical — it's that the fixes are operational rather than architectural, which makes them easier to defer.")
body(doc, "The biggest wins don't come from a library install. They come from iteration caps in AGENT.md, preprocessed error logs, and retrieval that's scoped to what the task actually needs. None of that is glamorous. It also doesn't show up in demos. It shows up on the invoice.")

p = doc.add_paragraph()
r = p.add_run("Start with the loop cap. Everything else is secondary.")
r.bold = True
r.font.size = Pt(10)
r.font.color.rgb = INK

# ── Sources ─────────────────────────────────────────────────────────────────
doc.add_paragraph().paragraph_format.space_before = Pt(24)
p = doc.add_paragraph()
r = p.add_run("SOURCES & FURTHER READING")
r.font.size = Pt(8)
r.font.color.rgb = MID
r.font.name = "Courier New"

sources = [
    ("Caveman benchmarks and tutorial", "https://www.qwe.edu.pl/tutorial/caveman-claude-reduce-tokens-75-percent/"),
    ("Caveman Mode — The New Stack", "https://thenewstack.io/caveman-mode-token-savings/"),
    ("Ponytail — Coding Nexus", "https://medium.com/coding-nexus/ponytail-the-ai-plugin-that-makes-claude-code-write-54-less-code-without-breaking-anything-df29842c8ff6"),
    ("Cutting LLM token costs with RTK — CodePointer", "https://codepointer.substack.com/p/cutting-llm-token-costs-with-rtk"),
    ("Caveman — GitHub", "https://github.com/JuliusBrussee/caveman"),
]

for label, url in sources:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(3)
    run = p.add_run(f"· {label} — {url}")
    run.font.size = Pt(8.5)
    run.font.color.rgb = MID


out = "/Users/nickvermeylen/projects/insights/token_savings/Stop Burning Money.docx"
doc.save(out)
print(f"Saved: {out}")
