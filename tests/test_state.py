from caseinsight.utils.state import ContactState


def test_mark_and_seen(tmp_path):
    state = ContactState(str(tmp_path / "s.json"))
    assert not state.seen("a@b.com")
    state.mark("a@b.com", "drafted")
    assert state.seen("a@b.com")
    assert state.reached("a@b.com", "drafted")
    assert not state.reached("a@b.com", "synced")


def test_case_insensitive(tmp_path):
    state = ContactState(str(tmp_path / "s.json"))
    state.mark("A@B.com", "drafted")
    assert state.seen("a@b.com")


def test_none_email_is_safe(tmp_path):
    state = ContactState(str(tmp_path / "s.json"))
    assert not state.seen(None)
    state.mark(None, "drafted")  # no-op, no crash


def test_persistence(tmp_path):
    path = tmp_path / "s.json"
    s1 = ContactState(str(path))
    s1.mark("x@y.com", "enrolled")
    s1.save()
    s2 = ContactState(str(path))
    assert s2.reached("x@y.com", "enrolled")
