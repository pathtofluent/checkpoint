"""
PathToFluent Checkpoint - an Anki add-on.

Cards whose note type is listed in the config (default: "Task") skip the
"Show Answer" step and show a single "Complete" button instead of
Again / Hard / Good / Easy. Anki still schedules them for review as usual.

Also adds Tools > Add Task Cards... for creating many of them at once
(book chapters, numbered lessons and so on).
"""
import html

from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.utils import showWarning, tooltip

DEFAULTS = {
    "note_types": ["Task"],
    "button_label": "Complete",
    "skip_show_answer": True,
    "ease_first_time": 4,   # Easy: a brand-new card graduates at once instead of returning in 10 minutes
    "ease_review": 3,       # Good
}
TASK_FRONT = """<div class="task">{{Title}}</div>
{{#Details}}<div class="details">{{Details}}</div>{{/Details}}"""
TASK_BACK = "{{FrontSide}}"
TASK_CSS = """.card{font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:26px;
text-align:center;padding:40px 20px}
.task{font-weight:600;line-height:1.35}
.details{font-size:.7em;opacity:.75;margin-top:18px;line-height:1.5}"""


def cfg():
    conf = dict(DEFAULTS)
    conf.update(mw.addonManager.getConfig(__name__) or {})
    return conf


def is_task(card):
    try:
        return card.note_type()["name"] in cfg()["note_types"]
    except Exception:
        return False


def ease_for(card):
    conf = cfg()
    ease = conf["ease_review"] if card.type == 2 else conf["ease_first_time"]
    return ease if ease in (1, 2, 3, 4) else 3


# ── reviewer behaviour ──────────────────────────────────────────────────────
def on_buttons(buttons, reviewer, card):
    if is_task(card):
        return ((ease_for(card), cfg()["button_label"]),)
    return buttons


def on_answer(ease_tuple, reviewer, card):
    # Whatever key or button was used, a task card is answered one way only.
    if ease_tuple[0] and is_task(card):
        return (True, ease_for(card))
    return ease_tuple


def flip(card_id):
    r = mw.reviewer
    if mw.state == "review" and r.card and r.card.id == card_id and r.state == "question":
        r._showAnswer()


def on_question(card):
    if cfg()["skip_show_answer"] and is_task(card):
        QTimer.singleShot(0, lambda cid=card.id: flip(cid))


# ── the "Task" note type ────────────────────────────────────────────────────
def ensure_note_type():
    if "Task" not in cfg()["note_types"] or not mw.col:
        return
    mm = mw.col.models
    if mm.by_name("Task"):
        return
    m = mm.new("Task")
    mm.add_field(m, mm.new_field("Title"))
    mm.add_field(m, mm.new_field("Details"))
    t = mm.new_template("Task")
    t["qfmt"], t["afmt"] = TASK_FRONT, TASK_BACK
    mm.add_template(m, t)
    m["css"] = TASK_CSS
    mm.add(m)


# ── bulk add dialog ─────────────────────────────────────────────────────────
class AddTasks(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("PathToFluent Checkpoint - Add Task Cards")
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)
        form = QFormLayout()

        self.deck = QComboBox()
        self.deck.setEditable(True)
        self.deck.addItems(sorted(d.name for d in mw.col.decks.all_names_and_ids()))
        current = mw.col.decks.name(mw.col.decks.get_current_id())
        self.deck.setCurrentText(current)
        form.addRow("Deck (type a new name to create one)", self.deck)

        self.kind = QComboBox()
        self.kind.addItems(cfg()["note_types"])
        if self.kind.count() > 1:
            form.addRow("Note type", self.kind)

        self.tags = QLineEdit()
        form.addRow("Tags (optional)", self.tags)
        lay.addLayout(form)

        box = QGroupBox("Numbered series")
        row = QHBoxLayout(box)
        self.pattern = QLineEdit("Pimsleur Spanish 1 - Lesson {n}")
        self.first, self.last = QSpinBox(), QSpinBox()
        for s, v in ((self.first, 1), (self.last, 30)):
            s.setRange(0, 9999)
            s.setValue(v)
        fill = QPushButton("Add to list")
        fill.clicked.connect(self.fill)
        for w in (self.pattern, QLabel("from"), self.first, QLabel("to"), self.last, fill):
            row.addWidget(w)
        lay.addWidget(box)

        lay.addWidget(QLabel("One card per line. Add details after a | if you like:  Chapter 3 | pages 41-60"))
        self.text = QPlainTextEdit()
        self.text.setMinimumHeight(220)
        lay.addWidget(self.text)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Add cards")
        buttons.accepted.connect(self.add)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)

    def fill(self):
        pat = self.pattern.text().strip() or "Item {n}"
        if "{n}" not in pat:
            pat += " {n}"
        a, b = self.first.value(), self.last.value()
        lines = [pat.replace("{n}", str(n)) for n in range(a, b + 1)]
        self.text.appendPlainText("\n".join(lines))

    def add(self):
        lines = [l.strip() for l in self.text.toPlainText().splitlines() if l.strip()]
        deck_name = self.deck.currentText().strip()
        if not lines or not deck_name:
            showWarning("Enter at least one line and choose a deck.")
            return
        model = mw.col.models.by_name(self.kind.currentText())
        if not model:
            showWarning("The note type '%s' doesn't exist." % self.kind.currentText())
            return
        deck_id = mw.col.decks.id(deck_name)
        tags = self.tags.text().split()
        for line in lines:
            title, _, details = line.partition("|")
            note = mw.col.new_note(model)
            note.fields[0] = html.escape(title.strip())
            if len(note.fields) > 1:
                note.fields[1] = html.escape(details.strip())
            note.tags = list(tags)
            mw.col.add_note(note, deck_id)
        mw.reset()
        tooltip("Added %d cards to %s" % (len(lines), deck_name))
        self.accept()


def open_dialog():
    ensure_note_type()
    AddTasks(mw).exec()


gui_hooks.reviewer_will_init_answer_buttons.append(on_buttons)
gui_hooks.reviewer_will_answer_card.append(on_answer)
gui_hooks.reviewer_did_show_question.append(on_question)
gui_hooks.profile_did_open.append(ensure_note_type)

action = QAction("Add Task Cards...", mw)
action.triggered.connect(open_dialog)
mw.form.menuTools.addAction(action)
