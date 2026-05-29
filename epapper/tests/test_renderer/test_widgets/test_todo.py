from epapper.ha_state import Entity, HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import LAYOUT
from epapper.renderer.widgets.todo import TodoWidget, TODO_NAKUP_SLOTS, TODO_UKOLY_SLOTS


def _todo_entity(eid, items):
    return Entity(eid, str(len(items)), {
        "items": [{"summary": s, "status": "needs_action"} for s in items]
    })


def _state(nakup_items, ukoly_items):
    s = HAState()
    s.set(_todo_entity("todo.nakup", nakup_items))
    s.set(_todo_entity("todo.ukoly", ukoly_items))
    return s


def test_todo_watches_both_entities():
    w = TodoWidget(nakup_entity="todo.nakup", ukoly_entity="todo.ukoly")
    assert set(w.watched_entities()) == {"todo.nakup", "todo.ukoly"}


def test_todo_default(assert_snapshot):
    nakup = ["Mléko 1,5 % (2×)", "Chleba kváskový", "Jogurt bílý 500 g",
             "Banány", "Máslo", "Káva", "Cibule", "Mrkev", "Brambory", "Vejce",
             "Olej", "Pomeranče"]
    ukoly = ["Zaplatit pojištění (do Po)", "Domluvit servis kola",
             "Vyzvednout balík", "Zavolat doktorovi", "Spravit kapající kohoutek"]
    c = Canvas.blank()
    w = TodoWidget(nakup_entity="todo.nakup", ukoly_entity="todo.ukoly")
    w.render(c, LAYOUT["todo"], _state(nakup, ukoly))
    assert_snapshot("widget_todo_default", c.image)


def test_todo_fits_within_slot_count():
    w = TodoWidget(nakup_entity="todo.nakup", ukoly_entity="todo.ukoly")
    assert TODO_NAKUP_SLOTS == 3
    assert TODO_UKOLY_SLOTS == 2


def test_todo_empty_nakup_expands_ukoly(assert_snapshot):
    ukoly = ["A", "B", "C", "D"]
    c = Canvas.blank()
    w = TodoWidget(nakup_entity="todo.nakup", ukoly_entity="todo.ukoly")
    w.render(c, LAYOUT["todo"], _state([], ukoly))
    assert_snapshot("widget_todo_empty_nakup", c.image)


def test_todo_empty_ukoly_expands_nakup(assert_snapshot):
    nakup = ["A", "B", "C", "D", "E"]
    c = Canvas.blank()
    w = TodoWidget(nakup_entity="todo.nakup", ukoly_entity="todo.ukoly")
    w.render(c, LAYOUT["todo"], _state(nakup, []))
    assert_snapshot("widget_todo_empty_ukoly", c.image)


def test_todo_both_empty(assert_snapshot):
    c = Canvas.blank()
    w = TodoWidget(nakup_entity="todo.nakup", ukoly_entity="todo.ukoly")
    w.render(c, LAYOUT["todo"], _state([], []))
    assert_snapshot("widget_todo_both_empty", c.image)
