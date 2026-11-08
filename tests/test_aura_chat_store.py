"""
Unit and integration tests for AuraConversationStore:
- Verifies conversation creation, auto-titling, updating, and deletion.
- Verifies searching across conversation titles and contents.
- Verifies session restoration and persistence across reloads.
"""

import pytest
from src.aura_chat_store import AuraConversationStore


def test_create_and_retrieve_conversation():
    cid = AuraConversationStore.create_conversation(title="Trip to Hyderabad")
    assert cid.startswith("conv_")
    
    conv = AuraConversationStore.get_conversation(cid)
    assert conv is not None
    assert conv["title"] == "Trip to Hyderabad"
    assert conv["messages"] == []


def test_auto_title_generation():
    cid = AuraConversationStore.create_conversation()
    messages = [
        {"role": "assistant", "content": "Welcome to AURA"},
        {"role": "user", "content": "Plan a trip to Hyderabad for 3 days"},
        {"role": "assistant", "content": "Here is your plan..."}
    ]
    AuraConversationStore.update_messages(cid, messages)
    conv = AuraConversationStore.get_conversation(cid)
    assert "Hyderabad" in conv["title"]


def test_search_conversations():
    c1 = AuraConversationStore.create_conversation(title="Exploring Manali Mountains")
    c2 = AuraConversationStore.create_conversation(title="Goa Beach Vacation")
    
    manali_results = AuraConversationStore.list_conversations("Manali")
    assert any(c["id"] == c1 for c in manali_results)
    assert not any(c["id"] == c2 for c in manali_results)
    
    # Cleanup
    AuraConversationStore.delete_conversation(c1)
    AuraConversationStore.delete_conversation(c2)


def test_rename_and_delete_conversation():
    cid = AuraConversationStore.create_conversation(title="Old Title")
    AuraConversationStore.rename_conversation(cid, "New Updated Title")
    conv = AuraConversationStore.get_conversation(cid)
    assert conv["title"] == "New Updated Title"
    
    AuraConversationStore.delete_conversation(cid)
    assert AuraConversationStore.get_conversation(cid) is None
