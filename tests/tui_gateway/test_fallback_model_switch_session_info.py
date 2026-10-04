"""The TUI status bar must name the model actually answering after a mid-turn fallback.

``try_activate_fallback`` swaps ``agent.model``/``agent.provider`` in place, but nothing re-emitted
``session.info``, so the status bar kept showing the primary model while the fallback answered.
"""

from __future__ import annotations

from types import SimpleNamespace

from agent.chat_completion_helpers import emit_model_switched
from tui_gateway import server


def test_emit_model_switched_calls_event_callback_with_new_route():
    seen = []
    agent = SimpleNamespace(session_id="s1", event_callback=lambda et, ctx: seen.append((et, ctx)))

    emit_model_switched(agent, old_model="opus", old_provider="agy",
                        new_model="deepseek", new_provider="commandcode", kind="fallback")

    assert seen == [("agent:model_switched", {
        "session_id": "s1", "kind": "fallback", "old_model": "opus", "old_provider": "agy",
        "model": "deepseek", "provider": "commandcode"})]


def test_emit_model_switched_without_callback_or_with_failing_callback_is_silent():
    emit_model_switched(SimpleNamespace(), old_model="a", old_provider="b",
                        new_model="c", new_provider="d", kind="restore")

    def boom(*_a, **_k):
        raise RuntimeError("surface down")

    emit_model_switched(SimpleNamespace(event_callback=boom), old_model="a", old_provider="b",
                        new_model="c", new_provider="d", kind="fallback")


def test_tui_callbacks_reemit_session_info_on_model_switch(monkeypatch):
    agent = SimpleNamespace(model="deepseek", provider="commandcode")
    session = {"agent": agent}
    emitted = []
    monkeypatch.setitem(server._sessions, "sid-fb", session)
    monkeypatch.setattr(server, "_emit", lambda ev, sid, payload=None: emitted.append((ev, sid, payload)))
    monkeypatch.setattr(server, "_session_info",
                        lambda a, s: {"model": a.model, "provider": a.provider})

    cb = server._agent_cbs("sid-fb")["event_callback"]
    cb("agent:model_switched", {"model": "deepseek", "provider": "commandcode"})
    cb("session:compress", {})  # unrelated hook events stay off the status rail

    assert emitted == [("session.info", "sid-fb", {"model": "deepseek", "provider": "commandcode"})]
