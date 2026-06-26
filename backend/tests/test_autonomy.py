from app import autonomy


def test_remember_with_consent_still_proposes_other_intents():
    msg = "remember this and create a plan for Gebo desktop"
    proposals = autonomy.detect_action_intents(msg, consent=True)
    types = {p["action_type"] for p in proposals}
    assert "save_memory" not in types
    assert "create_plan" in types


def test_remember_without_consent_proposes_save_memory():
    msg = "remember this milestone"
    proposals = autonomy.detect_action_intents(msg, consent=False)
    types = {p["action_type"] for p in proposals}
    assert "save_memory" in types
