from datetime import datetime, timedelta, timezone

from epapper.ha_state import Entity, HAState
from epapper.renderer.canvas import Canvas
from epapper.renderer.layout import LAYOUT
from epapper.renderer.widgets.calendar import CalendarWidget


def _now():
    return datetime(2026, 5, 17, 13, 30, tzinfo=timezone.utc)


def _ev(summary, start_hour, day_offset=0, duration_h=1, location=""):
    start = _now().replace(hour=start_hour, minute=0) + timedelta(days=day_offset)
    return {
        "summary": summary,
        "start": start.isoformat(),
        "end": (start + timedelta(hours=duration_h)).isoformat(),
        "location": location,
    }


def _state(events):
    s = HAState()
    s.set(Entity("calendar.family", "on", {"all_events": events}))
    return s


def test_calendar_watches_entity():
    w = CalendarWidget(calendar_entity="calendar.family", now=_now)
    assert w.watched_entities() == ["calendar.family"]


def test_calendar_renders_today_tomorrow_later(assert_snapshot):
    events = [
        _ev("Doktor Novák", 14, location="Praha 4"),
        _ev("Vyzvednout Klárku", 16, duration_h=0, location="ZŠ"),
        _ev("Tenis", 18, location="klub"),
        _ev("Snídaně u rodičů", 9, day_offset=1),
        _ev("Narozeniny Tom", 14, day_offset=1, location="Letná"),
        _ev("Schůze HOA", 10, day_offset=3),
    ]
    c = Canvas.blank()
    w = CalendarWidget(calendar_entity="calendar.family", now=_now)
    w.render(c, LAYOUT["calendar"], _state(events))
    assert_snapshot("widget_calendar_default", c.image)


def test_calendar_inverts_now_event(assert_snapshot):
    events = [_ev("Doktor Novák", 13, duration_h=2, location="Praha 4")]
    c = Canvas.blank()
    w = CalendarWidget(calendar_entity="calendar.family", now=_now)
    w.render(c, LAYOUT["calendar"], _state(events))
    assert_snapshot("widget_calendar_now_event", c.image)


def test_calendar_empty(assert_snapshot):
    c = Canvas.blank()
    w = CalendarWidget(calendar_entity="calendar.family", now=_now)
    w.render(c, LAYOUT["calendar"], _state([]))
    assert_snapshot("widget_calendar_empty", c.image)


def test_calendar_truncates_long_titles(assert_snapshot):
    events = [_ev("Velmi dlouhý název události který by mohl přetejct přes celou šířku", 14)]
    c = Canvas.blank()
    w = CalendarWidget(calendar_entity="calendar.family", now=_now)
    w.render(c, LAYOUT["calendar"], _state(events))
    assert_snapshot("widget_calendar_truncation", c.image)
