from conversation.manager import ConversationManager

def test_year_clarification():
    cm = ConversationManager()
    step = cm.next_action("Revenue in Q2")
    assert step["need_clarification"]
    assert any("year" in q.lower() for q in step["questions"])
